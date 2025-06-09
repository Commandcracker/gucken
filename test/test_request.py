import asyncio
import sys
import os

# Füge das src-Verzeichnis zum sys.path hinzu, damit die Imports funktionieren
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from gucken.provider.aniworld import AniWorldProvider

async def test_get_popular():
    results = await AniWorldProvider.get_popular()
    assert isinstance(results, list), "Ergebnis ist keine Liste"
    assert len(results) > 0, "Keine populären Animes gefunden"
    for entry in results:
        assert "name" in entry, "Feld 'name' fehlt"
        assert "img" in entry, "Feld 'img' fehlt"
        assert "link" in entry, "Feld 'link' fehlt"
        print(entry)

if __name__ == "__main__":
    asyncio.run(test_get_popular())