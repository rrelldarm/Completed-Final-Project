# Structural Analysis — District 9 Inventory App

**Author:** Darrell Darmawan
**Project:** District 9 — Clothing Store Inventory Management System
**Course:** MISY350-010 — Business Application Development
**Date:** May 10, 2026

---

## Origin Prompt

> *"Analyze the current app structure of my Phase 2 project. Identify the UI layer, service layer, data layer, models/classes, and important dependencies. Also explain what should be protected before making changes."*
> — Darrell Darmawan, May 10, 2026

---

## Project File Structure

```
Phase 2/
├── Phase_2.py                  ← UI layer (entry point)
├── services/
│   ├── __init__.py             ← Package marker
│   ├── data_store.py           ← Data layer
│   ├── auth_service.py         ← Service layer (authentication)
│   ├── product_service.py      ← Service layer (inventory + sales)
│   └── ai_assistant.py         ← Service layer (OpenAI integration)
├── data/
│   ├── users.json              ← User records
│   ├── products.json           ← Product inventory
│   ├── sales.json              ← Sale transaction history
│   └── chat_logs.json          ← AI conversation history
├── .streamlit/
│   └── config.toml             ← Theme configuration
├── .env                        ← API key (not committed)
├── .gitignore
├── requirements.txt
└── Individual_Report.md
```

---

## Layer Breakdown

### UI Layer — `Phase_2.py`

The UI layer is the Streamlit entry point. It is responsible for:

- Initializing session state defaults
- Rendering the sidebar with user info and logout
- Routing authenticated users to their role-specific dashboard
- Rendering all Streamlit widgets: tabs, forms, containers, columns, metrics, chat UI
- Calling service layer methods in response to user actions
- Displaying success/error/warning messages returned from services

**Key functions in this layer:**

| Function | Responsibility |
|---|---|
| `main()` | Entry point — routes to login or role dashboard |
| `render_sidebar()` | Sidebar with user info and logout |
| `show_login_page()` | Login and registration forms |
| `show_manager_dashboard()` | All 6 tabs for Store Manager |
| `show_associate_dashboard()` | All 4 tabs for Sales Associate |
| `show_ai_chat(role)` | Shared AI chat panel, renders for both roles |

**What this layer does NOT do:** It does not read or write JSON directly. It does not compute business logic (totals, validation, ID generation). It does not construct AI prompts.

---

### Service Layer — `services/`

The service layer contains all business logic. It is split into three classes with distinct responsibilities.

#### `AuthService` (`auth_service.py`)
Handles all user authentication and account management.

| Method | Responsibility |
|---|---|
| `authenticate(username, password)` | Compares SHA-256 hashed password, returns user dict or None |
| `register_user(username, password, email, role)` | Validates fields, checks duplicates, creates new user |
| `delete_user(user_id, current_user_id)` | Guards against self-deletion and last-manager deletion |

#### `ProductService` (`product_service.py`)
Handles all inventory CRUD and sale transactions.

| Method | Responsibility |
|---|---|
| `add_product(...)` | Validates input, checks name uniqueness, generates safe ID |
| `update_product(...)` | Validates input, checks name uniqueness excluding self |
| `delete_product(product_id)` | Removes product by ID |
| `log_sale(product_id, quantity, employee)` | Validates stock, decrements inventory, saves full sale record |
| `get_low_stock(threshold)` | Returns products with stock below threshold |
| `get_inventory_value()` | Returns sum of price × stock across all products |

#### `InventoryAssistant` (`ai_assistant.py`)
Handles OpenAI API communication.

| Method | Responsibility |
|---|---|
| `build_prompt()` | Constructs system message with product and optional sales context |
| `get_response(chat_history)` | Prepends system prompt to chat history, calls `gpt-3.5-turbo`, returns reply |

---

### Data Layer — `services/data_store.py`

The data layer is responsible only for reading and writing JSON files. It contains four store classes and two utility functions.

| Class / Function | File Managed | Key Methods |
|---|---|---|
| `UserStore` | `users.json` | `load()`, `save()`, `find_by_username()`, `find_by_email()` |
| `ProductStore` | `products.json` | `load()`, `save()`, `find_by_id()`, `as_string()` |
| `SalesStore` | `sales.json` | `load()`, `save()`, `as_string()` |
| `ChatLogStore` | `chat_logs.json` | `load()`, `save()` |
| `initialize_data_files()` | All 4 files | Seeds default data if files don't exist |
| `hash_password(password)` | — | Returns SHA-256 hex digest |

---

### Models / Classes Summary

| Class | Layer | Purpose |
|---|---|---|
| `UserStore` | Data | JSON persistence for user accounts |
| `ProductStore` | Data | JSON persistence for product inventory |
| `SalesStore` | Data | JSON persistence for sale records |
| `ChatLogStore` | Data | JSON persistence for AI chat history |
| `AuthService` | Service | Authentication and user management logic |
| `ProductService` | Service | Inventory CRUD and sale transaction logic |
| `InventoryAssistant` | Service (AI) | OpenAI prompt construction and API calls |

---

### Key Dependencies

| Dependency | Purpose |
|---|---|
| `streamlit` | UI framework |
| `openai` | OpenAI API client |
| `python-dotenv` | Loads `OPENAI_API_KEY` from `.env` |
| `hashlib` (stdlib) | SHA-256 password hashing |
| `uuid` (stdlib) | Unique sale ID generation |
| `datetime` (stdlib) | ISO 8601 timestamps on sale records |
| `pathlib` (stdlib) | File path management |
| `json` (stdlib) | JSON serialization |

---

### Dependency Flow Between Layers

```
Phase_2.py (UI)
    ├── imports AuthService      → which imports UserStore
    ├── imports ProductService   → which imports ProductStore, SalesStore
    ├── imports InventoryAssistant → which imports openai
    ├── imports UserStore, ProductStore, SalesStore, ChatLogStore directly
    └── imports initialize_data_files, hash_password (utilities)
```

The UI layer depends on the service layer. The service layer depends on the data layer. The data layer has no upward dependencies — it only uses the Python standard library.

---

## What Should Be Protected Before Making Changes

### Never modify without understanding the full impact:

1. **`initialize_data_files()`** — This seeds the default demo accounts and products. Changing the default user structure (e.g., adding a new field) requires also updating all code that reads those fields.

2. **`hash_password()`** — The hashing function must stay consistent. If this function changes, all existing password hashes in `users.json` become invalid and existing users cannot log in.

3. **`st.session_state` key names in `_DEFAULTS`** — These keys are used across all UI functions. Renaming a key in `_DEFAULTS` without updating every reference in `Phase_2.py` will break session state management.

4. **`sales.json` record structure** — The fields `sale_id`, `timestamp`, `product_id`, `product_name`, `quantity`, `unit_price`, `total`, `employee` are read by both the Manager dashboard and the AI assistant. Adding or renaming fields requires updating all consumers.

5. **`data/` folder path** — All store classes resolve paths relative to where the app is launched. The app must always be run from inside the `Phase 2/` directory.
