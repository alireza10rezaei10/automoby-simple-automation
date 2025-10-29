import requests
from typing import Any
import time


class Main:
    def __init__(self):
        self.url = (
            "https://mvm5052.com/wp-json/wc/store/v1/products?per_page=100&page={page}"
        )
        self.headers = {
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
            )
        }
        self.max_retries = 3

    def _clean_products(self, products: dict[str, Any]) -> dict[str:str]:
        return [
            {
                "name": product.get("name"),
                "quantity": product.get("add_to_cart").get("maximum"),
                "in_stock": product.get("stock_availability").get("text"),
                "price": product.get("prices").get("price"),
                "regular_price": product.get("prices").get("regular_price"),
                "sale_price": product.get("prices").get("sale_price"),
                "currency_symbol": product.get("prices").get("currency_symbol"),
                "url": product.get("permalink"),
            }
            for product in products
        ]

    def _fetch_page_products(self, page):
        exceptions = []
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    self.url.format(page=page),
                    headers=self.headers,
                )

                if response.status_code != 200:
                    raise BaseException(
                        f"Error on fetching page: {page} | status code: {response.status_code} on {attempt}/{self.total_attempts} attempt."
                    )

                return {
                    "total_products": response.headers.get("X-WP-Total"),
                    "total_pages": response.headers.get("X-WP-TotalPages"),
                    "products": self._clean_products(products=response.json()),
                }
            except Exception as e:
                exceptions.append(e)
                time.sleep(0.1)
        raise BaseException(exceptions)
