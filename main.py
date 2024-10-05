import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import re

# Function to fetch and parse HTML of the page
def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            st.error(f"Error fetching {url}: Status code {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching {url}: {e}")
        return None

# Function to extract basic keywords by word frequency
def extract_basic_keywords(text):
    # Clean the text: remove non-alphabetic characters and convert to lowercase
    clean_text = re.sub(r'[^A-Za-z\s]', '', text).lower()
    
    # Split text into words
    words = clean_text.split()
    
    # Filter out common stop words (you can expand this list as needed)
    stop_words = ['the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'it', 'for', 'on', 'with', 'as', 'this', 'by', 'an', 'be', 'at', 'or', 'from']
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count word frequency
    word_freq = Counter(filtered_words)
    
    # Return top 10 most common keywords
    return word_freq.most_common(10)

# Function to extract on-page SEO data
def analyze_page(url):
    soup = get_html(url)
    if not soup:
        return None

    # Meta Title
    meta_title = soup.title.string if soup.title else 'No title'
    title_length = len(meta_title) if meta_title else 0

    # Meta Description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_description['content'] if meta_description else 'No description'
    description_length = len(meta_description) if meta_description else 0

    # H1 Tag
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')] or ['No H1 tags']

    # H2 Tags
    h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')] or ['No H2 tags']

    # Word Count (for article length analysis)
    article_text = soup.get_text()
    word_count = len(article_text.split())

    # Extract basic keywords
    basic_keywords = extract_basic_keywords(article_text)

    # Internal Links
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if url in href or href.startswith('/'):  # If the link is internal
            internal_links.append(href)
    internal_links = internal_links if internal_links else ['No internal links']

    # Return analysis as a dictionary
    return {
        'url': url,
        'meta_title': meta_title,
        'title_length': title_length,
        'meta_description': meta_description,
        'description_length': description_length,
        'h1_tags': ', '.join(h1_tags),
        'h2_tags': ', '.join(h2_tags),
        'word_count': word_count,
        'basic_keywords': ', '.join([kw[0] for kw in basic_keywords]),
        'internal_links': ', '.join(internal_links)
    }

# Function to analyze multiple competitor pages
def analyze_pages(urls):
    data = []
    for url in urls:
        result = analyze_page(url)
        if result:
            data.append(result)
    
    # Convert to DataFrame for better analysis
    df = pd.DataFrame(data)
    return df

# Streamlit UI
st.title('On-Page SEO Analysis Tool')

# Input for URLs
url_input = st.text_area("Enter URLs (one per line)", "https://example.com\nhttps://example2.com")
urls = [url.strip() for url in url_input.split('\n') if url.strip()]

if st.button('Analyze'):
    if urls:
        # Analyze the pages
        df = analyze_pages(urls)

        if not df.empty:
            st.write("### Complete On-Page SEO Analysis Table:")
            st.dataframe(df)

            # Calculate and display averages
            average_word_count = df['word_count'].mean()
            average_title_length = df['title_length'].mean()
            average_description_length = df['description_length'].mean()

            st.write(f'**Average word count per article:** {average_word_count:.2f}')
            st.write(f'**Average title length:** {average_title_length:.2f} characters')
            st.write(f'**Average meta description length:** {average_description_length:.2f} characters')

            # Option to download results as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='on_page_seo_analysis.csv',
                mime='text/csv'
            )
        else:
            st.warning("No valid data found. Please check the URLs and try again.")
    else:
        st.warning("Please enter at least one URL.")

