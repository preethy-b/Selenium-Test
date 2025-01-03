import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import Counter
import langdetect
import time
import os
import requests
from googletrans import Translator
import re

XPATH_OPINION_SECTION = "//*[@id='csw']//a[contains(text(),'Opinión')]" # Xpath used for locating opinion_section

def fetch_articles(browser):
    # Navigate to the Opinion section of the website
    opinion_section = browser.find_element(By.XPATH,XPATH_OPINION_SECTION)
    opinion_section.click()
    time.sleep(5)
    article_tags = browser.find_elements(By.TAG_NAME, "article")
    articles = []
    # Fetch All articles
    for article in article_tags:
        try:
            title = article.find_element(By.CSS_SELECTOR, "h1, h2, h3").text
            content = article.text
            articles.append({"title": title, "content": content})
        except Exception as e:
            print(f"Error fetching article: {e}")
    detected_language = langdetect.detect(str(articles))
    print(f"Article Language is: {detected_language}")
    assert detected_language == "es"
    assert len(articles) > 0
    return article_tags, articles

def download_image(image_url, save_path):
    """Download an image from a URL and save it to a local file."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return False

def test_website_text(browser):
    # Ensure that the website's text is displayed in Spanish

    body_text = browser.find_element(By.TAG_NAME, "body").text
    detected_language = langdetect.detect(body_text)
    assert detected_language == "es"

def test_scrape_articles_in_opinion_Section(browser,setup_directory):
    article_tags, articles = fetch_articles(browser)
    directory = setup_directory
    for i in range(0,5):
        try:
            # Fetch the first five articles in this section and print the article title and content
            print(f"Article : {i + 1}")
            print("Article Title:",articles[i]['title'])
            print("Article Content:",articles[i]['content'])
            # If available, download and save the cover image of each article to your local machine
            img_element = article_tags[i].find_element(By.TAG_NAME,"img")
            image_url = img_element.get_attribute("src")
            save_path = os.path.join(directory, f"article_{i + 1}_cover.jpg")
            if download_image(image_url, save_path):
                print(f"Downloaded: {image_url} -> {save_path}")
            else:
                print(f"Failed to download: {image_url}")
        except Exception as e:
            print(f"No cover image for article {i + 1}")

def test_translate_and_analyze_article_headers(browser):
    article_tags, articles = fetch_articles(browser)
    translated_article_titles = []
    translator = Translator()
    # Translate the title of each article to English using google trans API library
    for i in range(0,5):
        translation = translator.translate(articles[i]['title'],src='es',dest='en')
        print(translation)
        print(translation.text)
        translated_article_titles.append(translation.text)
    # Print the translated headers
    print(translated_article_titles)
    all_titles = " ".join(translated_article_titles).lower()
    words = re.split(r'[\s\W]+', all_titles)
    # From the translated headers, identify any words that are repeated more than twice across all headers combined
    word_counts = Counter(words)
    repeated_words = {word: count for word,count in word_counts.items() if count > 2}
    # Print each repeated word along with the count of its occurrences if repeated more than twice
    if repeated_words:
        print("Words repeated more than twice:")
        for word, count in repeated_words.items():
            print(f"{word}: {count}")
    else:
        print("No words are repeated more than twice")