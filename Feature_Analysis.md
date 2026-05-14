# Feature Analysis — District 9 Inventory App

**Author:** Darrell Darmawan
**Project:** District 9 — Clothing Store Inventory Management System
**Course:** MISY350-010 — Business Application Development
**Date:** May 10, 2026

---

## Origin Prompt

> *"Study what the District 9 app currently does. Identify current features, missing features, incomplete workflows, usability issues, and areas for improvement. This is a separate analysis from the structural analysis."*
> — Darrell Darmawan, May 10, 2026

---

## Current Features

### Authentication
- User login with SHA-256 hashed password comparison
- User registration with field validation (username length, password length, email format, duplicate checks)
- Role-based routing after login — Store Manager and Sales Associate receive different dashboards
- Logout that fully resets session state
- Demo credentials displayed on login page for grader convenience
- Seeded default accounts (`owner` / `employee`) created automatically on first run

### Store Manager Dashboard (6 tabs)

| Tab | Features |
|---|---|
| Manage Products | View all products in bordered cards; inline edit form (one open at a time); two-step delete confirmation |
| Add Product | Form with name, description, category, price, stock; validates uniqueness, price > 0, stock ≥ 1 |
| Inventory Overview | Metrics: total products, total units, inventory value, low stock count; low stock alert list |
| Sales History | Metrics: total transactions, units sold, total revenue; full sale records displayed newest-first |
| Manage Users | All user accounts with role badge; two-step delete confirmation; guards against self-delete and last-manager delete |
| AI Assistant | Full chat UI connected to OpenAI; context includes products + sales history; chat history persisted to `chat_logs.json` |

### Sales Associate Dashboard (4 tabs)

| Tab | Features |
|---|---|
| Product Catalog | Read-only product cards with color-coded stock indicators (green / yellow / red) |
| Log a Sale | Product selector filtered to in-stock items only; quantity input bounded by current stock; estimated total displayed; sale record saved to `sales.json` with full fields |
| My Sales | Personal sales history filtered by logged-in username; personal metrics (count, units, revenue) |
| AI Assistant | Full chat UI connected to OpenAI; context includes products only; chat history persisted |

### Data Persistence
- All user, product, sale, and chat records persist to JSON files across sessions
- Sale records include: `sale_id`, `timestamp`, `product_id`, `product_name`, `quantity`, `unit_price`, `total`, `employee`
- `unit_price` and `total` computed server-side — never trusted from UI input

---

## Phase 1 Features That Were Missing and Are Now Fixed

| Phase 1 Issue | Phase 2 Resolution |
|---|---|
| Fake hardcoded AI assistant | Real OpenAI `gpt-3.5-turbo` integration |
| No sales history saved | Full `sales.json` with balanced record structure |
| Plaintext passwords | SHA-256 hashing on register and login |
| Per-product `editing_{id}` session flags | Single `editing_product_id` key |
| ID generation via `len()` | Max-ID scan to prevent collisions |
| No delete confirmations | Two-step confirm for product and user deletion |
| No guard on user deletion | Cannot delete self or last Manager |
| Product validation gaps | Name uniqueness, price > 0, stock ≥ 0 enforced on add and edit |
| Repeated `load_products()` during render | Data loaded once per action via service methods |
| All logic in one file | Separated into 4 files across 3 layers |

---

## Missing Features / Incomplete Workflows

These are features that would strengthen the app but were not in scope for Phase 2:

- **No password reset or change flow** — a user cannot update their own password after registration
- **No stock replenishment workflow** — a Manager can manually edit stock in the edit form, but there is no dedicated "restock" action with logging
- **No sale filtering or search** — the Manager's Sales History tab shows all sales but has no filter by date, product, or employee
- **No category filter on catalog** — the Sales Associate product catalog shows all products with no way to filter by category
- **Chat history is shared across sessions** — all users of the same username share the same chat log; there is no per-session isolation
- **No rate-limit handling on AI calls** — if the OpenAI API returns a rate limit error or network failure, the app surfaces a raw exception rather than a friendly message

---

## Usability Issues Identified

- **Add Product form does not clear after submission** — Streamlit forms reset on submit, but a success message without navigation guidance may leave the user uncertain about next steps
- **Sales History newest-first display** — currently achieved with `reversed()` but there is no sort control for the user to change order
- **AI chat history loads all past logs on login** — for users with many past interactions, this could make the chat panel slow to initialize; there is no pagination or limit
- **No visual distinction between tabs on mobile** — tabs render horizontally and may overflow on small screens, though this is a Streamlit platform limitation

---

## Areas for Improvement

| Area | Suggestion |
|---|---|
| Error handling | Wrap OpenAI API calls in `try/except` to catch `openai.APIError`, rate limits, and network timeouts gracefully |
| Sales filtering | Add a date range or employee filter to the Manager's Sales History tab |
| Stock replenishment | Add a dedicated "Restock" action that logs the replenishment event separately from a manual stock edit |
| Chat log isolation | Scope chat logs per session or add a "Clear chat" button so users can start fresh |
| README | Add a `README.md` with setup instructions, run command, and demo credentials for first-time users and graders |
