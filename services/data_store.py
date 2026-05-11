import json
import hashlib
from pathlib import Path

# ── File paths ────────────────────────────────────────────────────────────────
DATA_DIR      = Path("data")
USERS_FILE    = DATA_DIR / "users.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
SALES_FILE    = DATA_DIR / "sales.json"
CHAT_LOG_FILE = DATA_DIR / "chat_logs.json"

ROLE_OWNER    = "Store Manager"
ROLE_EMPLOYEE = "Sales Associate"


def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_data_files() -> None:
    """Create the data directory and seed JSON files if they don't exist yet."""
    DATA_DIR.mkdir(exist_ok=True)

    # ── users.json ────────────────────────────────────────────────────────────
    if not USERS_FILE.exists():
        default_users = {
            "users": [
                {
                    "id": "owner1",
                    "username": "owner",
                    "password": hash_password("owner123"),
                    "role": ROLE_OWNER,
                    "email": "owner@shop.com",
                },
                {
                    "id": "emp1",
                    "username": "employee",
                    "password": hash_password("emp123"),
                    "role": ROLE_EMPLOYEE,
                    "email": "emp@shop.com",
                },
            ]
        }
        with USERS_FILE.open("w") as f:
            json.dump(default_users, f, indent=2)

    # ── products.json ─────────────────────────────────────────────────────────
    if not PRODUCTS_FILE.exists():
        default_products = {
            "products": [
                {
                    "id": "P001",
                    "name": "Cropped Blank Hoodie",
                    "description": "Comfortable cropped blank hoodie, versatile wardrobe essential",
                    "price": 45.99,
                    "stock": 12,
                    "category": "Hoodies",
                },
                {
                    "id": "P002",
                    "name": "Baggy Flared Boot Cut Jeans",
                    "description": "Trendy baggy flared boot cut jeans with vintage wash",
                    "price": 80.99,
                    "stock": 4,
                    "category": "Jeans",
                },
                {
                    "id": "P003",
                    "name": "925 Silver Statement Ring",
                    "description": "Sterling silver 925 statement ring with bold design",
                    "price": 55.99,
                    "stock": 2,
                    "category": "Accessories",
                },
                {
                    "id": "P004",
                    "name": "Blank Oversized T-Shirt",
                    "description": "Oversized blank t-shirt perfect for layering or casual wear",
                    "price": 35.99,
                    "stock": 18,
                    "category": "T-Shirts",
                },
                {
                    "id": "P005",
                    "name": "Faded Washed Leather Jacket",
                    "description": "Premium faded washed leather jacket with vintage appeal",
                    "price": 170.99,
                    "stock": 5,
                    "category": "Jackets",
                },
            ]
        }
        with PRODUCTS_FILE.open("w") as f:
            json.dump(default_products, f, indent=2)

    # ── sales.json ────────────────────────────────────────────────────────────
    if not SALES_FILE.exists():
        with SALES_FILE.open("w") as f:
            json.dump([], f, indent=2)

    # ── chat_logs.json ────────────────────────────────────────────────────────
    if not CHAT_LOG_FILE.exists():
        with CHAT_LOG_FILE.open("w") as f:
            json.dump([], f, indent=2)


# ── Data store classes ────────────────────────────────────────────────────────

class UserStore:
    """Responsible only for reading and writing users.json."""

    def __init__(self):
        self.filepath = USERS_FILE

    def load(self) -> dict:
        with self.filepath.open("r") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with self.filepath.open("w") as f:
            json.dump(data, f, indent=2)

    def find_by_username(self, username: str) -> dict | None:
        for user in self.load()["users"]:
            if user["username"] == username:
                return user
        return None

    def find_by_email(self, email: str) -> dict | None:
        for user in self.load()["users"]:
            if user["email"] == email:
                return user
        return None


class ProductStore:
    """Responsible only for reading and writing products.json."""

    def __init__(self):
        self.filepath = PRODUCTS_FILE

    def load(self) -> dict:
        with self.filepath.open("r") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with self.filepath.open("w") as f:
            json.dump(data, f, indent=2)

    def find_by_id(self, product_id: str) -> dict | None:
        for p in self.load()["products"]:
            if p["id"] == product_id:
                return p
        return None

    def as_string(self) -> str:
        """Return the full product list as a formatted JSON string for AI context."""
        return json.dumps(self.load(), indent=2)


class SalesStore:
    """Responsible only for reading and writing sales.json."""

    def __init__(self):
        self.filepath = SALES_FILE

    def load(self) -> list:
        if not self.filepath.exists():
            return []
        with self.filepath.open("r") as f:
            return json.load(f)

    def save(self, records: list) -> None:
        with self.filepath.open("w") as f:
            json.dump(records, f, indent=2)

    def as_string(self) -> str:
        """Return all sales as a formatted JSON string for AI context."""
        return json.dumps(self.load(), indent=2)


class ChatLogStore:
    """Responsible only for reading and writing chat_logs.json."""

    def __init__(self):
        self.filepath = CHAT_LOG_FILE

    def load(self) -> list:
        if not self.filepath.exists():
            return []
        with self.filepath.open("r") as f:
            return json.load(f)

    def save(self, logs: list) -> None:
        with self.filepath.open("w") as f:
            json.dump(logs, f, indent=2)
