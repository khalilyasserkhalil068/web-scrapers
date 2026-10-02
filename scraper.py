import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
REQUEST_TIMEOUT = 10

def fetch_page(url: str) -> Optional[BeautifulSoup]: 
    """
    Fetches the HTML content of a given URL.
    Returns a BeautifulSoup object or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"Successfully fetched: {url}")
            return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching {url}: {e}")
    return None

def parse_book(book_soup: BeautifulSoup, base_url: str) -> Optional[Dict[str, str]]:
    """
    Parses an individual book's HTML element to extract details.
    Returns a dictionary containing the extracted information, or None if essential data is missing.
    """
    try:
        title_tag = book_soup.find('h3').find('a')
        if not title_tag:
            return None
            
        title = title_tag.get('title')
        
        price_tag = book_soup.find('p', class_='price_color')
        price = price_tag.text.strip() if price_tag else "Unknown"
        
        avail_tag = book_soup.find('p', class_='instock availability')
        availability = avail_tag.text.strip() if avail_tag else "Unknown"
        
        rating_tag = book_soup.find('p', class_='star-rating')
        rating = rating_tag.get('class')[1] if rating_tag and len(rating_tag.get('class', [])) > 1 else "None"
        
        product_href = title_tag.get('href')
        product_url = urljoin(base_url, product_href) if product_href else ""
        
        if not title or not product_url:
            return None
            
        return {
            "Title": title,
            "Price": price,
            "Availability": availability,
            "Rating": rating,
            "Product URL": product_url
        }
    except Exception as e:
        print(f"Error parsing a book: {e}")
        return None

def scrape_page(page_url: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Scrapes all books on a single page.
    Returns a list of book dictionaries and the URL of the next page (if any).
    """
    soup = fetch_page(page_url)
    if not soup:
        return [], None
    
    books_data = []
    book_pods = soup.find_all('article', class_='product_pod')
    
    for pod in book_pods:
        book_info = parse_book(pod, BASE_URL)
        if book_info:
            books_data.append(book_info)
            
    next_button = soup.find('li', class_='next')
    if next_button:
        next_anchor = next_button.find('a')
        if next_anchor:
            next_page_href = next_anchor.get('href')
            next_page_url = urljoin(page_url, next_page_href)
            return books_data, next_page_url
            
    return books_data, None

def scrape_all_pages(start_url: str) -> List[Dict[str, str]]:
    """
    Scrapes books from all available pages starting from the given URL.
    Returns a list containing all scraped book dictionaries.
    """
    all_books = []
    current_url: Optional[str] = start_url
    pages_scraped = 0
    
    while current_url:
        books_on_page, next_url = scrape_page(current_url)
        if not books_on_page and not next_url:
            break
            
        all_books.extend(books_on_page)
        current_url = next_url
        pages_scraped += 1
        
        time.sleep(1) 
        
    return all_books

def save_data(df: pd.DataFrame) -> None:
    """
    Saves the pandas DataFrame to CSV and TXT files safely in the script's directory.
    """
    try:
        output_dir = Path(__file__).resolve().parent
        
        csv_path = output_dir / "books.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Data successfully saved to: {csv_path}")

        Excel_Path = output_dir / "books.xlsx"
        df.to_excel(Excel_Path, index=False, encoding='utf-8')
        print(f"Data successfully saved to: {Excel_Path}")
        
        txt_path = output_dir / "books.txt"
        df.to_csv(txt_path, sep='\t', index=False, encoding='utf-8')
        print(f"Data successfully saved to: {txt_path}")
        
    except Exception as e:
        print(f"Error saving data: {e}")

def main() -> None:
    print("Starting book scraping process...")
    scraped_books = scrape_all_pages(START_URL)
    
    if scraped_books:
        print(f"Successfully scraped {len(scraped_books)} books in total.")
        df = pd.DataFrame(scraped_books)
        save_data(df)
    else:
        print("No books were scraped. Please check your network connection or target URLs.")

if __name__ == "__main__":
    main()