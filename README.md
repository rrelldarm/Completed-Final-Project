# District 9 — Inventory Management App (Phase 2)

A Streamlit-based inventory and sales management system for a clothing store. Phase 2 rebuilds Phase 1 with a layered architecture, real AI assistance via OpenAI, and secure authentication.

---

## Features

- **Two roles:** Manager (owner) and Associate (employee)
- **Inventory management:** Add, edit, delete products with low-stock alerts
- **Sales recording:** Log sales and view full sales history with computed totals
- **User management:** Register and delete store accounts (manager only)
- **AI assistant:** Live OpenAI-powered chatbot with access to real inventory and sales data
- **Secure login:** SHA-256 hashed passwords, no plaintext storage

---

## Project Structure

```
Phase 2/
├── Phase_2.py                  # UI layer — all Streamlit code
├── requirements.txt
├── .env                        # Your OpenAI API key goes here (not committed)
├── .gitignore
├── .streamlit/
│   └── config.toml             # Dark theme settings
├── services/                   # Service & data layers
│   ├── auth_service.py         # Login, registration, user deletion
│   ├── product_service.py      # Inventory CRUD and sale logging
│   ├── ai_assistant.py         # OpenAI API wrapper
│   └── data_store.py           # All JSON file read/write
└── data/                       # Auto-created on first run
    ├── users.json
    ├── products.json
    ├── sales.json
    └── chat_logs.json
```

---

## Setup

### 1. Clone the repo and enter the Phase 2 folder

```bash
git clone <your-repo-url>
cd "Mid_Final Project/Phase 2"
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Open `.env` and replace the placeholder:

```
OPENAI_API_KEY="your-actual-api-key-here"
```

> The `.env` file is excluded from git via `.gitignore` — your key is never committed.

### 5. Run the app

```bash
streamlit run Phase_2.py
```

The app will open at `http://localhost:8501`. The `data/` folder and all JSON files are created automatically on first run.

---

## Demo Credentials

| Role | Username | Password |
|---|---|---|
| Manager | `owner` | `owner123` |
| Associate | `employee` | `emp123` |

---

## AI Assistant Notes

- The AI assistant is powered by `gpt-3.5-turbo` via the OpenAI API.
- The system message injects live JSON from `products.json` and `sales.json` so the model answers questions about the actual store inventory, not generic made-up data.
- Manager role receives both inventory and sales context; associate role receives inventory only.
- If no API key is set, the AI tab will display a configuration warning instead of erroring out.

---

## Phase 1 Issues Fixed

| Phase 1 Problem | Phase 2 Fix |
|---|---|
| All code in one file | Split into 4-file layered architecture |
| Plaintext passwords | SHA-256 hashing via `hashlib` |
| ID collisions after deletes | `max() + 1` ID generation |
| Sales total computed in UI | Computed in `product_service.log_sale()` |
| Stale widget state per product | Single `editing_product_id` session key |
| Fake/hardcoded AI responses | Real OpenAI API with live context |
| No delete confirmation | Two-step confirm pattern |
| No last-manager guard | Guard in `AuthService.delete_user()` |

---

## Requirements

```
streamlit
openai
python-dotenv
```

Python 3.9+ recommended.
