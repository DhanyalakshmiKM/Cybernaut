import requests
from bs4 import BeautifulSoup
import json

def scrape_amazon(query, pages=1):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    base_url = "https://www.amazon.in/s"
    products = []

    for page in range(1, pages + 1):
        params = {"k": query, "page": page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"⚠ Failed to fetch page {page}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})

        for item in results:
          
            title = item.h2.text.strip() if item.h2 else None

            
            link = None
            a_tag = item.find("a", class_="a-link-normal")
            if a_tag and a_tag.has_attr("href"):
                link = "https://www.amazon.in" + a_tag["href"]

           
            price_span = item.find("span", class_="a-price-whole")
            price = int(price_span.text.replace(",", "")) if price_span else None

           
            rating_span = item.find("span", class_="a-icon-alt")
            rating = rating_span.text if rating_span else None

            if title and price:
                products.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "link": link
                })

    return products


if __name__ == "__main__":
    query = "headphones"   # change keyword as needed
    products = scrape_amazon(query, pages=1)

    if products:
        print(json.dumps(products, indent=4, ensure_ascii=False))
    else:
        print("⚠ No products found. Amazon may be blocking requests.")











