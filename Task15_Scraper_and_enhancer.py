import sys
import json
import requests
from bs4 import BeautifulSoup
import openai
import os
import re

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")

def scrape_product(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error: Unable to retrieve the URL.")
        sys.exit(1)
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # These selectors are examples and may need adjustment per target site structure.
    name_elem = soup.find("h1")
    description_elem = soup.find("div", id="product_description")
    price_elem = soup.find("p", class_="price_color")
    rating_elem = soup.find("p", class_="star-rating")

    product = {
        "name": name_elem.get_text(strip=True) if name_elem else "Unknown Product",
        "description": description_elem.get_text(strip=True) if description_elem else "No description available.",
        "price": price_elem.get_text(strip=True) if price_elem else "Price not found",
        "rating": rating_elem.get_text(strip=True) if rating_elem else "No rating"
    }
    return product

def improve_description(product):
    price_cleaned = re.sub(r'[^\d.]', '', product["price"])
    prompt = (
        f"Improve the product description by considering the product name, price, review rating, and existing description.\n\n"
        f"Product Name: {product['name']}\n"
        f"Original Description: {product['description']}\n"
        f"Price: {price_cleaned}\n"
        f"Review Rating: {product['rating']}\n\n"
        "Provide a more appealing and accurate improved description."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    improved_description = response.choices[0].message.content.strip()
    return improved_description

def main():
    product_url = input("Enter product URL: ").strip()
    if not product_url:
        print("Error: URL cannot be empty.")
        sys.exit(1)

    product = scrape_product(product_url)
    product["improved_description"] = improve_description(product)

    # Output the product details as JSON
    print(json.dumps(product, indent=4))

if __name__ == "__main__":
    main()