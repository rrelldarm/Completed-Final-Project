# Individual Final Report

**Student Name:** Darrell Darmawan
**Team Members:** Solo Project
**Project Name:** District 9 — Clothing Store Inventory Management System
**Course:** MISY350-010 — Business Application Development

---

## My Role in the Team

As the sole developer, I was responsible for the entire project — including the data layer, business logic, authentication, AI integration, and all Streamlit UI pages for both user roles. I designed the JSON data structures, wrote every Python module, and made all architectural decisions for both Phase 1 and Phase 2.

---

## 1. Phase 1 Contribution Summary

In Phase 1, I built a single-file Streamlit application (`Phase_1.py`) for a fictional clothing store called District 9. The app included:

- A login and registration system with session state management and role-based routing
- Two role-specific dashboards: **Store Manager** and **Sales Associate**
- Full product CRUD (create, read, update, delete) for the Store Manager, with changes saved to `products.json`
- A sales logging feature for the Sales Associate that decremented stock in real time
- A user management tab allowing the Store Manager to view and delete accounts
- A simulated "Inventory Assistant" tab for the Sales Associate using hardcoded keyword matching
- Demo credentials seeded into `users.json` on first run

One issue I encountered in Phase 1 was that editing a product required a separate session state flag per product (e.g., `st.session_state["editing_P001"]`), which created dozens of dynamic keys and caused stale widget behavior when switching between products.

---

## 2. Phase 1 Issues Identified

Based on instructor feedback, team testing, and self-review:

- **Stale widget behavior** — per-product `editing_{id}` session flags scattered throughout the code caused UI state to persist unexpectedly when switching between products
- **ID generation collision risk** — new product IDs were generated using `f"P{len(products)+1}"`, which could produce duplicate IDs if a product was deleted and re-added
- **Plaintext password storage** — user passwords were written directly to `users.json` with no hashing
- **No delete confirmation** — clicking "Delete" on a product or user immediately removed the record with no second confirmation step
- **Fake AI assistant** — the "Inventory Assistant" used hardcoded `if/elif` keyword matching instead of a real OpenAI connection
- **No sales history** — sales decremented stock correctly but no record of the transaction was saved anywhere
- **Mixed responsibilities** — data loading, business logic, and UI rendering were all in one 550-line file with no separation of concerns
- **Repeated load/save calls during render** — `load_products()` was called inside loops during page rendering, causing redundant file reads

---

## 3. Phase 2 Refactoring Report — Service Layer

**What I refactored:** The product management and data access logic

### Original Code (Phase 1 — mixed into the UI)

```python
# Called directly inside a Streamlit button handler
if st.button("Confirm Sale", ...):
    current_product["stock"] -= quantity
    save_products(products_data)
    st.success(f"Sale logged! {quantity}x {selected_product_name} sold for ${total_sale:.2f}")
    st.rerun()
```

**The issue:** The stock decrement, file write, and UI response were all happening inside the same button block. There was no validation that quantity was within stock bounds at the time of the call, no sale record being saved, and the total was computed in the UI layer rather than server-side. If this logic was needed elsewhere, it would have to be duplicated.

### Refactored Code (Phase 2 — `services/product_service.py`)

```python
def log_sale(self, product_id: str, quantity: int, employee_username: str) -> tuple[bool, dict | str]:
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

    product["stock"] -= quantity
    self.products.save(data)

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
```

The UI in `Phase_2.py` now only calls:

```python
ok, result = product_svc.log_sale(selected_id, int(quantity), st.session_state.current_user["username"])
```

**The result:** The UI has no knowledge of how a sale is processed. It only receives a success/failure signal and a result to display. `unit_price` and `total` are always computed server-side from the live product record, making it impossible for the UI to pass incorrect values.

**Why the new version is better:** The business rule — "a sale must deduct stock, compute the total server-side, and persist a full sale record" — now lives in exactly one place. If the logic ever needs to change, there is only one function to update. This is the Single Responsibility Principle in practice.

---

## 4. What I Learned

**Phase 1:**
- Streamlit reruns the entire script from top to bottom on every interaction — understanding this is essential to avoiding stale session state
- JSON files work well as a lightweight persistence layer for small apps, but every write must be done carefully to avoid overwriting valid data
- Hardcoding responses in an "AI assistant" is easy to build but immediately obvious as fake — real value requires an actual API connection

**Phase 2:**
- Separating code into layers (data, service, UI) makes each piece easier to test and reason about independently — when a bug occurs, the file structure tells you exactly where to look
- Hashing passwords is a one-line change (`hashlib.sha256`) that eliminates a significant security weakness — small effort, meaningful improvement
- Prompt engineering matters — injecting live `products.json` as a system message grounds the AI in real data and prevents hallucinated responses

**Full Project:**
- Planning architecture before writing code (deciding what classes exist and what they own) saves significant refactoring time later
- The difference between a working app and a well-structured app is not visible to the end user, but it determines how maintainable the code is as it grows
- AI tools are most useful when you understand the goal well enough to evaluate the output — they accelerate implementation but require judgment to use effectively
