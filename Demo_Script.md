# Demo Script — District 9 Inventory App Phase 2

## Step 1 — Login as Manager

**Action:** Enter username `owner`, password `owner123`, click Login.

- Phase 1 stored passwords as plain text — the professor flagged this as a security weakness
- Phase 2 hashes every password with SHA-256 using Python's built-in `hashlib` (no external library needed)
- When you log in, the submitted string is hashed and the hash is compared to what's stored — the plaintext is never saved anywhere
- This was a direct response to professor feedback, not a bonus addition

**Why this matters for the rubric:** Demonstrates awareness of Phase 1 feedback and a concrete fix.

---

## Step 2 — Show the File Structure (brief, verbal)

**Action:** Briefly mention the four files in `services/` while on screen.


- Why separate files? **Single Responsibility** — each file has exactly one job, so bugs are easier to isolate and fix
- `data_store.py` — only reads and writes JSON, nothing else
- `auth_service.py` — only handles login and registration, keeps that logic out of the UI entirely
- `product_service.py` — owns all inventory CRUD and sale logging
- `ai_assistant.py` — only makes the OpenAI API call
- `Phase_2.py` — only builds the Streamlit interface; it calls the services but doesn't contain business logic

**Why this matters for the rubric:** Demonstrates layered architecture and OOP design.

---

## Step 3 — Inventory Tab: Add a Product

**Action:** Go to Inventory tab → fill in Name, Category, Price, Quantity → click Add Product.


- Products are saved to `data/products.json` automatically
- The new product ID is generated with `max(existing_ids) + 1`, not `len(list)`
- If you use `len()` and delete a record, the count drops and the next ID can collide with a deleted one
- `max() + 1` always produces a unique ID regardless of how many deletions have happened

**Expected result:** New product appears in the table below the form.

---

## Step 4 — Inventory Tab: Edit a Product

**Action:** Click Edit on any product → change the price → click Save.


- Phase 1 created a separate session state flag for every product row on every page load
- When the page re-rendered, those old keys lingered and caused stale widget bugs — edit forms would reopen unexpectedly
- Phase 2 uses a single `editing_product_id` key in session state instead
- Only one product can be in edit mode at a time, and the key resets cleanly on save or cancel
- Fewer keys = less state to go stale

**Expected result:** Updated price shows in the table immediately.

---

## Step 5 — Log a Sale

**Action:** Go to Log Sale tab → choose a product → enter quantity → click Log Sale.


- The sale total is calculated inside `product_service.log_sale()`, on the service layer
- It uses the price stored in `products.json`, not any value from the UI
- The UI only sends the product ID, quantity, and the logged-in employee's username
- This means the UI cannot manipulate the price or total — the service layer is the single source of truth

**Expected result:** Success message, quantity decremented in inventory.

---

## Step 6 — View Sales History

**Action:** Go to Sales History tab.


- Every sale record includes: a UUID, UTC timestamp, product name, unit price at time of sale, quantity, computed total, and the employee who made the sale
- The unit price is snapshotted at sale time, so the record stays accurate even if the product price changes later
- All records persist in `data/sales.json` — nothing is session-only

**Expected result:** Table showing all logged sales.

---

## Step 7 — Low Stock Alert

**Action:** Stay in Inventory tab or check the sidebar.


- Any product with a quantity of 5 or below triggers a low-stock warning
- This is calculated in `product_service.get_low_stock()` on the service layer, not hardcoded in the UI
- The manager can spot reorder needs at a glance without scanning the full inventory table

**Expected result:** Warning banner or highlighted row for any low-stock item.

---

## Step 8 — AI Assistant (Manager)

**Action:** Go to AI Assistant tab → type: *"Which product has the lowest stock right now?"*


- **What's the AI system message for?** It injects the live contents of `products.json` and `sales.json` into the prompt before the conversation starts
- Without this, the model would only have general knowledge — it couldn't answer questions about our specific store
- With it, the model sees the real product names, prices, and stock levels and answers accordingly
- Manager role gets both inventory and sales context; associate role gets inventory only
- The AI is powered by `gpt-3.5-turbo` via the OpenAI API — not a hardcoded response

**Expected result:** The AI names the correct low-stock product from the live data.

Follow-up question to ask live: *"What was our total revenue this week?"*

---

## Step 9 — User Management (Register + Delete)

**Action:** Go to User Management tab → register a new associate account → then delete it.


- Registration validates for duplicate usernames and enforces a minimum password length before saving
- **What does AuthService do?** It handles all login validation and user registration — that logic lives in `auth_service.py`, completely separate from the UI
- Deletion uses a two-step confirmation to prevent accidental removal
- There's a last-manager guard built into `AuthService.delete_user()` — if only one manager account exists, deletion is blocked
- This prevents the app from ever being permanently locked out

**Expected result:** New user appears in the list, confirm prompt appears on delete, user is removed.

---

## Step 10 — Login as Associate

**Action:** Log out → log in as `employee` / `emp123`.


- Associates see a restricted dashboard — inventory browsing, sale logging, and the AI assistant are available
- User Management and the full Sales History report are not visible or accessible
- Role-based access is enforced in `Phase_2.py` by checking `st.session_state.role` on each page render
- There is no client-side trick to bypass this — the role is set on the server at login and never exposed to the UI as an editable value

**Expected result:** User Management and full Sales History tabs are not visible.

---

## Step 11 — AI Assistant (Associate)

**Action:** Go to AI Assistant tab → type: *"Do we have any size medium hoodies in stock?"*


- The associate's AI assistant receives inventory context only — no sales data is injected
- This limits it to product-level questions, which is all a floor employee actually needs
- It's a deliberate design choice: associates don't need revenue figures, so the prompt doesn't include them