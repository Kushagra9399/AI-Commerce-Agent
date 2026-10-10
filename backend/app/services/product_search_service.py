import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.core.config import settings


class ProductSearchService:
    """Search Amazon product listings through SerpAPI."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.api_key = settings.SERPAPI_API_KEY

    @staticmethod
    def _price(value):
        if isinstance(value, (int, float)):
            return float(value)
        if not value:
            return None
        match = re.search(r"[-+]?\\d[\\d,]*(?:\\.\\d+)?", str(value))
        if not match:
            return None
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None

    @staticmethod
    def _discount(value):
        if value is None:
            return None
        match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*%", str(value))
        return float(match.group(1)) if match else None

    def _request(self, params):
        if not self.api_key:
            raise RuntimeError("SERPAPI_API_KEY is not configured in the backend environment.")

        params = {
            **params,
            "api_key": self.api_key,
            "amazon_domain": "amazon.in",
        }
        url = "https://serpapi.com/search.json?" + urlencode(params)
        request = Request(url, headers={"User-Agent": "AI-Commerce-Agent/1.0"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"SerpAPI request failed with HTTP {exc.code}.") from exc
        except (URLError, TimeoutError) as exc:
            raise RuntimeError("Could not connect to SerpAPI. Check network connectivity.") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("SerpAPI returned an invalid JSON response.") from exc

        if data.get("error"):
            raise RuntimeError(f"SerpAPI error: {data['error']}")
        return data

    def _normalize(self, item):
        price = self._price(item.get("extracted_price"))
        if price is None:
            price = self._price(item.get("price"))
        title = item.get("title") or item.get("name")
        asin = item.get("asin") or item.get("product_id")
        if not title or not asin:
            return None

        discount = self._discount(item.get("discount"))
        return {
            "id": str(asin),
            "product_id": str(asin),
            "asin": str(asin),
            "name": title,
            "title": title,
            "brand": item.get("brand") or "Unknown",
            "category": item.get("category"),
            "sale_price": price,
            "price": price,
            "extracted_price": price,
            "market_price": self._price(item.get("old_price")),
            "discount_percent": discount,
            "discount": item.get("discount"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews"),
            "thumbnail": item.get("thumbnail"),
            "image": item.get("thumbnail"),
            "link": item.get("link"),
            "source": "serpapi_amazon_in",
            "stock": None,
            "is_active": True,
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_price: float | None = None,
        min_price: float | None = None,
        brand: str | None = None,
        min_discount: float | None = None,
        in_stock_only: bool = False,
    ):
        if not query or not query.strip():
            return []

        data = self._request({
            "engine": "amazon",
            "k": query.strip(),
        })
        raw_results = data.get("organic_results") or []
        results = []
        seen = set()

        for raw in raw_results:
            product = self._normalize(raw)
            if not product or product["id"] in seen:
                continue
            seen.add(product["id"])

            price = product["sale_price"]
            if max_price is not None and (price is None or price > max_price):
                continue
            if min_price is not None and (price is None or price < min_price):
                continue
            if brand and brand.lower() not in product["name"].lower() and brand.lower() not in product["brand"].lower():
                continue
            if min_discount is not None and (product["discount_percent"] is None or product["discount_percent"] < min_discount):
                continue

            results.append(product)
            if len(results) >= max(1, min(top_k, 20)):
                break

        return results

    def get_product(self, product_id: str):
        if not product_id:
            return None
        data = self._request({
            "engine": "amazon_product",
            "asin": product_id,
        })
        raw = data.get("product_results")
        if not isinstance(raw, dict):
            return None
        return self._normalize(raw)
