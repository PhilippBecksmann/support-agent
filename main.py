"""Interaktiver Kundensupport-Agent (Claude Agent SDK).

Start:  uv run main.py
Beenden: "exit", "quit" oder Strg+C
"""

import asyncio
import os
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ClaudeSDKError,
    CLINotFoundError,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
from dotenv import load_dotenv

from support_agent import ALLOWED_TOOLS, SYSTEM_PROMPT, support_server

# Zeigt an, welche Tools der Agent gerade aufruft. Für den Produktivbetrieb
# auf False setzen – Endkundschaft interessiert das nicht.
DEBUG_TOOLS = True


def build_options() -> ClaudeAgentOptions:
    """Konfiguration des Agenten an einer Stelle gebündelt."""
    return ClaudeAgentOptions(
        # Rolle, Sprache und Regeln – siehe support_agent/prompts.py
        system_prompt=SYSTEM_PROMPT,
        # Unsere eigenen Tools als In-Process-MCP-Server registrieren.
        mcp_servers={"support": support_server},
        # Vorab freigegeben: laufen ohne Rückfrage.
        allowed_tools=ALLOWED_TOOLS,
        # Leere Liste = keine eingebauten Tools (Bash, Read, Write, WebFetch ...).
        # Ein Support-Agent braucht keinen Dateisystem- oder Shell-Zugriff.
        tools=[],
        # Alles, was nicht vorab erlaubt ist, wird abgelehnt statt nachgefragt.
        permission_mode="dontAsk",
        # Lädt .claude/ aus dem Projektverzeichnis (Subagents, settings.json).
        # Ohne diese Zeile ignoriert das SDK alle Datei-Einstellungen.
        # Bewusst nur "project" – "user" und "local" würden das Verhalten des
        # Agenten von den persönlichen Einstellungen der ausführenden Person
        # abhängig machen.
        setting_sources=["project"],
        # Schutz gegen Endlosschleifen und Kostenausreißer pro Anfrage.
        max_turns=12,
        model="claude-sonnet-5",
    )


# Übersetzt die Fehlercodes aus AssistantMessage.error in verwertbare Hinweise.
FEHLERTEXTE: dict[str, str] = {
    "authentication_failed": "Anmeldung fehlgeschlagen – ANTHROPIC_API_KEY in .env prüfen.",
    "billing_error": "Abrechnungsproblem – Guthaben unter console.anthropic.com prüfen.",
    "rate_limit": "Rate-Limit erreicht – bitte kurz warten und erneut versuchen.",
    "invalid_request": "Die Anfrage wurde abgelehnt (ungültiges Format).",
    "server_error": "Serverfehler bei Anthropic – ein erneuter Versuch hilft meist.",
    "unknown": "Unbekannter Fehler bei der Anfrage.",
}


def render(message: object) -> None:
    """Eine SDK-Nachricht auf der Konsole ausgeben."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text, end="", flush=True)
            elif isinstance(block, ToolUseBlock) and DEBUG_TOOLS:
                print(f"\n  [Tool] {block.name} {block.input}", flush=True)
        # Wird gesetzt, wenn die Antwort abbricht – z. B. Rate-Limit oder Auth.
        if message.error:
            hinweis = FEHLERTEXTE.get(message.error, message.error)
            print(f"\n  [Fehler] {hinweis}")
    elif isinstance(message, ResultMessage):
        print()
        if message.subtype != "success":
            print(f"  [Hinweis] Durchlauf endete mit Status: {message.subtype}")
        # Details, die das SDK zusätzlich zum Status mitliefert.
        if message.api_error_status:
            print(f"  [Hinweis] HTTP-Status der API: {message.api_error_status}")
        for fehler in message.errors or []:
            print(f"  [Hinweis] {fehler}")
        if message.permission_denials:
            # Tritt auf, wenn Claude ein Tool aufruft, das nicht in
            # ALLOWED_TOOLS steht – unter permission_mode="dontAsk" wird das
            # ohne Rückfrage abgelehnt.
            # Einträge kommen je nach SDK-Version als dict oder als Objekt.
            namen = {
                (d.get("tool_name") if isinstance(d, dict) else getattr(d, "tool_name", None))
                or str(d)
                for d in message.permission_denials
            }
            print(f"  [Hinweis] Abgelehnte Tool-Aufrufe: {', '.join(sorted(namen))}")


async def chat_loop(client: ClaudeSDKClient) -> None:
    """Liest Eingaben und gibt die Antworten des Agenten aus."""
    while True:
        # input() blockiert – in einen Thread auslagern, damit die Event-Loop frei bleibt.
        try:
            frage = (await asyncio.to_thread(input, "\nSie: ")).strip()
        except EOFError:
            return

        if not frage:
            continue
        if frage.lower() in {"exit", "quit", "ende", "tschüss"}:
            print("\nAuf Wiedersehen!")
            return

        print("\nMia: ", end="", flush=True)
        try:
            # query() sendet die Nachricht, receive_response() liefert alle
            # Nachrichten bis zum Abschluss dieser Runde. Der Gesprächsverlauf
            # bleibt über den gesamten Client hinweg erhalten.
            await client.query(frage)
            async for message in client.receive_response():
                render(message)
        except Exception as fehler:  # z. B. Netzwerk- oder Auth-Fehler
            print(f"\n  [Fehler] Anfrage fehlgeschlagen: {fehler}")


async def main() -> None:
    # Windows-Konsolen laufen sonst oft in cp1252 – Umlaute würden abstürzen.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY ist nicht gesetzt.\n"
            "  1. .env.example nach .env kopieren\n"
            "  2. Key von https://console.anthropic.com/ eintragen",
            file=sys.stderr,
        )
        sys.exit(1)

    # ClaudeSDKClient hält die Session offen, damit Rückfragen im Kontext bleiben.
    # Für einmalige, kontextlose Aufgaben stattdessen query() verwenden.
    try:
        async with ClaudeSDKClient(options=build_options()) as client:
            # Begrüßung erst, wenn die Verbindung wirklich steht.
            print("NordWaren Kundensupport – Mia ist bereit. ('exit' zum Beenden)")
            print(
                "Beispiele: 'Wo bleibt meine Bestellung B-5521?' | "
                "'Wie lange kann ich zurückgeben?'"
            )
            await chat_loop(client)
    except CLINotFoundError:
        # Das SDK startet intern die Claude-Code-Engine – die braucht Node.js.
        print(
            "\nDie Claude-Code-Engine wurde nicht gefunden.\n"
            "  Node.js 18 oder neuer installieren: https://nodejs.org/\n"
            "  Danach 'uv sync' erneut ausführen.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ClaudeSDKError as fehler:
        # Deckt CLIConnectionError, ProcessError und CLIJSONDecodeError ab.
        print(
            f"\nVerbindung zum Agenten fehlgeschlagen: {fehler}\n"
            "  API-Key in .env prüfen und Internetverbindung sicherstellen.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
