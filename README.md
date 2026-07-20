# Mein_Agent — deutschsprachiger Kundensupport-Agent

Ein Support-Agent auf Basis des [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/python)
(Python, `claude-agent-sdk` 0.2.123). Er antwortet ausschließlich auf Deutsch und
greift für Fakten auf vier eigene Tools zu.

## Einrichtung

```powershell
copy .env.example .env      # danach ANTHROPIC_API_KEY eintragen
uv sync
uv run main.py
```

API-Key: <https://console.anthropic.com/> → Settings → API Keys.
Voraussetzungen: Python ≥ 3.10, Node.js ≥ 18 (das SDK startet intern die Claude-Code-Engine).

## Aufbau

| Datei | Inhalt |
| --- | --- |
| `main.py` | Interaktive Konsolen-Schleife, `ClaudeSDKClient` (Session bleibt über mehrere Fragen erhalten) |
| `support_agent/prompts.py` | System-Prompt: Rolle, Sprache, Eskalationsregeln |
| `support_agent/tools.py` | Custom-Tools + In-Process-MCP-Server |
| `support_agent/data.py` | Demo-Daten (Platzhalter für dein Backend) |

## Tools

| Tool | Zweck |
| --- | --- |
| `lookup_ticket` | Ticket per Nummer (`T-1001`, `T-1002`) |
| `lookup_order` | Bestellung per Nummer (`B-5521`, `B-5488`) |
| `search_faq` | Stichwortsuche in der Wissensdatenbank |
| `escalate_to_human` | Vorgang an einen Menschen übergeben |

Vollqualifiziert heißen sie `mcp__support__<name>` — unter diesem Namen stehen sie
in `allowed_tools` und laufen dadurch ohne Rückfrage.

## Beispiel-Dialog

```
Sie: Wo bleibt meine Bestellung B-5521?
Mia: Ihre Bestellung wurde am 08.07.2026 mit DHL zugestellt …

Sie: Der Reißverschluss ist kaputt, ich will mit einem Menschen sprechen.
Mia: Ich habe den Vorgang ESK-1234 mit hoher Priorität angelegt …
```

## Konfiguration anpassen

Alles Wesentliche steckt in `build_options()` in `main.py`:

- **`system_prompt`** — Verhalten und Tonalität; die erste Stellschraube.
- **`tools=[]`** — entfernt alle eingebauten Tools (Bash, Read, Write, WebFetch).
  Ein Support-Agent braucht keinen Datei- oder Shell-Zugriff. Für einen Coding-Agenten
  hier z. B. `["Read", "Grep"]` setzen.
- **`permission_mode="dontAsk"`** — alles, was nicht in `allowed_tools` steht, wird
  abgelehnt statt nachgefragt. Alternativen: `default`, `acceptEdits`, `plan`, `auto`.
  Für feingranulare Regeln stattdessen `can_use_tool` mit eigenem Callback nutzen.
- **`max_turns`** — Obergrenze pro Anfrage; schützt vor Schleifen.
- **`model`** — derzeit `claude-sonnet-5`.

## Eigenes Backend anbinden

Die Handler in `support_agent/tools.py` lesen aktuell aus `data.py`. Ersetze den
Zugriff durch deine API- oder DB-Aufrufe (die Handler sind `async`, `httpx` liegt
bereits als Transitiv-Abhängigkeit vor). Signaturen und Schemata bleiben gleich.

Fehler meldest du als Ergebnis mit `"is_error": True` zurück, statt eine Exception
zu werfen — dann kann Claude reagieren (nachfragen, eskalieren).

## Das `.claude/`-Verzeichnis

Diese Dateien richten sich an **Claude Code beim Weiterentwickeln** des Projekts.
`setting_sources=["project"]` in `build_options()` sorgt dafür, dass der Agent zur
Laufzeit zusätzlich die Regeln aus `.claude/settings.json` übernimmt:

| Pfad | Zweck |
| --- | --- |
| `.claude/settings.json` | Erlaubt `uv`-Befehle ohne Rückfrage, sperrt das Lesen von `.env` |
| `.claude/agents/tool-autor.md` | Subagent, der neue Custom-Tools nach den Projektkonventionen anlegt |
| `.claude/commands/dialog-test.md` | `/dialog-test` — spielt Testdialoge durch und bewertet die Antworten |
| `.claude/commands/prompt-schaerfen.md` | `/prompt-schaerfen <Fehlverhalten>` — überarbeitet den System-Prompt gezielt |

> **Hintergrund:** Ohne `setting_sources` ignoriert das SDK sämtliche
> Datei-Einstellungen — das ist Absicht, damit sich das Verhalten eines Agenten nicht
> ändert, nur weil auf einem Rechner andere lokale Einstellungen liegen. Wir laden
> bewusst nur `"project"` (versioniert im Repo), nicht `"user"` oder `"local"`.
>
> **Subagents zur Laufzeit:** Der `tool-autor` steht nur Claude Code zur Verfügung,
> nicht dem Support-Agenten. Claude ruft Subagents über das `Agent`-Tool auf — das ist
> hier durch `tools=[]` aus dem Kontext entfernt und stünde unter `permission_mode="dontAsk"`
> ohnehin nicht in `allowed_tools`. Das ist Absicht: Ein Support-Agent soll keine
> Subagents mit Datei- und Shell-Zugriff starten können. Soll er es doch, brauchst du
> `"Agent"` in `allowed_tools` **und** die passenden Tools in `tools` — oder du
> definierst Subagents direkt im Code über die Option `agents={...}`.

## Weiterführend

- Python-SDK-Referenz: <https://code.claude.com/docs/en/agent-sdk/python>
- Custom Tools: <https://code.claude.com/docs/en/agent-sdk/custom-tools>
- Permissions: <https://code.claude.com/docs/en/agent-sdk/permissions>
- Subagents: <https://code.claude.com/docs/en/agent-sdk/subagents>
