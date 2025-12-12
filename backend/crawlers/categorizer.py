"""
Intelligente Kategorisierung von Ausschreibungen basierend auf Titel und Beschreibung.
"""
import re


# Kategorie-Definitionen mit Keywords
CATEGORIES = {
    # Hochbau
    "Hochbau": [
        "hochbau", "neubau", "gebäude", "gebaeude", "wohnbau", "wohnhaus", 
        "bürogebäude", "buerogebaeude", "geschossbau", "mehrfamilienhaus",
        "einfamilienhaus", "rohbau", "mauerwerk", "betonbau"
    ],
    
    # Tiefbau
    "Tiefbau": [
        "tiefbau", "kanalbau", "kanal", "entwässerung", "entwaesserung",
        "abwasser", "kanalisation", "schacht", "rohrverlegung"
    ],
    
    # Straßenbau
    "Strassenbau": [
        "straßenbau", "strassenbau", "asphalt", "pflaster", "gehweg",
        "radweg", "fahrbahn", "verkehrsweg", "straßensanierung", "strassensanierung"
    ],
    
    # Elektroinstallation
    "Elektroinstallation": [
        "elektro", "elektrisch", "starkstrom", "schwachstrom", "beleuchtung",
        "photovoltaik", "pv-anlage", "solar", "elektroinstallation", "kabel"
    ],
    
    # Heizung/Sanitär/Klima
    "Heizung/Sanitaer/Klima": [
        "heizung", "sanitär", "sanitaer", "klima", "lüftung", "lueftung",
        "hls", "hvac", "wärmepumpe", "waermepumpe", "gas", "fernwärme"
    ],
    
    # Maler/Lackierer
    "Maler/Lackierer": [
        "maler", "anstrich", "lackier", "beschichtung", "farbig", "wandfarbe"
    ],
    
    # Trockenbau
    "Trockenbau": [
        "trockenbau", "gipskarton", "rigips", "deckenabhängung", "akustikdecke"
    ],
    
    # Fassade
    "Fassadenbau": [
        "fassade", "wärmedämmung", "waermedaemmung", "wdvs", "außenwand",
        "aussenwand", "verkleidung", "vorhangfassade"
    ],
    
    # Dach
    "Dacharbeiten": [
        "dach", "dachdecker", "dachsanierung", "dachziegel", "flachdach",
        "steildach", "abdichtung", "bitumen"
    ],
    
    # Fenster/Türen
    "Fenster/Tueren": [
        "fenster", "tür", "tuer", "verglasung", "glas", "türen", "tueren",
        "fensterbau", "rolladen", "jalousie"
    ],
    
    # Bodenbelag
    "Bodenbelag": [
        "boden", "bodenbelag", "parkett", "laminat", "fliese", "estrich",
        "teppich", "linoleum", "vinyl", "bodenlegearb"
    ],
    
    # Metallbau/Schlosser
    "Metallbau": [
        "metall", "stahl", "schlosser", "geländer", "gelaender", "stahlbau",
        "konstruktion", "schweißen", "schweissen"
    ],
    
    # Holzbau/Zimmerer
    "Holzbau/Zimmerer": [
        "holzbau", "zimmerer", "zimmermann", "holzkonstruktion", "dachstuhl",
        "carport", "holzfassade"
    ],
    
    # Garten/Landschaft
    "Garten-/Landschaftsbau": [
        "garten", "landschaft", "grünanlage", "gruenanlage", "pflanz",
        "baumpflege", "spielplatz", "außenanlage", "aussenanlage"
    ],
    
    # Abbruch/Entsorgung
    "Abbruch/Entsorgung": [
        "abbruch", "abriss", "rückbau", "rueckbau", "entsorgung", "demontage",
        "schadstoff", "asbest", "kontaminiert"
    ],
    
    # Erdarbeiten
    "Erdarbeiten": [
        "erdarbeit", "aushub", "erdbau", "baggerarbeit", "gründung", "gruendung",
        "fundament", "baugrube", "verfüllung"
    ],
    
    # Aufzüge
    "Aufzuege/Foerdertechnik": [
        "aufzug", "fahrstuhl", "lift", "förderanlage", "foerderanlage",
        "aufzugsanlage", "treppenlift"
    ],
    
    # Brandschutz
    "Brandschutz": [
        "brandschutz", "feuerschutz", "brandmelde", "sprinkler", "rauchmelder",
        "brandschott", "fluchtweg"
    ],
    
    # Planung/Architektur
    "Planung/Architektur": [
        "planung", "architekt", "generalplan", "entwurf", "bauüberwachung",
        "bauueberwachung", "projektsteuerung", "öba", "oeba"
    ],
    
    # IT/Technik
    "IT/Technik": [
        "it-", "software", "hardware", "netzwerk", "server", "datenverarbeitung",
        "telekommunikation", "medientechnik"
    ],
    
    # Reinigung
    "Reinigung": [
        "reinigung", "gebäudereinigung", "gebaeudereinigung", "unterhaltsreinigung",
        "glasreinigung", "sonderreinigung"
    ],
    
    # Möbel/Einrichtung
    "Moebel/Einrichtung": [
        "möbel", "moebel", "einrichtung", "büromöbel", "bueromoebel",
        "schrank", "tisch", "stuhl", "ausstattung"
    ],
    
    # Lieferungen
    "Lieferung/Material": [
        "lieferung", "beschaffung", "material", "baustoffe", "liefern"
    ],
}


def categorize_tender(title: str, description: str = "") -> str:
    """
    Kategorisiert eine Ausschreibung basierend auf Titel und Beschreibung.
    
    Returns:
        Kategorie-Name oder "Sonstige Bauleistungen" als Fallback
    """
    # Kombiniere Titel und Beschreibung
    text = f"{title} {description}".lower()
    
    # Zähle Matches pro Kategorie
    scores = {}
    
    for category, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                # Gewichtung: Titel-Match zählt doppelt
                if keyword in title.lower():
                    score += 2
                else:
                    score += 1
        
        if score > 0:
            scores[category] = score
    
    # Beste Kategorie zurückgeben
    if scores:
        best_category = max(scores, key=scores.get)
        return best_category
    
    return "Sonstige Bauleistungen"


def get_all_categories() -> list:
    """Gibt alle verfügbaren Kategorien zurück"""
    return list(CATEGORIES.keys()) + ["Sonstige Bauleistungen"]


# Test
if __name__ == "__main__":
    test_cases = [
        ("Bodenlegearbeiten - Neubau Forensik", "Verlegung von Parkett und Laminat"),
        ("Elektroinstallation Schule", "Starkstrom und Beleuchtung"),
        ("Dachsanierung Rathaus", "Erneuerung Flachdach mit Abdichtung"),
        ("Straßenbau Ortsdurchfahrt", "Asphaltierung und Pflasterarbeiten"),
        ("Generalplanerleistungen", "Architektur und Bauüberwachung"),
        ("Lieferung von Büromöbeln", "Schreibtische und Stühle"),
    ]
    
    print("Kategorisierungs-Test:")
    print("-" * 60)
    for title, desc in test_cases:
        cat = categorize_tender(title, desc)
        print(f"  {title[:40]:40} -> {cat}")

