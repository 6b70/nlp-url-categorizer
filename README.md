# NLP URL Categorizer

This project is a Python tool for classifying URLs into predefined categories using Natural Language Processing. It extracts and cleans text from web pages, processes the content, and compares it against a corpus of categorized text data using a probabilistic model.

Sample output data for the current contents of `links.json` can be found in `result.json`.

## How It Works

1. Downloads Wikipedia data into `category_data/` to create the categorized corpus.
2. Fetches web pages and extracts title, meta tags, and content.
3. Lemmatizes and cleans the extracted text.
4. Compares the text against the categorized corpus.
5. Assigns the URL to the category with the highest probabilistic match.


## Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - `requests`
  - `nltk`
  - `Scrapy`
  - `beautifulsoup4`
  - `newspaper3k`
  - `lxml_html_clean`

---

## Installation

1. **Clone the repository**:
   ```
   git clone git@github.com:6b70/nlp-url-categorizer.git
   cd nlp-url-categorizer
   ```

2. **Set up a virtual environment**:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

---

## Usage

### Input Data
- The input is a JSON list of links stored in `links.json`. Example:
  ```json
  [
      "https://developer.apple.com",
      "https://github.com"
  ]
  ```
- **Corpus Data**:
  - The program automatically downloads corpus data from Wikipedia and organizes it into `category_data/` for predefined categories.
    - Categories are stored in directories, each containing .txt files with data.

1. **Run the Program**:
   ```
   python3 main.py
   ```

2. **Output**:
   - The program generates a `result.json` file with categorized results based on the input URLs.
