"""Custom-Tools für den Support-Agenten.

Jedes Tool wird mit `@tool(name, beschreibung, schema)` definiert. Die
Beschreibung ist das, woran Claude erkennt, wann ein Tool passt – sie sollte
präzise sein. Alle Tools laufen im selben Prozess wie diese Anwendung
(In-Process-MCP-Server), es wird also kein Subprozess gestartet.
"""

import json
import random
from typing import Any

from claude_agent_sdk import ToolAnnotations, create_sdk_mcp_server, tool

from .data import BESTELLUNGEN, FAQ, TICKETS

# Servername – taucht im vollqualifizierten Tool-Namen auf: mcp__support__<tool>
SERVER_NAME = "support"

# Häufige Füllwörter. Ohne diesen Filter erzeugt schon ein "für" oder "wie" einen
# Treffer in fast jedem FAQ-Eintrag – der Agent bekäme dann zu einer völlig
# fremden Frage eine scheinbar passende Antwort geliefert.
STOPPWOERTER = frozenset(
    """
    aber auch auf aus bei bin bis das dass dem den denn der des die diese diesem
    diesen dieser dieses doch dort durch ein eine einem einen einer eines etwas
    euer eure für gibt hab habe haben habt hat ich ihm ihn ihnen ihr ihre immer
    ins ist kann kein keine können mal man mein meine mich mir mit muss nach
    nicht noch nur oder schon sein seine sich sie sind soll über und uns unser
    vom von war waren was wenn wer werden wie wir wird wollen zum zur
    """.split()
)


def _text(payload: Any) -> dict[str, Any]:
    """Ergebnis als Text-Block verpacken (das erwartet das MCP-Protokoll)."""
    if not isinstance(payload, str):
        payload = json.dumps(payload, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": payload}]}


def _error(nachricht: str) -> dict[str, Any]:
    """Fehler als Tool-Ergebnis melden, statt eine Exception zu werfen.

    `is_error` signalisiert Claude einen fehlgeschlagenen Aufruf – der Agent
    kann dann reagieren (nachfragen, eskalieren), statt die Meldung als
    normales Ergebnis zu behandeln.
    """
    return {"content": [{"type": "text", "text": nachricht}], "is_error": True}


@tool(
    "lookup_ticket",
    "Ruft ein Support-Ticket anhand seiner Ticket-Nummer ab (Format: T-1234). "
    "Liefert Status, Betreff, zugehörige Bestellnummer und die letzte interne Notiz.",
    {"ticket_id": str},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def lookup_ticket(args: dict[str, Any]) -> dict[str, Any]:
    ticket_id = str(args["ticket_id"]).strip().upper()
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        return _error(
            f"Kein Ticket mit der Nummer {ticket_id} gefunden. "
            "Bitte die Nummer prüfen (Format T-1234)."
        )
    return _text({"ticket_id": ticket_id, **ticket})


@tool(
    "lookup_order",
    "Ruft eine Bestellung anhand der Bestellnummer ab (Format: B-1234). Liefert "
    "Lieferstatus, Sendungsnummer, Positionen und Gesamtsumme.",
    {"order_id": str},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def lookup_order(args: dict[str, Any]) -> dict[str, Any]:
    order_id = str(args["order_id"]).strip().upper()
    bestellung = BESTELLUNGEN.get(order_id)
    if bestellung is None:
        return _error(
            f"Keine Bestellung mit der Nummer {order_id} gefunden. "
            "Bitte die Nummer prüfen (Format B-1234)."
        )
    return _text({"bestellnummer": order_id, **bestellung})


@tool(
    "search_faq",
    "Durchsucht die Wissensdatenbank nach Antworten zu allgemeinen Fragen: "
    "Öffnungszeiten und Erreichbarkeit, Ladengeschäft, Zahlungsarten, Rückgabe, "
    "Versand, Erstattung, Garantie, Größen, Kundenkonto. Erwartet Stichwörter, "
    "keine ganzen Sätze. Optional 'limit' (Standard 3) für die Trefferzahl.",
    {"query": str},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def search_faq(args: dict[str, Any]) -> dict[str, Any]:
    # 'limit' steht bewusst nicht im Schema: Im Python-Dict-Schema ist jedes Feld
    # Pflicht. Optionale Parameter werden in der Beschreibung erwähnt und hier
    # mit .get() gelesen.
    limit = int(args.get("limit", 3))
    begriffe = [
        wort
        for wort in str(args["query"]).lower().strip(".,!?").split()
        if len(wort) > 2 and wort not in STOPPWOERTER
    ]

    def score(eintrag: dict[str, str]) -> int:
        heuhaufen = " ".join(eintrag.values()).lower()
        return sum(1 for begriff in begriffe if begriff in heuhaufen)

    treffer = sorted(((score(e), e) for e in FAQ), key=lambda p: p[0], reverse=True)
    relevant = [eintrag for punkte, eintrag in treffer if punkte > 0][:limit]

    if not relevant:
        return _text(
            "Keine passenden FAQ-Einträge gefunden. "
            "Andere Stichwörter versuchen oder an einen Menschen eskalieren."
        )
    return _text(relevant)


@tool(
    "escalate_to_human",
    "Übergibt den Vorgang an einen menschlichen Support-Mitarbeiter und legt "
    "einen Eskalationsvorgang an. Nur nutzen, wenn die Kundschaft ausdrücklich "
    "darum bittet oder der Fall nicht selbst lösbar ist.",
    {
        # Volles JSON-Schema, weil das Dict-Kurzschema keine Enums unterstützt.
        "type": "object",
        "properties": {
            "zusammenfassung": {
                "type": "string",
                "description": "Kurze Zusammenfassung des Anliegens für die Kollegin oder den Kollegen",
            },
            "prioritaet": {
                "type": "string",
                "enum": ["niedrig", "normal", "hoch"],
                "description": "Dringlichkeit des Vorgangs",
            },
            "kontakt": {
                "type": "string",
                "description": "E-Mail-Adresse oder Ticket-Nummer der Kundin bzw. des Kunden",
            },
        },
        "required": ["zusammenfassung", "prioritaet", "kontakt"],
    },
)
async def escalate_to_human(args: dict[str, Any]) -> dict[str, Any]:
    # Hier würdest du echt ein Ticket in Zendesk/Jira/... anlegen.
    vorgang = f"ESK-{random.randint(1000, 9999)}"
    reaktionszeit = {"hoch": "2 Stunden", "normal": "1 Werktag", "niedrig": "3 Werktage"}
    prioritaet = args["prioritaet"]
    return _text(
        {
            "vorgangsnummer": vorgang,
            "prioritaet": prioritaet,
            "kontakt": args["kontakt"],
            "zusammenfassung": args["zusammenfassung"],
            "zugesagte_reaktionszeit": reaktionszeit[prioritaet],
        }
    )


# Alle Tools zu einem In-Process-MCP-Server bündeln.
support_server = create_sdk_mcp_server(
    name=SERVER_NAME,
    version="1.0.0",
    tools=[lookup_ticket, lookup_order, search_faq, escalate_to_human],
)

# Vollqualifizierte Namen: mcp__{server}__{tool}. In `allowed_tools` gelistete
# Tools laufen ohne Rückfrage.
ALLOWED_TOOLS = [
    f"mcp__{SERVER_NAME}__lookup_ticket",
    f"mcp__{SERVER_NAME}__lookup_order",
    f"mcp__{SERVER_NAME}__search_faq",
    f"mcp__{SERVER_NAME}__escalate_to_human",
]
