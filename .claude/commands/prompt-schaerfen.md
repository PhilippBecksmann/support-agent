---
description: Überarbeitet den System-Prompt gezielt für ein beobachtetes Fehlverhalten
argument-hint: <beobachtetes Fehlverhalten>
allowed-tools: Read, Edit
---

Beobachtetes Fehlverhalten: $ARGUMENTS

Überarbeite `support_agent/prompts.py` so, dass genau dieses Verhalten abgestellt wird.

Regeln:

- Zuerst prüfen, ob der bestehende Prompt die Regel schon enthält. Wenn ja, liegt
  das Problem woanders (Tool-Beschreibung, Datenlage, Modell) — sag das, statt den
  Prompt aufzublähen.
- Bestehende Abschnitte schärfen statt neue anhängen. Der Prompt bleibt kurz;
  jede zusätzliche Zeile kostet Kontext in **jeder** Anfrage.
- Regeln positiv und konkret formulieren („Nenne immer die Sendungsnummer") statt
  vage negativ („Sei nicht ungenau").
- Deutsch, Struktur mit Markdown-Überschriften wie gehabt.

Zeige mir vorher die geplante Änderung als Diff und begründe sie in einem Satz.
