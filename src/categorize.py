import json
from string import punctuation
from math import log10
from collections import Counter
from src.scrape import Scraper
from src.fetch_corpus_data import CATEGORIES_DIR
from pathlib import Path

class Categorizer:
    def __init__(self):
        self.scraper = Scraper()
        self.url_data = {}

    def _extract_vocabulary(self, url):
        entry = self.url_data.get(url, {})
        desc_keywords = entry.get("desc")
        title = entry.get("title", "")
        content = entry.get("desc")
        keywords = ""
        desc = []

        if desc_keywords:
            keywords = desc_keywords.get('keywords', "")
            desc = desc_keywords.get('desc', [])

        return f"{title} {keywords} {' '.join(desc)} {content}"

    def _get_corpus_vocab(self, directory):
        vocab_text = ""
        files = Path(directory).glob('*.txt')
        for filepath in files:
            vocab_text += ' ' + filepath.read_text()
        for symbol in punctuation:
            vocab_text = vocab_text.replace(symbol, ' ')
        return vocab_text.lower(), len(list(files))

    def _get_entire_corpus_vocab(self):
        corpus_dirs = [d for d in CATEGORIES_DIR.iterdir() if d.is_dir()]
        all_vocab = ""
        for directory in corpus_dirs:
            corpus_vocab, _ = self._get_corpus_vocab(directory)
            all_vocab += ' ' + corpus_vocab
        return all_vocab

    def _get_non_corpus_vocab(self, exclude_dir):
        corpus_dirs = [d for d in CATEGORIES_DIR.glob('*/') if exclude_dir not in str(d)]
        non_corpus_vocab = ""
        for directory in corpus_dirs:
            corpus_vocab, _ = self._get_corpus_vocab(directory)
            non_corpus_vocab += ' ' + corpus_vocab
        for symbol in punctuation:
            non_corpus_vocab = non_corpus_vocab.replace(symbol, ' ')
        return non_corpus_vocab

    def _bayes(self, combined_vocab):
        words = [w for w in combined_vocab.lower().split() if len(w) > 1]
        category_dirs = [d for d in CATEGORIES_DIR.iterdir() if d.is_dir()]
        total_files = sum(1 for _ in CATEGORIES_DIR.glob('*/*.txt'))

        entire_corpus = self._get_entire_corpus_vocab()
        total_vocab_size = len(set(entire_corpus.split()))

        best_category = None
        best_score = float('-inf')
        smallest_delta = float('inf')

        for corpus in category_dirs:
            cache_path = corpus / "cache.json.ext"
            if cache_path.exists():
                with cache_path.open("r", encoding='utf-8') as f:
                    data = json.load(f)
                freq_vocab = Counter(data["frequency_corpus_vocab"])
                freq_non_vocab = Counter(data["frequency_corpus_non_vocab"])
                words_corpus = data["words_corpus"]
                non_words_corpus = data["non_words_corpus"]
                corpus_score = data["corpus_is"]
                corpus_score_not = data["corpus_is_not"]
            else:
                corpus_vocab, file_count = self._get_corpus_vocab(corpus)
                non_corpus_vocab = self._get_non_corpus_vocab(corpus)
                p_vj = file_count / total_files
                corpus_score = log10(p_vj)
                corpus_score_not = log10(1 - p_vj)

                vocab_words = [w for w in corpus_vocab.split() if len(w) > 1]
                non_vocab_words = [w for w in non_corpus_vocab.split() if len(w) > 1]

                freq_vocab = Counter(vocab_words)
                freq_non_vocab = Counter(non_vocab_words)
                words_corpus = len(vocab_words)
                non_words_corpus = len(non_vocab_words)

                data = {
                    "frequency_corpus_vocab": dict(freq_vocab),
                    "frequency_corpus_non_vocab": dict(freq_non_vocab),
                    "words_corpus": words_corpus,
                    "non_words_corpus": non_words_corpus,
                    "corpus_is": corpus_score,
                    "corpus_is_not": corpus_score_not,
                }
                with cache_path.open("w", encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

            delta = 0
            for word in words:
                match = freq_vocab.get(word, 0)
                corpus_score += log10((match + 1) / (words_corpus + total_vocab_size))

                non_match = freq_non_vocab.get(word, 0)
                corpus_score_not += log10((non_match + 1) / (non_words_corpus + total_vocab_size))
                delta = abs(corpus_score_not - corpus_score)

            if corpus_score > corpus_score_not or delta < 10:
                if corpus_score > best_score or (delta < smallest_delta and abs(best_score - corpus_score) <= 1):
                    best_category = corpus
                    best_score = corpus_score
                    smallest_delta = delta

        return best_category, best_score

    def _clean_category(self, category_path):
        full_path = Path(category_path)
        return full_path.name

    def classify_urls(self, urls):
        results = {}
        for url in urls:
            try:
                # scrape page data
                data = self.scraper.fetch_page(url)
                self.url_data[url] = data

                # classify page
                vocab = self._extract_vocabulary(url)
                category, score = self._bayes(vocab)
                results[url] = self._clean_category(category)
            except Exception as e:
                results[url] = f"Failed: {e}"
        return results
