import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import re
import time
import os
import ssl
from urllib.parse import urlparse

# SSL Context Fix for Certain Websites
ssl._create_default_https_context = ssl._create_unverified_context

# Function to fetch website data
def get_website_data(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        return None
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extracting basic SEO information
    title = soup.find('title').get_text() if soup.find('title') else "No title"
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_description['content'] if meta_description else "No meta description"
    
    h1_tags = [h1.get_text() for h1 in soup.find_all('h1')]
    h2_tags = [h2.get_text() for h2 in soup.find_all('h2')]
    img_tags = [img['src'] for img in soup.find_all('img') if 'alt' in img.attrs]
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    canonical_tag = soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else None
    favicon = soup.find('link', rel='icon')['href'] if soup.find('link', rel='icon') else None
    robots_txt = urlparse(url)._replace(path='/robots.txt').geturl()
    sitemap_xml = urlparse(url)._replace(path='/sitemap.xml').geturl()

    # SSL Check
    ssl_check = "Yes" if url.startswith("https://") else "No"
    
    # Social Media Tags
    og_tags = soup.find_all('meta', property='og:image')
    twitter_tags = soup.find_all('meta', name='twitter:image')
    
    # Checking for Google Analytics/Tag Manager
    analytics_check = "Yes" if "google-analytics.com" in response.text else "No"
    
    # Image Alt Text Check
    missing_alt_tags = len([img for img in soup.find_all('img') if 'alt' not in img.attrs])
    
    # Word count
    text = soup.get_text()
    word_count = len(text.split())
    
    # Internal and external links count
    internal_links = [link for link in links if link.startswith(url)]
    external_links = [link for link in links if not link.startswith(url)]
    
    # Robots.txt & Sitemap availability
    robots_txt_avail = "Yes" if requests.head(robots_txt).status_code == 200 else "No"
    sitemap_avail = "Yes" if requests.head(sitemap_xml).status_code == 200 else "No"
    
    return {
        'title': title,
        'meta_description': meta_description,
        'h1_tags': len(h1_tags),
        'h2_tags': len(h2_tags),
        'img_tags': len(img_tags),
        'broken_links': len(internal_links),
        'favicon': favicon,
        'canonical_tag': canonical_tag,
        'ssl': ssl_check,
        'og_tags': len(og_tags),
        'twitter_tags': len(twitter_tags),
        'google_analytics': analytics_check,
        'missing_alt_tags': missing_alt_tags,
        'word_count': word_count,
        'internal_links': len(internal_links),
        'external_links': len(external_links),
        'robots_txt_avail': robots_txt_avail,
        'sitemap_avail': sitemap_avail
    }

# SEO Analysis
def analyze_seo_data(sites):
    results = []
    for site in sites:
        data = get_website_data(site)
        if data:
            results.append({
                'Website': site,
                'Title': data['title'],
                'Meta Description': data['meta_description'],
                'H1 Tags': data['h1_tags'],
                'H2 Tags': data['h2_tags'],
                'Images': data['img_tags'],
                'Broken Links': data['broken_links'],
                'Favicon': data['favicon'],
                'Canonical Tag': data['canonical_tag'],
                'SSL': data['ssl'],
                'Open Graph Tags': data['og_tags'],
                'Twitter Tags': data['twitter_tags'],
                'Google Analytics': data['google_analytics'],
                'Missing Alt Tags': data['missing_alt_tags'],
                'Word Count': data['word_count'],
                'Internal Links': data['internal_links'],
                'External Links': data['external_links'],
                'Robots.txt Available': data['robots_txt_avail'],
                'Sitemap Available': data['sitemap_avail'],
            })
        else:
            results.append({
                'Website': site,
                'Title': 'Error fetching title',
                'Meta Description': 'Error fetching meta description',
                'H1 Tags': 0,
                'H2 Tags': 0,
                'Images': 0,
                'Broken Links': 0,
                'Favicon': 'No favicon',
                'Canonical Tag': 'No canonical tag',
                'SSL': 'No',
                'Open Graph Tags': 0,
                'Twitter Tags': 0,
                'Google Analytics': 'No',
                'Missing Alt Tags': 0,
                'Word Count': 0,
                'Internal Links': 0,
                'External Links': 0,
                'Robots.txt Available': 'No',
                'Sitemap Available': 'No',
            })
    return results

# Generate CSV Report
def generate_csv_report(data):
    df = pd.DataFrame(data)
    file_path = "/tmp/website_seo_analysis.csv"
    df.to_csv(file_path, index=False)
    return file_path

# Streamlit Interface
st.title("Complete Website SEO & Analysis Tool")
st.markdown("### Enter up to 5 website URLs for SEO analysis")

# Input for websites
website_input = st.text_area("Enter URLs (separate by commas)", "")
websites = [url.strip() for url in website_input.split(',') if url.strip()]

if len(websites) > 5:
    st.error("Please limit to 5 websites.")
else:
    if st.button("Start Analysis"):
        if websites:
            st.info("Analyzing websites... please wait.")
            with st.spinner('Processing...'):
                # Perform SEO analysis
                results = analyze_seo_data(websites)

                # Show results in a table
                df = pd.DataFrame(results)
                st.dataframe(df)

                # Provide download option
                csv_file = generate_csv_report(results)
                st.download_button(
                    label="Download CSV Report",
                    data=open(csv_file, 'rb'),
                    file_name="website_seo_analysis.csv",
                    mime="text/csv"
                )
        else:
            st.error("Please enter at least one website URL.")
