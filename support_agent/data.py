"""Demo-Datenbestand.

Platzhalter für dein echtes Backend. In der Praxis ersetzt du die Zugriffe in
`tools.py` durch API-Calls oder Datenbank-Queries – die Tool-Signaturen bleiben
dabei gleich.
"""

from typing import Any

TICKETS: dict[str, dict[str, Any]] = {
    "T-1001": {
        "status": "in Bearbeitung",
        "betreff": "Zelt mit defektem Reißverschluss geliefert",
        "kunde": "anna.berg@example.com",
        "bestellnummer": "B-5521",
        "erstellt_am": "2026-07-14",
        "letzte_notiz": "Ersatzteil beim Hersteller angefragt, Rückmeldung offen.",
    },
    "T-1002": {
        "status": "wartet auf Kundenrückmeldung",
        "betreff": "Rücksendung Wanderschuhe Größe 43",
        "kunde": "max.lehmann@example.com",
        "bestellnummer": "B-5488",
        "erstellt_am": "2026-07-11",
        "letzte_notiz": "Retourenlabel per E-Mail verschickt.",
    },
}

BESTELLUNGEN: dict[str, dict[str, Any]] = {
    "B-5521": {
        "status": "geliefert",
        "besteldatum": "2026-07-02",
        "lieferdatum": "2026-07-08",
        "versanddienst": "DHL",
        "sendungsnummer": "00340434161234567890",
        "positionen": [{"artikel": "Trekkingzelt Fjell 2", "menge": 1, "preis_eur": 289.00}],
        "summe_eur": 289.00,
    },
    "B-5488": {
        "status": "Retoure angemeldet",
        "besteldatum": "2026-06-28",
        "lieferdatum": "2026-07-01",
        "versanddienst": "DHL",
        "sendungsnummer": "00340434161234512345",
        "positionen": [{"artikel": "Wanderschuh Tind GTX 43", "menge": 1, "preis_eur": 179.95}],
        "summe_eur": 179.95,
    },
}

# Sehr einfache FAQ-Basis. Für echte Volltext- oder Vektorsuche hier ansetzen.
#
# Das Feld "stichworte" fängt Formulierungen ab, die in Frage und Antwort nicht
# wörtlich vorkommen ("Rückgaberecht", "Widerruf" statt "Rücksendung"). Die Suche
# in tools.py durchsucht alle Felder eines Eintrags, deshalb wirkt es ohne
# weiteren Code. Bei echten Daten übernimmt das eine Volltext- oder Vektorsuche.
FAQ: list[dict[str, str]] = [
    {
        "thema": "Erreichbarkeit",
        "frage": "Wann ist der Kundenservice erreichbar?",
        "antwort": (
            "Montag bis Freitag von 8 bis 18 Uhr, samstags von 9 bis 14 Uhr. "
            "Telefon 0800 1234567 (kostenfrei), E-Mail service@nordwaren.example. "
            "An gesetzlichen Feiertagen ist der Service geschlossen. E-Mails werden "
            "innerhalb eines Werktags beantwortet."
        ),
        "stichworte": (
            "Öffnungszeiten Servicezeiten Sprechzeiten Hotline Telefonnummer anrufen "
            "erreichen Kontakt Support Wochenende Feiertag geschlossen offen"
        ),
    },
    {
        "thema": "Ladengeschäft",
        "frage": "Gibt es ein Ladengeschäft vor Ort?",
        "antwort": (
            "Ja, unser Store in Hamburg, Speicherstraße 12, hat montags bis samstags "
            "von 10 bis 19 Uhr geöffnet. Online bestellte Artikel können dort "
            "kostenfrei abgeholt und zurückgegeben werden."
        ),
        "stichworte": (
            "Filiale Laden Geschäft Store Öffnungszeiten Adresse Standort Hamburg "
            "Abholung abholen vorbeikommen offen"
        ),
    },
    {
        "thema": "Zahlung",
        "frage": "Welche Zahlungsarten werden akzeptiert?",
        "antwort": (
            "Kreditkarte (Visa, Mastercard), PayPal, Lastschrift, Sofortüberweisung "
            "und Kauf auf Rechnung ab dem zweiten Einkauf. Ratenzahlung ist ab einem "
            "Bestellwert von 200 EUR möglich."
        ),
        "stichworte": (
            "bezahlen Zahlungsmittel Kreditkarte PayPal Rechnung Lastschrift "
            "Ratenzahlung Vorkasse Überweisung"
        ),
    },
    {
        "thema": "Rückgabe",
        "frage": "Wie lange habe ich Zeit für eine Rücksendung?",
        "antwort": (
            "30 Tage ab Erhalt der Ware. Die Artikel müssen ungetragen und in der "
            "Originalverpackung sein. Das Retourenlabel gibt es kostenlos im Kundenkonto."
        ),
        "stichworte": (
            "Rückgaberecht Retoure zurückschicken zurücksenden Widerruf Widerrufsrecht "
            "umtauschen Umtausch Frist"
        ),
    },
    {
        "thema": "Versand",
        "frage": "Wie lange dauert die Lieferung?",
        "antwort": (
            "Innerhalb Deutschlands 2 bis 4 Werktage, in die EU 4 bis 7 Werktage. "
            "Ab 50 EUR Bestellwert ist der Versand kostenfrei."
        ),
        "stichworte": (
            "Lieferzeit Lieferdauer Versandkosten verschicken Paket DHL Ausland "
            "Österreich Schweiz Zustellung"
        ),
    },
    {
        "thema": "Erstattung",
        "frage": "Wann bekomme ich mein Geld zurück?",
        "antwort": (
            "Nach Eingang der Retoure im Lager dauert die Prüfung bis zu 3 Werktage. "
            "Die Erstattung erfolgt auf das ursprüngliche Zahlungsmittel und ist "
            "je nach Bank nach 2 bis 5 weiteren Werktagen sichtbar."
        ),
        "stichworte": (
            "Rückerstattung Geld zurück Gutschrift überwiesen Auszahlung Konto "
            "wie lange dauert"
        ),
    },
    {
        "thema": "Garantie",
        "frage": "Welche Garantie gibt es auf Ausrüstung?",
        "antwort": (
            "Zwei Jahre gesetzliche Gewährleistung. Auf Zelte und Rucksäcke gewährt "
            "der Hersteller zusätzlich eine freiwillige Garantie von fünf Jahren auf "
            "Material- und Verarbeitungsfehler."
        ),
        "stichworte": (
            "Gewährleistung Reklamation defekt kaputt Mangel reparieren Reparatur "
            "Hersteller Umtausch"
        ),
    },
    {
        "thema": "Größen",
        "frage": "Wie finde ich die richtige Größe?",
        "antwort": (
            "Zu jedem Artikel gibt es eine Größentabelle auf der Produktseite. "
            "Wanderschuhe fallen erfahrungsgemäß eine halbe Nummer kleiner aus – "
            "im Zweifel die nächstgrößere Nummer wählen. Ein Größentausch ist "
            "innerhalb der 30-tägigen Rückgabefrist kostenfrei."
        ),
        "stichworte": (
            "Größentabelle Größenberatung passt nicht zu klein zu groß Schuhgröße "
            "Konfektionsgröße tauschen"
        ),
    },
    {
        "thema": "Kundenkonto",
        "frage": "Wie ändere ich meine Adresse oder mein Passwort?",
        "antwort": (
            "Beides im Kundenkonto unter 'Meine Daten'. Eine Lieferadresse lässt sich "
            "nur ändern, solange die Bestellung noch nicht versandt wurde – danach "
            "hilft eine Nachfrage beim Zustelldienst mit der Sendungsnummer."
        ),
        "stichworte": (
            "Adresse ändern Adressänderung Passwort vergessen Login anmelden "
            "Konto Zugangsdaten E-Mail ändern"
        ),
    },
]
