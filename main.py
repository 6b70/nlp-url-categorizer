import json
from src.categorize import Categorizer
from src.fetch_corpus_data import fetch_corpus_data


def main():
    with open('links.json', 'r') as f:
        links = json.load(f)
    with open("wikipedia-links.json", "r") as f:
        wikipedia_links = json.load(f)

    fetch_corpus_data(wikipedia_links)
    categorizer = Categorizer()
    res = categorizer.classify_urls(links)

    with open('result.json', 'w', encoding='utf-8') as fp:
        json.dump(res, fp, indent=2)


if __name__ == '__main__':
    main()