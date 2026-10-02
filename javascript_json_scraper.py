import requests
import pandas as pd
import json

def fetch_json_data(api_url):
    """
    Fetches JSON data from the given API endpoint.
    Handles network errors and checks the response status code.
    """
    print(f"Fetching data from JSON endpoint: {api_url}")
    try:
        response = requests.get(api_url, timeout=10)    
        if response.status_code == 200:
            print("Successfully connected to the API!")
    
            return response.json()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle invalid JSON responses
        print(f"Failed to parse JSON response: {e}")
        return None

def extract_data(json_data):
    """
    Extracts the useful fields (list of products) from the parsed JSON data.
    """
    if not json_data:
        return []
    products = json_data.get('products', [])
    
    if not products:
        print("No products found in the JSON data.")
        return []
        
    print(f"Extracted {len(products)} products from the JSON payload.")
    return products

def filter_data(products, min_price=50, min_rating=4.0):
    """
    Filters the products based on specific criteria to satisfy the filtering BONUS.
    We filter products where price > min_price AND rating >= min_rating.
    """
    filtered_products = []
    
    for product in products:
        price = product.get('price', 0)
        rating = product.get('rating', 0.0)
        
        if price > min_price and rating >= min_rating:
            filtered_products.append({
                'id': product.get('id'),
                'title': product.get('title', 'No Title'),
                'category': product.get('category', 'Uncategorized'),
                'price': price,
                'rating': rating,
                'stock': product.get('stock', 0)
            })
            
    print(f"Filtered data: {len(filtered_products)} products match the criteria (Price > ${min_price} and Rating >= {min_rating}).")
    return filtered_products

def save_data(filtered_products, csv_filename, json_filename):
    """
    Converts the filtered data into a Pandas DataFrame and saves it to CSV and JSON formats.
    """
    if not filtered_products:
        print("No data to save.")
        return
        
    df = pd.DataFrame(filtered_products)
    
    print("\nData Preview (Pandas DataFrame):")
    print(df.head())
    
    try:
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\nData successfully saved to '{csv_filename}'.")

        df.to_json(json_filename, orient='records', indent=4)
        print(f"Data successfully saved to '{json_filename}'.")
    except Exception as e:
        print(f"An error occurred while saving files: {e}")

def main():
    print("--- Starting JavaScript JSON Scraper ---")
    
    api_endpoint = "https://dummyjson.com/products?limit=50"
    
    json_data = fetch_json_data(api_endpoint)
    
    products = extract_data(json_data)
    
    if products:
        filtered_products = filter_data(products, min_price=100, min_rating=4.5)
        

        save_data(filtered_products, "javascript_data.csv", "javascript_data.json")
    else:
        print("Scraping process stopped due to empty results.")
        
    print("--- Scraping Finished ---")

if __name__ == "__main__":
    main()
