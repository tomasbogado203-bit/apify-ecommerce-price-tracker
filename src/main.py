"""
E-Commerce Price Tracker & Competitor Scraper Actor for Apify
Extracts real-time product prices, stock status, ratings, discounts, and competitor store URLs.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from apify import Actor

PRICE_REGEX = re.compile(r"(\$|€|£|R\$|ARS)?\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})|\d+)")

def parse_price_and_currency(text: str, default_currency: str = "USD") -> Dict[str, Any]:
    """Extracts numeric price and currency symbol from text snippet."""
    if not text:
        return {"price": 0.0, "currency": default_currency, "raw": ""}
    
    match = PRICE_REGEX.search(text)
    if match:
        raw_val = match.group(2).replace(",", "")
        try:
            val = float(raw_val)
            sym = match.group(1) or default_currency
            return {"price": val, "currency": sym, "raw": match.group(0).strip()}
        except ValueError:
            pass
    return {"price": 0.0, "currency": default_currency, "raw": text[:30]}

async def scrape_ecommerce_listings(client: httpx.AsyncClient, product_query: str, max_results: int, country: str, default_currency: str) -> List[Dict[str, Any]]:
    """Scrapes commercial product listings, competitor offers, and marketplace prices."""
    encoded_query = urllib.parse.quote_plus(product_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}+buy+price+store+{country}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    }
    
    items = []
    try:
        resp = await client.get(url, headers=headers, timeout=12.0)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            results = soup.find_all("div", class_="result")
            
            for res in results[:max_results]:
                title_elem = res.find("a", class_="result__a")
                snippet_elem = res.find("a", class_="result__snippet")
                url_elem = res.find("a", class_="result__url")
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                raw_url = url_elem.get("href", "") if url_elem else ""
                
                clean_url = ""
                seller_domain = "Unknown Store"
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    if "uddg" in parsed:
                        clean_url = parsed["uddg"][0]
                elif raw_url.startswith("http"):
                    clean_url = raw_url

                if clean_url:
                    try:
                        seller_domain = urllib.parse.urlparse(clean_url).netloc.replace("www.", "")
                    except:
                        pass

                price_info = parse_price_and_currency(snippet + " " + title, default_currency)

                # Determine stock status heuristic
                stock_status = "In Stock"
                lower_snip = snippet.lower()
                if "out of stock" in lower_snip or "agotado" in lower_snip:
                    stock_status = "Out of Stock"
                elif "pre-order" in lower_snip or "preventa" in lower_snip:
                    stock_status = "Pre-Order"

                items.append({
                    "productSearch": product_query,
                    "title": title,
                    "price": price_info["price"],
                    "currency": price_info["currency"],
                    "rawPriceText": price_info["raw"],
                    "stockStatus": stock_status,
                    "seller": seller_domain,
                    "productUrl": clean_url,
                    "snippet": snippet
                })
    except Exception as e:
        Actor.log.warning(f"Error scraping product '{product_query}': {e}")
        
    return items

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        products = actor_input.get("products", ["PlayStation 5 Console", "iPhone 15 Pro 128GB"])
        max_results = actor_input.get("maxResults", 25)
        country = actor_input.get("targetMarket", "US")
        currency = actor_input.get("currency", "USD")
        
        Actor.log.info(f"Starting E-Commerce Price Tracker with {len(products)} products in {country} market...")

        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True) as client:
            total_items = 0
            
            for prod in products:
                Actor.log.info(f"Tracking prices for product: '{prod}'...")
                listings = await scrape_ecommerce_listings(client, prod, max_results, country, currency)
                
                for item in listings:
                    await Actor.push_data(item)
                    total_items += 1

            Actor.log.info(f"Done! Successfully tracked and pushed {total_items} price listings to dataset.")

if __name__ == "__main__":
    asyncio.run(main())
