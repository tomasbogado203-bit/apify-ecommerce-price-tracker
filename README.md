# E-Commerce Price Tracker & Competitor Scraper

Monitor real-time product prices, competitor discounts, seller domains, and stock availability across major online marketplaces and stores (Amazon, Mercado Libre, Shopify, Walmart, eBay).

## 🚀 Features

- **Automated Price Extraction:** Automatically extracts price, currency, seller store, and stock status.
- **Multi-Product Monitoring:** Track dozens or hundreds of SKU names in a single run.
- **Global Market Support:** Filter by target country (US, ES, AR, MX, BR, UK, etc.).
- **Export Formats:** Direct export to **Excel (XLSX)**, **CSV**, and **JSON**.

## 📥 Input Example

```json
{
  "products": [
    "PlayStation 5 Slim Console",
    "iPhone 15 Pro Max 256GB",
    "Sony WH-1000XM5 Noise Canceling Headphones"
  ],
  "maxResults": 30,
  "targetMarket": "US",
  "currency": "USD"
}
```

## 📤 Output Format

Each record in the dataset includes:
- `productSearch`: Search query
- `title`: Product listing title
- `price`: Numeric price
- `currency`: Currency symbol
- `stockStatus`: In Stock / Out of Stock / Pre-Order
- `seller`: Seller domain or marketplace
- `productUrl`: Direct product link
- `snippet`: Store description and specs
