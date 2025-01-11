from newspaper import fulltext
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
import requests, nltk

nltk.download('stopwords')
nltk.download('wordnet')

class LanguageError(Exception):
    pass

class Scraper:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def fetch_page(self, url):
        soup, html = self._fetch_content(url)
        if not soup or not html:
            raise ValueError("Failed to fetch page")
        title, meta, content = self._extract_and_clean(soup, html)
        return {"title": title, "meta": meta, "content": content}

    def _fetch_content(self, url: str) -> tuple[BeautifulSoup | None, str | None]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            lang = soup.html.get('lang', 'en')
            if not ('en' in lang or 'mul' in lang):
                raise ValueError("Page isn't english")
            return soup, response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None, None

    def _extract_and_clean(self, soup: BeautifulSoup, html: str):
        # Extract title and meta tags
        title_tag = soup.title.string.strip() if soup.title and soup.title.string else ''
        title = title_tag.split('|')[0].strip() if '|' in title_tag else title_tag
        meta_tags = soup.find_all('meta')
        description, keywords = [], ''
        for tag in meta_tags:
            attr = tag.get('name') or tag.get('property')
            content = tag.get('content', '')
            if attr in ['og:description', 'description']:
                description.append(content)
            elif attr == 'keywords':
                keywords = content
        meta = {'keywords': keywords, 'desc': description} if description or keywords else None

        # Clean text
        try:
            raw_text = fulltext(html)
        except:
            raw_text = soup.get_text(separator=' ', strip=True)

        for symbol in punctuation:
            raw_text = raw_text.replace(symbol, ' ')
        words = [
            self.lemmatizer.lemmatize(word)
            for word in raw_text.split()
            if word.isalpha() and word.lower() not in self.stopwords
        ]
        return title, meta, words
