import requests
from pathlib import Path

CATEGORIES_DIR = Path('./category_data/')

def _fetch_wikipedia_extract(title: str) -> str:
    params = {
        "format": "json",
        "redirects": 1,
        "titles": title,
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "origin": "*",
        "limit": 1
    }
    response = requests.get("https://en.wikipedia.org/w/api.php", params=params)
    response.raise_for_status()
    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    page = next(iter(pages.values()), {})
    return {"text": page.get('extract', '')}['text']

def fetch_corpus_data(layouts):
    for category, titles in layouts.items():
        category_dir = CATEGORIES_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)

        for title in titles:
            target_file = category_dir / f"{title}.txt"
            if not target_file.exists():
                try:
                    corpus = _fetch_wikipedia_extract(title)
                    target_file.write_text(corpus)
                    print(f"Saved: {target_file}")
                except requests.RequestException as e:
                    print(f"Error fetching '{title}': {e}")


