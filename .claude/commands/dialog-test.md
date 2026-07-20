---
description: Spielt Testdialoge gegen den Support-Agenten und bewertet die Antworten
argument-hint: [optionale zusätzliche Testfrage]
allowed-tools: Read, Write, Bash(uv run:*)
---

Teste den Support-Agenten aus `main.py` mit einem Skript, das `query()` statt der
interaktiven Schleife verwendet (Skript in ein temporäres Verzeichnis schreiben,
nicht ins Projekt).

Standard-Testfälle:

1. „Wo bleibt meine Bestellung B-5521?" — soll `lookup_order` aufrufen
2. „Wie lange kann ich zurückgeben?" — soll `search_faq` aufrufen
3. „Was ist mit Ticket T-9999?" — Tool meldet `is_error`; der Agent soll das
   sauber auffangen und nach der korrekten Nummer fragen, nicht halluzinieren
4. „Ich will sofort einen Menschen sprechen!" — soll `escalate_to_human` mit
   passender Priorität aufrufen und die Vorgangsnummer nennen

Zusätzliche Testfrage (optional): $1

Bewerte je Fall:
- Wurde das **richtige Tool** aufgerufen (oder eines zu viel / zu wenig)?
- Ist die Antwort **durchgehend deutsch** und in der Sie-Form?
- Werden rohe JSON-Ausgaben oder interne Feldnamen durchgereicht? (Darf nicht sein.)
- Werden Zusagen gemacht, die kein Tool-Ergebnis deckt? (Darf nicht sein.)

Fasse am Ende in einer kurzen Tabelle zusammen, was bestanden hat und was nicht.
Nenne bei Fehlern die konkrete Stelle in `prompts.py` oder `tools.py`, die dafür
verantwortlich ist. Ändere nichts, ohne vorher zu fragen.
