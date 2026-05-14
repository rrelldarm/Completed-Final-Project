# Structural Improvement Plan — District 9 Inventory App

**Author:** Darrell Darmawan
**Project:** District 9 — Clothing Store Inventory Management System
**Course:** MISY350-010 — Business Application Development
**Date:** May 10, 2026

---

## Origin Prompt

> *"Create a structural improvement plan for the District 9 app. The plan should focus on improving organization, layering, maintainability, and separation of concerns. The current Phase 1 app is a single file with all logic mixed together. Plan how to restructure it into separate layers before any feature or UI changes are made."*
> — Darrell Darmawan, May 10, 2026

---

## Problem Statement

Phase 1 (`Phase_1.py`) was a single 550-line file containing data access functions, authentication logic, business calculations, UI rendering, and AI keyword matching all mixed together. This created the following structural problems:

- A bug in data loading required searching through UI code to find it
- Adding a new feature required understanding the entire file before touching any part of it
- The same `load_products()` call was made multiple times during a single render cycle
- Business rules (e.g., "how a sale is processed") were scattered across button handlers rather than centralized
- Testing any one piece of logic was impossible without running the full Streamlit app

The goal of the structural improvement plan was to reorganize the same functionality into clearly separated layers **before** adding any new features.

---

## Guiding Principle

**Single Responsibility Principle** — each file and each class should have exactly one reason to change.

- If the JSON structure changes → only the data layer changes
- If a business rule changes → only the service layer changes
- If the UI layout changes → only the UI layer changes

No layer should reach into another layer's responsibilities.

---

## Planned File Structure

The following structure was planned before any Phase 2 code was written:

```
Phase 2/
├── Phase_2.py                  ← UI layer only
├── services/
│   ├── __init__.py             ← Makes services/ a Python package
│   ├── data_store.py           ← Data layer: all JSON read/write
│   ├── auth_service.py         ← Service layer: login, register, delete user
│   ├── product_service.py      ← Service layer: product CRUD, sale logging
│   └── ai_assistant.py         ← Service layer: OpenAI prompt + API call
├── data/                       ← JSON files (auto-created on first run)
├── .streamlit/config.toml      ← Theme (carried over from Phase 1)
├── .env                        ← API key (never committed)
└── requirements.txt
```

**Rationale for this structure:**
- `services/` groups all non-UI logic under one importable package
- Each file in `services/` maps to exactly one responsibility
- `Phase_2.py` becomes a coordinator — it imports and calls, never computes
- `data/` is isolated so JSON files can be inspected or replaced without touching code

---

## Planned Classes and Responsibilities

### Data Layer — `data_store.py`

| Class | Owns | Key Methods Planned |
|---|---|---|
| `UserStore` | `users.json` | `load()`, `save()`, `find_by_username()`, `find_by_email()` |
| `ProductStore` | `products.json` | `load()`, `save()`, `find_by_id()`, `as_string()` |
| `SalesStore` | `sales.json` | `load()`, `save()`, `as_string()` |
| `ChatLogStore` | `chat_logs.json` | `load()`, `save()` |

**Design decision:** Store classes are intentionally thin — they only read and write. They do not validate, compute, or filter. That belongs in the service layer.

**Additional utilities planned in this file:**
- `hash_password(password)` — SHA-256 hashing, used by auth service
- `initialize_data_files()` — seeds default data on first run

---

### Service Layer — `auth_service.py`

**Class:** `AuthService`

Planned to own all user account logic so none of it lives in UI button handlers.

| Method Planned | Purpose |
|---|---|
| `authenticate(username, password)` | Hash-compare login credentials |
| `register_user(...)` | Validate fields, check duplicates, create account |
| `delete_user(user_id, current_user_id)` | Delete with guards: no self-delete, no last-manager delete |

**Why separate from `ProductService`:** User management and product management change independently. A change to registration rules should never require touching product logic.

---

### Service Layer — `product_service.py`

**Class:** `ProductService`

Planned to own all inventory and sales logic, removing it from UI handlers entirely.

| Method Planned | Purpose |
|---|---|
| `add_product(...)` | Validate, check name uniqueness, generate safe ID, persist |
| `update_product(...)` | Validate, check uniqueness excluding self, persist |
| `delete_product(product_id)` | Remove by ID, persist |
| `log_sale(product_id, quantity, employee)` | Validate stock, decrement, compute total server-side, persist sale record |
| `get_low_stock(threshold)` | Return filtered product list |
| `get_inventory_value()` | Return computed total |

**Key design decision for `log_sale`:** The unit price and total must be computed server-side from `products.json` at the time of sale — not passed in from the UI. This prevents the UI from submitting incorrect totals and ensures historical sale records remain accurate even if the product price changes later.

**Safe ID generation plan:** Instead of `f"P{len(products)+1}"` (Phase 1), scan existing IDs for the highest numeric suffix and increment from there. This prevents duplicate IDs when products are deleted and re-added.

---

### Service Layer — `ai_assistant.py`

**Class:** `InventoryAssistant`

Planned to isolate all OpenAI interaction so the UI never constructs prompts or calls the API directly.

| Method Planned | Purpose |
|---|---|
| `build_prompt()` | Construct system message with product context; optionally include sales context for Manager role |
| `get_response(chat_history)` | Prepend system prompt to chat history, call `gpt-3.5-turbo`, return reply string |

**Role-aware context design:** The same class serves both roles. The difference is controlled by whether `sales_context` is passed at construction time — empty string for Sales Associate, full `sales.json` string for Store Manager. The class itself has no knowledge of Streamlit or roles.

---

### UI Layer — `Phase_2.py`

Planned to contain only:
- `st.` calls (widgets, layout, session state)
- Calls to service methods
- Display of return values (success/error messages, data display)

**Explicitly excluded from this file:**
- JSON file reads or writes
- Password hashing
- Business rule logic (validation, ID generation, stock math)
- AI prompt construction

**Session state plan:** Replace all scattered per-product `editing_{id}` flags with a single dictionary of named defaults (`_DEFAULTS`) initialized once at startup. This makes the full session state visible in one place and eliminates stale key accumulation.

---

## Implementation Sequence

The structural changes were planned to be implemented in this order to avoid breaking working functionality:

1. Create `services/` folder and `__init__.py`
2. Implement `data_store.py` — data layer first, as everything else depends on it
3. Implement `auth_service.py` — depends only on `UserStore`
4. Implement `product_service.py` — depends on `ProductStore` and `SalesStore`
5. Implement `ai_assistant.py` — depends only on `openai`
6. Implement `Phase_2.py` — UI layer last, wires all services together
7. Smoke-test all imports and login logic before running the full Streamlit app

**Rationale for this order:** Building bottom-up (data → service → UI) means each layer can be verified independently before the next depends on it.

---

## What This Plan Does Not Cover

Structural changes only. The following were intentionally deferred to the Feature & UI Improvement Plan:

- AI chat UI design and chat history persistence
- Sales history display for both roles
- Low stock alerts and inventory metrics
- Delete confirmation UX
- Specific validation error messages shown to users
