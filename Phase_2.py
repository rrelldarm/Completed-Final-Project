import os
import streamlit as st
from dotenv import load_dotenv

from services.data_store import (
    initialize_data_files,
    UserStore,
    ProductStore,
    SalesStore,
    ChatLogStore,
)
from services.auth_service import AuthService, ROLE_OWNER, ROLE_EMPLOYEE
from services.product_service import ProductService
from services.ai_assistant import InventoryAssistant

# ── Bootstrap ─────────────────────────────────────────────────────────────────
load_dotenv()
initialize_data_files()

st.set_page_config(
    page_title="District 9",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Service objects (stateless — recreated each Streamlit run) ────────────────
user_store     = UserStore()
product_store  = ProductStore()
sales_store    = SalesStore()
chat_log_store = ChatLogStore()

auth_svc    = AuthService(user_store)
product_svc = ProductService(product_store, sales_store)

# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "authenticated":              False,
    "user_role":                  None,
    "current_user":               None,
    "editing_product_id":         None,   # single key replaces per-product flags
    "confirm_delete_product_id":  None,
    "confirm_delete_user_id":     None,
    "messages":                   None,   # AI chat history; None = not yet loaded
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Helpers ───────────────────────────────────────────────────────────────────

def _logout() -> None:
    """Reset all session state keys to their defaults."""
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("# District 9")
        st.divider()

        if st.session_state.authenticated:
            user = st.session_state.current_user
            st.markdown(f"**{user['username']}**")
            st.caption(f"Role: {st.session_state.user_role}")
            st.divider()
            if st.button("Logout", use_container_width=True):
                _logout()
                st.rerun()
        else:
            st.info("Log in to access the dashboard.")


# ── Login page ────────────────────────────────────────────────────────────────

def show_login_page() -> None:
    st.markdown("## Welcome to District 9 — Inventory System")
    st.divider()

    col_login, col_register = st.columns(2, gap="large")

    # ── Login form ────────────────────────────────────────────────────────────
    with col_login:
        st.markdown("### Login")
        with st.form("login_form"):
            username  = st.text_input("Username", placeholder="Enter your username")
            password  = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                ok, user = auth_svc.authenticate(username, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user_role     = user["role"]
                    st.session_state.current_user  = user
                    st.session_state.messages      = None  # reset chat on new login
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    # ── Register form ─────────────────────────────────────────────────────────
    with col_register:
        st.markdown("### Register")
        with st.form("register_form"):
            reg_username  = st.text_input("Username",  placeholder="Choose a username")
            reg_email     = st.text_input("Email",     placeholder="your@email.com")
            reg_password  = st.text_input("Password",  type="password", placeholder="Min. 5 characters")
            reg_role      = st.selectbox("Role", [ROLE_EMPLOYEE, ROLE_OWNER])
            reg_submitted = st.form_submit_button("Register", use_container_width=True, type="primary")

        if reg_submitted:
            if not reg_username or not reg_email or not reg_password:
                st.warning("Please fill in all fields.")
            else:
                ok, msg = auth_svc.register_user(reg_username, reg_password, reg_email, reg_role)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.divider()
    st.info(
        "**Demo Credentials** \n\n"
        "**Store Manager** → Username: `owner` | Password: `owner123` \n\n"
        "**Sales Associate** → Username: `employee` | Password: `emp123`"
    )


# ── Shared AI chat panel ──────────────────────────────────────────────────────

def show_ai_chat(role: str) -> None:
    """
    Renders the AI chat UI. Loads chat history from file on first call per session.
    Products context is always injected; sales context added for Store Manager only.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found. Add it to your .env file and restart.")
        return

    # Load chat history once per session (first time messages is None)
    if st.session_state.messages is None:
        st.session_state.messages = []
        current_username = st.session_state.current_user["username"]
        saved_logs = chat_log_store.load()

        for log in saved_logs:
            if log.get("user") == current_username:
                st.session_state.messages.append({"role": "user",      "content": log["user_message"]})
                st.session_state.messages.append({"role": "assistant",  "content": log["assistant_message"]})

        if not st.session_state.messages:
            st.session_state.messages.append({
                "role":    "assistant",
                "content": "Hi! I'm your District 9 assistant. Ask me about inventory, stock levels, or sales!",
            })

    # Render existing chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Handle new user input
    user_input = st.chat_input("Ask a question about the store...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container.chat_message("user"):
            st.markdown(user_input)

        # Build assistant with fresh data on every message
        products_ctx = product_store.as_string()
        sales_ctx    = sales_store.as_string() if role == ROLE_OWNER else ""
        bot          = InventoryAssistant(api_key=api_key, products_context=products_ctx, sales_context=sales_ctx)

        with chat_container.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = bot.get_response(st.session_state.messages)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Persist to chat_logs.json
        logs = chat_log_store.load()
        logs.append({
            "user":               st.session_state.current_user["username"],
            "user_message":       user_input,
            "assistant_message":  response,
        })
        chat_log_store.save(logs)


# ── Store Manager dashboard ───────────────────────────────────────────────────

def show_manager_dashboard() -> None:
    st.title("Store Manager Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.current_user['username']}**!")
    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Manage Products",
        "Add Product",
        "Inventory Overview",
        "Sales History",
        "Manage Users",
        "AI Assistant",
    ])

    # ── Tab 1: Manage Products ────────────────────────────────────────────────
    with tab1:
        st.subheader("Manage Products")
        products = product_store.load()["products"]

        if not products:
            st.info("No products yet. Use the **Add Product** tab to get started.")
        else:
            for product in products:
                pid = product["id"]
                with st.container(border=True):
                    col_info, col_edit, col_del = st.columns([5, 1, 1])

                    with col_info:
                        st.markdown(f"**{product['name']}** — `{pid}`")
                        st.caption(product["description"])
                        st.markdown(
                            f"Category: `{product['category']}` &nbsp;|&nbsp; "
                            f"Price: `${product['price']:.2f}` &nbsp;|&nbsp; "
                            f"Stock: `{product['stock']}`"
                        )

                    with col_edit:
                        if st.button("Edit", key=f"btn_edit_{pid}", use_container_width=True):
                            st.session_state.editing_product_id        = pid
                            st.session_state.confirm_delete_product_id = None

                    with col_del:
                        if st.session_state.confirm_delete_product_id == pid:
                            # Second click confirms deletion
                            if st.button("Confirm", key=f"btn_cfm_del_{pid}", use_container_width=True, type="primary"):
                                ok, msg = product_svc.delete_product(pid)
                                st.session_state.confirm_delete_product_id = None
                                st.session_state.editing_product_id        = None
                                if ok:
                                    st.success(msg)
                                else:
                                    st.error(msg)
                                st.rerun()
                        else:
                            if st.button("Delete", key=f"btn_del_{pid}", use_container_width=True):
                                st.session_state.confirm_delete_product_id = pid
                                st.session_state.editing_product_id        = None
                                st.rerun()

                    # Inline edit form — only one product open at a time
                    if st.session_state.editing_product_id == pid:
                        st.markdown("---")
                        with st.form(key=f"edit_form_{pid}"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                new_name  = st.text_input("Product Name", value=product["name"])
                                new_price = st.number_input("Price ($)", value=float(product["price"]), min_value=0.01, step=0.01)
                                new_stock = st.number_input("Stock",     value=int(product["stock"]),   min_value=0,    step=1)
                            with ec2:
                                new_desc = st.text_area("Description", value=product["description"])
                                new_cat  = st.text_input("Category",   value=product["category"])

                            sc, cc = st.columns(2)
                            with sc:
                                save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
                            with cc:
                                cancel = st.form_submit_button("Cancel", use_container_width=True)

                        if save:
                            ok, msg = product_svc.update_product(
                                pid, new_name, new_desc, new_cat, new_price, int(new_stock)
                            )
                            if ok:
                                st.session_state.editing_product_id = None
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                        if cancel:
                            st.session_state.editing_product_id = None
                            st.rerun()

    # ── Tab 2: Add Product ────────────────────────────────────────────────────
    with tab2:
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            c1, c2 = st.columns([2, 1])
            with c1:
                new_name  = st.text_input("Product Name", placeholder="e.g., Crew Neck Sweater")
                new_desc  = st.text_area("Description",  placeholder="Enter product details...", height=100)
                new_cat   = st.text_input("Category",    placeholder="e.g., T-Shirts, Jeans, Jackets")
            with c2:
                new_price = st.number_input("Price ($)",      value=0.01, min_value=0.01, step=0.01)
                new_stock = st.number_input("Initial Stock",  value=1,    min_value=1,    step=1)

            add_submitted = st.form_submit_button("Add Product", use_container_width=True, type="primary")

        if add_submitted:
            ok, msg = product_svc.add_product(new_name, new_desc, new_cat, new_price, int(new_stock))
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    # ── Tab 3: Inventory Overview ─────────────────────────────────────────────
    with tab3:
        st.subheader("Inventory Overview")
        products = product_store.load()["products"]

        if not products:
            st.info("No products to display.")
        else:
            total_value     = product_svc.get_inventory_value()
            low_stock_items = product_svc.get_low_stock()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Products",   len(products))
            c2.metric("Total Units",      sum(p["stock"] for p in products))
            c3.metric("Inventory Value",  f"${total_value:,.2f}")
            c4.metric(
                "Low Stock Items",
                len(low_stock_items),
                delta="Needs Attention" if low_stock_items else "All Good",
            )

            st.divider()

            if low_stock_items:
                st.warning("**Low Stock Alert** — These products need restocking:")
                for item in low_stock_items:
                    st.markdown(
                        f"- **{item['name']}** (`{item['id']}`): **{item['stock']}** units remaining"
                    )
            else:
                st.success("All products are at healthy stock levels.")

    # ── Tab 4: Sales History ──────────────────────────────────────────────────
    with tab4:
        st.subheader("Sales History")
        sales = sales_store.load()

        if not sales:
            st.info("No sales have been recorded yet.")
        else:
            total_revenue = sum(s["total"] for s in sales)
            total_units   = sum(s["quantity"] for s in sales)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Transactions", len(sales))
            c2.metric("Total Units Sold",   total_units)
            c3.metric("Total Revenue",      f"${total_revenue:,.2f}")

            st.divider()

            for sale in reversed(sales):
                with st.container(border=True):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"**{sale['product_name']}** × {sale['quantity']}")
                        st.caption(
                            f"Sold by: {sale['employee']} &nbsp;|&nbsp; {sale['timestamp']}"
                        )
                        st.markdown(
                            f"Unit price: `${sale['unit_price']:.2f}` &nbsp;|&nbsp; "
                            f"Sale ID: `{sale['sale_id']}`"
                        )
                    with col_b:
                        st.markdown(f"### ${sale['total']:.2f}")

    # ── Tab 5: Manage Users ───────────────────────────────────────────────────
    with tab5:
        st.subheader("Manage Users")
        users = user_store.load()["users"]

        if not users:
            st.info("No users found.")
        else:
            for user in users:
                uid     = user["id"]
                is_self = uid == st.session_state.current_user["id"]

                with st.container(border=True):
                    col_info, col_del = st.columns([5, 1])
                    with col_info:
                        badge = "[Manager]" if user["role"] == ROLE_OWNER else "[Associate]"
                        st.markdown(f"{badge} **{user['username']}** (`{uid}`)")
                        st.caption(f"Email: {user['email']} &nbsp;|&nbsp; Role: {user['role']}")

                    with col_del:
                        if is_self:
                            st.caption("_(you)_")
                        elif st.session_state.confirm_delete_user_id == uid:
                            if st.button("Confirm", key=f"cfm_del_user_{uid}", use_container_width=True, type="primary"):
                                ok, msg = auth_svc.delete_user(uid, st.session_state.current_user["id"])
                                st.session_state.confirm_delete_user_id = None
                                if ok:
                                    st.success(msg)
                                else:
                                    st.error(msg)
                                st.rerun()
                        else:
                            if st.button("Delete", key=f"del_user_{uid}", use_container_width=True):
                                st.session_state.confirm_delete_user_id = uid
                                st.rerun()

    # ── Tab 6: AI Assistant ───────────────────────────────────────────────────
    with tab6:
        st.subheader("AI Inventory & Sales Assistant")
        st.caption(
            "Ask me about stock levels, inventory value, revenue trends, or top-selling products."
        )
        show_ai_chat(ROLE_OWNER)


# ── Sales Associate dashboard ─────────────────────────────────────────────────

def show_associate_dashboard() -> None:
    st.title("Sales Associate Dashboard")
    st.markdown(f"Welcome, **{st.session_state.current_user['username']}**!")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Product Catalog",
        "Log a Sale",
        "My Sales",
        "AI Assistant",
    ])

    # ── Tab 1: Product Catalog ────────────────────────────────────────────────
    with tab1:
        st.subheader("Product Catalog")
        products = product_store.load()["products"]

        if not products:
            st.info("No products are available right now.")
        else:
            for product in products:
                with st.container(border=True):
                    col_info, col_stock = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"**{product['name']}** (`{product['id']}`)")
                        st.caption(product["description"])
                        st.markdown(
                            f"Price: `${product['price']:.2f}` &nbsp;|&nbsp; "
                            f"Category: `{product['category']}`"
                        )
                    with col_stock:
                        stock = product["stock"]
                        if stock >= 5:
                            st.success(f"{stock} in stock")
                        elif 1 <= stock < 5:
                            st.warning(f"{stock} — Low")
                        else:
                            st.error("Out of stock")

    # ── Tab 2: Log a Sale ─────────────────────────────────────────────────────
    with tab2:
        st.subheader("Log a Sale")
        available = [p for p in product_store.load()["products"] if p["stock"] > 0]

        if not available:
            st.warning("All products are currently out of stock.")
        else:
            with st.form("log_sale_form"):
                product_map   = {p["name"]: p["id"] for p in available}
                selected_name = st.selectbox("Select Product", list(product_map.keys()))
                selected_id   = product_map[selected_name]
                current_prod  = next(p for p in available if p["id"] == selected_id)

                col1, col2 = st.columns(2)
                with col1:
                    quantity = st.number_input(
                        "Quantity",
                        value=1,
                        min_value=1,
                        max_value=current_prod["stock"],
                        step=1,
                    )
                with col2:
                    st.metric("Estimated Total", f"${quantity * current_prod['price']:.2f}")

                sale_submitted = st.form_submit_button(
                    "Confirm Sale", use_container_width=True, type="primary"
                )

            if sale_submitted:
                ok, result = product_svc.log_sale(
                    selected_id,
                    int(quantity),
                    st.session_state.current_user["username"],
                )
                if ok:
                    st.success(
                        f"Sale recorded! &nbsp; **{result['quantity']}×** "
                        f"{result['product_name']} @ `${result['unit_price']:.2f}` "
                        f"= **${result['total']:.2f}**"
                    )
                    st.rerun()
                else:
                    st.error(result)

    # ── Tab 3: My Sales ───────────────────────────────────────────────────────
    with tab3:
        st.subheader("My Sales History")
        username = st.session_state.current_user["username"]
        my_sales = [s for s in sales_store.load() if s["employee"] == username]

        if not my_sales:
            st.info("You haven't logged any sales yet.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("My Sales",        len(my_sales))
            c2.metric("Units Sold",      sum(s["quantity"] for s in my_sales))
            c3.metric("My Total Revenue", f"${sum(s['total'] for s in my_sales):,.2f}")

            st.divider()

            for sale in reversed(my_sales):
                with st.container(border=True):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"**{sale['product_name']}** × {sale['quantity']}")
                        st.caption(sale["timestamp"])
                        st.markdown(f"Unit price: `${sale['unit_price']:.2f}`")
                    with col_b:
                        st.markdown(f"### ${sale['total']:.2f}")

    # ── Tab 4: AI Assistant ───────────────────────────────────────────────────
    with tab4:
        st.subheader("AI Inventory Assistant")
        st.caption("Ask me about stock levels, prices, low inventory, or restock suggestions.")
        show_ai_chat(ROLE_EMPLOYEE)


# ── Main entry point ──────────────────────────────────────────────────────────

def main() -> None:
    render_sidebar()

    if not st.session_state.authenticated:
        st.title("District 9")
        st.divider()
        show_login_page()

    elif st.session_state.user_role == ROLE_OWNER:
        show_manager_dashboard()

    elif st.session_state.user_role == ROLE_EMPLOYEE:
        show_associate_dashboard()


if __name__ == "__main__":
    main()
