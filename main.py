import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Function to get SERP results
def get_serp_results(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to analyze a single page
def analyze_page(link):
    response = requests.get(link)
    page_soup = BeautifulSoup(response.text, 'html.parser')
    title = page_soup.title.string if page_soup.title else 'No Title'
    h1 = page_soup.h1.string if page_soup.h1 else 'No H1'
    meta_desc = page_soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc['content'] if meta_desc else 'No Meta Description'
    
    page_text = page_soup.get_text()
    tokens = word_tokenize(page_text.lower())
    
    words = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    
    word_freq = Counter(filtered_words).most_common(10)  # Get top 10 words
    content_length = len(page_text)
    
    return title, h1, meta_desc, word_freq, content_length

# Function to extract related topics from SERP results
def topical_mapping(query):
    soup = get_serp_results(query)
    search_results = soup.find_all('div', class_='tF2Cxc')
    
    all_word_freq = Counter()
    
    for result in search_results:
        link = result.find('a')['href']
        title, h1, meta_desc, word_freq, content_length = analyze_page(link)
        all_word_freq.update(dict(word_freq))
    
    return all_word_freq.most_common(10)

# Function to generate semantic keywords
def generate_semantic_keywords(query):
    related_topics = topical_mapping(query)
    semantic_keywords = {word for word, freq in related_topics}
    return list(semantic_keywords)

# Streamlit app
st.title("Keyword Analyzer for SEO")

query = st.text_input("Enter a keyword to analyze:", "")

if query:
    st.write(f"Analyzing '{query}'...")

    st.write("### Semantic Keywords")
    semantic_keywords = generate_semantic_keywords(query)
    
    if semantic_keywords:
        semantic_keywords_df = pd.DataFrame(semantic_keywords, columns=['Semantic Keywords'])
        st.table(semantic_keywords_df)
    else:
        st.write("No semantic keywords found.")
