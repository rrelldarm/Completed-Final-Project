# Feature & UI Improvement Plan — District 9 Inventory App

**Author:** Darrell Darmawan
**Project:** District 9 — Clothing Store Inventory Management System
**Course:** MISY350-010 — Business Application Development
**Date:** May 10, 2026

---

## Origin Prompt

> *"After structural changes are complete, create a feature and UI improvement plan. Address missing features from Phase 1, UI design improvements, Streamlit layout decisions, session state handling, user action flows, and feedback messages. Each planned change should clearly state which layer it affects."*
> — Darrell Darmawan, May 10, 2026

---

## Prerequisite

This plan was created after the structural improvement plan was reviewed and the layered file structure (`data_store.py`, `auth_service.py`, `product_service.py`, `ai_assistant.py`, `Phase_2.py`) was implemented. All feature and UI changes below were built on top of that foundation.

---

## Feature Improvements

### 1. Real AI Assistant (replaces fake keyword matching)

**Phase 1 problem:** The "Inventory Assistant" used hardcoded `if/elif` keyword matching. It could not handle natural language, follow-up questions, or any query outside its predefined keywords.

**Planned change:**
- Replace with a real OpenAI `gpt-3.5-turbo` connection
- Use `st.chat_message` and `st.chat_input` for a proper chat UI instead of a single `st.text_input`
- Inject live `products.json` as a system message so the AI answers from real store data
- For Store Manager: also inject `sales.json` so the AI can answer revenue and trend questions
- Persist conversation history to `chat_logs.json` so chat survives page navigation within a session

**Layers affected:** Service layer (`ai_assistant.py`), UI layer (`Phase_2.py`), Data layer (`chat_logs.json` via `ChatLogStore`)

---

### 2. Sales History Persistence

**Phase 1 problem:** Logging a sale decremented stock in `products.json` but saved no record of the transaction. There was no way to review past sales or compute revenue.

**Planned change:**
- Add `sales.json` as a new data file
- Each sale record stores: `sale_id`, `timestamp`, `product_id`, `product_name`, `quantity`, `unit_price`, `total`, `employee`
- `unit_price` and `total` computed server-side at time of sale — never from UI input
- Store Manager gets a Sales History tab with revenue metrics and full transaction list
- Sales Associate gets a My Sales tab filtered to their own username

**Layers affected:** Service layer (`product_service.py` — `log_sale` method), Data layer (`SalesStore`), UI layer (new tabs in both dashboards)

---

### 3. Password Hashing

**Phase 1 problem:** Passwords were stored as plaintext strings in `users.json`. This is a security weakness flagged in instructor feedback.

**Planned change:**
- Hash all passwords with `hashlib.sha256` at registration time
- Compare hashed input against stored hash at login
- Default demo accounts seeded with pre-hashed passwords

**Layers affected:** Data layer (`hash_password()` utility in `data_store.py`), Service layer (`auth_service.py`)

---

### 4. Delete Confirmations

**Phase 1 problem:** Clicking "Delete" on a product or user immediately removed the record with no confirmation. This is a destructive action with no recovery path.

**Planned change:**
- First click on "Delete" sets a `confirm_delete_product_id` or `confirm_delete_user_id` session state key
- Button label changes to "Confirm ⚠️" on the next render
- Second click executes the deletion
- Clicking anywhere else (e.g., Edit on a different product) clears the confirmation state

**Layers affected:** UI layer only (`Phase_2.py` — session state and button rendering)

---

### 5. User Deletion Guards

**Phase 1 problem:** `delete_user()` had no guards. A manager could delete their own account or remove all manager accounts, locking everyone out.

**Planned change:**
- `AuthService.delete_user()` checks two conditions before deleting:
  1. The target `user_id` must not equal the `current_user_id`
  2. If the target is a Store Manager, there must be at least one other Manager remaining
- UI shows `_(you)_` label instead of a Delete button for the logged-in user's own row

**Layers affected:** Service layer (`auth_service.py`), UI layer (`Phase_2.py`)

---

### 6. Safe Product ID Generation

**Phase 1 problem:** New product IDs were generated with `f"P{len(products)+1}"`. If a product was deleted, the next product added could receive a duplicate ID.

**Planned change:**
- Scan all existing product IDs, parse the numeric suffix, find the maximum, and increment
- Result is always unique regardless of deletions

**Layers affected:** Service layer (`product_service.py` — `_next_product_id()` method)

---

## UI Improvements

### 7. Single `editing_product_id` Session Key

**Phase 1 problem:** Each product had its own `st.session_state[f"editing_{product_id}"]` flag. With 5+ products this created many dynamic keys, risked stale state, and made the session state impossible to inspect cleanly.

**Planned change:**
- Replace all per-product flags with one key: `st.session_state.editing_product_id`
- Stores the ID of the product currently being edited, or `None` if none
- Only one product edit form can be open at a time
- All session keys consolidated into a single `_DEFAULTS` dictionary initialized at app startup

**Layers affected:** UI layer only (`Phase_2.py`)

---

### 8. Login and Registration Using `st.form`

**Phase 1 problem:** Login and registration inputs were plain `st.text_input` widgets outside of forms. This meant pressing Enter did not submit the form, and widget state could persist unexpectedly across reruns.

**Planned change:**
- Wrap login inputs in `st.form("login_form")` with `st.form_submit_button`
- Wrap registration inputs in `st.form("register_form")` with `st.form_submit_button`
- Forms reset cleanly on submit and handle Enter key correctly

**Layers affected:** UI layer only (`Phase_2.py`)

---

### 9. Color-Coded Stock Indicators (Sales Associate Catalog)

**Phase 1 problem:** Stock was displayed as plain text with no visual urgency signal. An associate had to read the number to understand if a product was at risk.

**Planned change:**
- Stock ≥ 5 → `st.success` (green) — "✅ X in stock"
- Stock 1–4 → `st.warning` (yellow) — "⚠️ X — Low"
- Stock 0 → `st.error` (red) — "❌ Out of stock"

**Layers affected:** UI layer only (`Phase_2.py`)

---

### 10. Sales Associate — My Sales Tab

**Phase 1 problem:** The Sales Associate had no way to review their own sales history. After logging a sale, the record disappeared.

**Planned change:**
- Add a "My Sales" tab to the Sales Associate dashboard
- Filter `sales.json` records by the logged-in employee's username
- Display personal metrics: transaction count, units sold, personal revenue total
- Show individual sale cards (product, quantity, unit price, total, timestamp) newest-first

**Layers affected:** UI layer (`Phase_2.py`), Data layer (read from `SalesStore`)

---

### 11. Inventory Metrics for Store Manager

**Phase 1 problem:** The Inventory Overview tab showed a low stock warning list but no summary metrics. A manager had to count manually to understand the overall inventory state.

**Planned change:**
- Add four `st.metric` cards: Total Products, Total Units, Inventory Value, Low Stock Count
- Low Stock metric shows a delta label ("⚠️ Needs Attention" or "✅ All Good")
- Low stock threshold set at 5 units (consistent with Phase 1 definition)

**Layers affected:** UI layer (`Phase_2.py`), Service layer (`get_low_stock()`, `get_inventory_value()` in `product_service.py`)

---

### 12. Dark Theme (carried over from Phase 1)

**Phase 1:** A custom dark theme was defined in `.streamlit/config.toml`.

**Planned change:** Copy the same `config.toml` into the Phase 2 `.streamlit/` folder so the visual identity is consistent.

**Layers affected:** Configuration only (`.streamlit/config.toml`)

---

## Implementation Priority Order

| Priority | Change | Reason |
|---|---|---|
| 1 | Password hashing | Security baseline before anything else |
| 2 | Sales history (`sales.json`) | Required by AI assistant and both dashboards |
| 3 | Real AI assistant | Depends on sales history being in place for Manager context |
| 4 | Session state consolidation | Prerequisite for clean editing and delete confirmation UX |
| 5 | Delete confirmations + user deletion guards | Safety features |
| 6 | Safe product ID generation | Data integrity |
| 7 | Login/registration forms | UX polish |
| 8 | Stock indicators, metrics, My Sales tab | Dashboard completeness |
| 9 | Dark theme | Visual consistency |
