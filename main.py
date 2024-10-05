import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os

# Function to download NLTK data if not already downloaded
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Download NLTK data at the beginning
download_nltk_data()

# Function to get SERP results
def get_serp_results(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to analyze a single page
def analyze_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.title.string if soup.title else 'No title'
    h1 = soup.h1.get_text() if soup.h1 else 'No H1'
    meta_desc = ''
    for tag in soup.find_all('meta'):
        if 'name' in tag.attrs and tag.attrs['name'].lower() == 'description':
            meta_desc = tag.attrs['content']
            break
    
    page_text = soup.get_text()
    tokens = word_tokenize(page_text.lower())
    words = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    word_freq = Counter(filtered_words)
    
    content_length = len(page_text)
    
    # Find similar keywords in title and description
    title_words = set(word_tokenize(title.lower()))
    desc_words = set(word_tokenize(meta_desc.lower()))
    similar_keywords = title_words & desc_words
    
    return title, h1, meta_desc, word_freq, content_length, similar_keywords

# Streamlit app
st.title("SERP Analyzer for SEO")

query = st.text_input("Enter a keyword to search:", "")

if query:
    st.write(f"Analyzing SERP results for '{query}'...")

    soup = get_serp_results(query)
    search_results = soup.find_all('div', class_='tF2Cxc')

    result_data = []

    for result in search_results:
        link = result.find('a')['href']
        title, h1, meta_desc, word_freq, content_length, similar_keywords = analyze_page(link)
        result_data.append({
            "URL": link,
            "Title": title,
            "H1": h1,
            "Description": meta_desc,
            "Word Frequency": word_freq,
            "Content Length": content_length,
            "Similar Keywords": similar_keywords
        })

    if result_data:
        avg_title_length = sum(len(item['Title']) for item in result_data) / len(result_data)
        avg_desc_length = sum(len(item['Description']) for item in result_data) / len(result_data)
        avg_content_length = sum(item['Content Length'] for item in result_data) / len(result_data)

        st.write(f"Average Title Length: {avg_title_length:.2f} characters")
        st.write(f"Average Description Length: {avg_desc_length:.2f} characters")
        st.write(f"Average Content Length: {avg_content_length:.2f} characters")

        for idx, data in enumerate(result_data, start=1):
            st.write(f"### Result {idx}")
            st.write(f"**URL:** {data['URL']}")
            st.write(f"**Title:** {data['Title']}")
            st.write(f"**H1:** {data['H1']}")
            st.write(f"**Description:** {data['Description']}")
            st.write(f"**Word Frequency:** {data['Word Frequency'].most_common(10)}")
            st.write(f"**Similar Keywords in Title and Description:** {data['Similar Keywords']}")
