from bs4 import BeautifulSoup
import requests
import os

# Define the URLs for different wine categories
wine_categories = {
    'Red Wines': 'https://www.lcbo.com/en/products/wine/red-wine#t=clp-products-wine-red_wine',
    'White Wines': 'https://www.lcbo.com/en/products/wine/white-wine#t=clp-products-wine-white_wine',
    'Rosé Wines': 'https://www.lcbo.com/en/products/wine/rose-wine#t=clp-products-wine-ros%C3%A9_wine',
    'Sparkling Wines': 'https://www.lcbo.com/en/products/wine/sparkling-wine#t=clp-products-wine-sparkling_wine',
    'Champagne Wines': 'https://www.lcbo.com/en/products/wine/champagne#t=clp-products-wine-champagne',
    'Fortified Wines': 'https://www.lcbo.com/en/products/wine/fortified-wine#t=clp-products-wine-fortified_wine'
}

output_directory = 'html_out'
os.makedirs(output_directory, exist_ok=True)

for category, url in wine_categories.items():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    file_path = os.path.join(output_directory, f"{category.replace(' ', '_')}_output.html")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    print(f"Saved HTML content for {category} to {file_path}")
