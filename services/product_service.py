import uuid
from datetime import datetime
from services.data_store import ProductStore, SalesStore


class ProductService:
    """Responsible for inventory CRUD and sale logging."""

    def __init__(self, product_store: ProductStore, sales_store: SalesStore):
        self.products = product_store
        self.sales    = sales_store

    # ── Private helpers ───────────────────────────────────────────────────────

    def _next_product_id(self, products: list) -> str:
        """
        Generate the next product ID by scanning existing IDs for the highest
        numeric suffix, then incrementing. Avoids collisions from len()-based IDs.
        """
        existing = []
        for p in products:
            try:
                existing.append(int(p["id"][1:]))
            except (ValueError, IndexError):
                pass
        next_num = max(existing, default=0) + 1
        return f"P{str(next_num).zfill(3)}"

    # ── Product CRUD ──────────────────────────────────────────────────────────

    def add_product(
        self, name: str, description: str, category: str, price: float, stock: int
    ) -> tuple[bool, str]:
        """
        Validates input, checks name uniqueness, then adds the product.
        Returns (True, message) or (False, error_message).
        """
        if not name.strip() or not description.strip() or not category.strip():
            return False, "All text fields are required."
        if price <= 0:
            return False, "Price must be greater than $0.00."
        if stock < 1:
            return False, "Initial stock must be at least 1."

        data = self.products.load()

        if any(p["name"].lower() == name.strip().lower() for p in data["products"]):
            return False, f"A product named '{name.strip()}' already exists."

        new_id = self._next_product_id(data["products"])
        data["products"].append(
            {
                "id": new_id,
                "name": name.strip(),
                "description": description.strip(),
                "price": round(price, 2),
                "stock": stock,
                "category": category.strip(),
            }
        )
        self.products.save(data)
        return True, f"Product '{name.strip()}' (ID: {new_id}) added successfully."

    def update_product(
        self,
        product_id: str,
        name: str,
        description: str,
        category: str,
        price: float,
        stock: int,
    ) -> tuple[bool, str]:
        """
        Validates input, checks name uniqueness (excluding this product),
        then updates the product record.
        Returns (True, message) or (False, error_message).
        """
        if not name.strip() or not description.strip() or not category.strip():
            return False, "All text fields are required."
        if price <= 0:
            return False, "Price must be greater than $0.00."
        if stock < 0:
            return False, "Stock cannot be negative."

        data = self.products.load()

        # Name uniqueness check — exclude the product currently being edited
        if any(
            p["name"].lower() == name.strip().lower() and p["id"] != product_id
            for p in data["products"]
        ):
            return False, f"Another product named '{name.strip()}' already exists."

        for p in data["products"]:
            if p["id"] == product_id:
                p["name"]        = name.strip()
                p["description"] = description.strip()
                p["category"]    = category.strip()
                p["price"]       = round(price, 2)
                p["stock"]       = stock
                self.products.save(data)
                return True, f"'{name.strip()}' updated successfully."

        return False, "Product not found."

    def delete_product(self, product_id: str) -> tuple[bool, str]:
        """
        Removes a product by ID.
        Returns (True, message) or (False, error_message).
        """
        data    = self.products.load()
        target  = next((p for p in data["products"] if p["id"] == product_id), None)
        if not target:
            return False, "Product not found."

        data["products"] = [p for p in data["products"] if p["id"] != product_id]
        self.products.save(data)
        return True, f"'{target['name']}' has been deleted."

    # ── Sale logging ──────────────────────────────────────────────────────────

    def log_sale(
        self, product_id: str, quantity: int, employee_username: str
    ) -> tuple[bool, dict | str]:
        """
        Validates stock, decrements inventory, and appends a sale record.
        unit_price and total are always computed server-side.
        Returns (True, sale_record_dict) or (False, error_message).
        """
        if quantity < 1:
            return False, "Quantity must be at least 1."

        data    = self.products.load()
        product = next((p for p in data["products"] if p["id"] == product_id), None)

        if not product:
            return False, "Product not found."
        if quantity > product["stock"]:
            return False, f"Only {product['stock']} unit(s) in stock."

        unit_price = product["price"]
        total      = round(quantity * unit_price, 2)

        # Decrement stock and persist immediately
        product["stock"] -= quantity
        self.products.save(data)

        # Build and persist sale record
        sale = {
            "sale_id":      f"s_{uuid.uuid4().hex[:8]}",
            "timestamp":    datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "product_id":   product_id,
            "product_name": product["name"],
            "quantity":     quantity,
            "unit_price":   unit_price,
            "total":        total,
            "employee":     employee_username,
        }
        records = self.sales.load()
        records.append(sale)
        self.sales.save(records)

        return True, sale

    # ── Inventory utilities ───────────────────────────────────────────────────

    def get_low_stock(self, threshold: int = 5) -> list:
        """Return all products with stock below the given threshold."""
        return [
            p for p in self.products.load()["products"] if p["stock"] < threshold
        ]

    def get_inventory_value(self) -> float:
        """Return total value of all inventory (price × stock, summed)."""
        return round(
            sum(p["price"] * p["stock"] for p in self.products.load()["products"]), 2
        )
