import streamlit as st
import json
from pathlib import Path # For file handling and directory management 

# ROLE CONSTANTS
ROLE_OWNER = "Store Manager"
ROLE_EMPLOYEE = "Sales Associate"

# Data file locations
# Products and users are sent to JSON files in the 'data/' directory
# JSON structure:
#   users.json: {"users": [{"id", "username", "password", "role", "email"}
#   products.json: {"products": [{"id" (format: P###), "name", "description", "price", "stock", "category"}

# PAGE CONFIGURATION & SESSION STATE INIT

st.set_page_config(
    page_title="District 9",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# DATA MANAGEMENT FUNCTIONS

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
PRODUCTS_FILE = DATA_DIR / "products.json"

def initialize_data_files():
    """Create data directory and initialize JSON files if they don't exist"""
    DATA_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        default_users = {
            "users": [
                {
                    "id": "owner1",
                    "username": "owner",
                    "password": "owner123",
                    "role": ROLE_OWNER,
                    "email": "owner@shop.com"
                },
                {
                    "id": "emp1",
                    "username": "employee",
                    "password": "emp123",
                    "role": ROLE_EMPLOYEE,
                    "email": "emp@shop.com"
                }
            ]
        }
        with USERS_FILE.open("w") as f:
            json.dump(default_users, f, indent=2)
    
    # Initialize products.json
    if not PRODUCTS_FILE.exists():
        default_products = {
            "products": [
                {
                    "id": "P001",
                    "name": "Cropped Blank Hoodie",
                    "description": "Comfortable cropped blank hoodie, versatile wardrobe essential",
                    "price": 45.99,
                    "stock": 12,
                    "category": "Hoodies"
                },
                {
                    "id": "P002",
                    "name": "Baggy Flared Boot Cut Jeans",
                    "description": "Trendy baggy flared boot cut jeans with vintage wash",
                    "price": 80.99,
                    "stock": 4,
                    "category": "Jeans"
                },
                {
                    "id": "P003",
                    "name": "925 Silver Statement Ring",
                    "description": "Sterling silver 925 statement ring with bold design",
                    "price": 55.99,
                    "stock": 2,
                    "category": "Accessories"
                },
                {
                    "id": "P004",
                    "name": "Blank Oversized T-Shirt",
                    "description": "Oversized blank t-shirt perfect for layering or casual wear",
                    "price": 35.99,
                    "stock": 18,
                    "category": "T-Shirts"
                },
                {
                    "id": "P005",
                    "name": "Faded Washed Leather Jacket",
                    "description": "Premium faded washed leather jacket with vintage appeal",
                    "price": 170.99,
                    "stock": 5,
                    "category": "Jackets"
                }
            ]
        }
        with PRODUCTS_FILE.open("w") as f:
            json.dump(default_products, f, indent=2)

def load_users():
    """Load users from JSON file"""
    with USERS_FILE.open("r") as f:
        return json.load(f)

def save_users(data):
    """Save users to JSON file"""
    with USERS_FILE.open("w") as f:
        json.dump(data, f, indent=2)

def load_products():
    """Load products from JSON file"""
    with PRODUCTS_FILE.open("r") as f:
        return json.load(f)

def save_products(data):
    """Save products to JSON file"""
    with PRODUCTS_FILE.open("w") as f:
        json.dump(data, f, indent=2)


# AUTHENTICATION FUNCTIONS FOR LOGIN AND REGISTRATION

def register_user(username, password, email, role):
    """Register a new user"""
    users_data = load_users()
    
    # Input validation
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters!"
    
    if not password or len(password) < 5:
        return False, "Password must be at least 5 characters!"
    
    if "@" not in email:
        return False, "Please enter a valid email address!"
    
    # Check if username already exists
    for user in users_data["users"]:
        if user["username"] == username:
            return False, "Username already exists!"
    
    # Check if email already exists
    for user in users_data["users"]:
        if user["email"] == email:
            return False, "Email already registered!"
    
    # Create new user
    new_user = {
        "id": f"user_{len(users_data['users']) + 1}",
        "username": username,
        "password": password,
        "role": role,
        "email": email
    }
    
    users_data["users"].append(new_user)
    save_users(users_data)
    return True, "Registration successful! Please log in."

def authenticate_user(username, password):
    """Authenticate user and return user info"""
    users_data = load_users()
    
    for user in users_data["users"]:
        if user["username"] == username and user["password"] == password:
            return True, user
    
    return False, None

def delete_user(user_id):
    """Delete a user by ID"""
    users_data = load_users()
    users_data["users"] = [u for u in users_data["users"] if u["id"] != user_id]
    save_users(users_data)


# STYLING HELPER

def section_header(title):
    """Display a section header using theme styling"""
    st.subheader(title)


# PAGE: AUTHENTICATION

def show_login_page():
    """Display login/registration interface"""
    st.markdown("## Welcome to the Inventory System ##")
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### Login")
        with st.container():
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    success, user = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_role = user["role"]
                        st.session_state.current_user = user
                        st.success(f"Welcome, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                else:
                    st.warning("Please enter both username and password!")
    
    with col2:
        st.markdown("### Register")
        with st.container():
            reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
            reg_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
            reg_role = st.selectbox("Role", [ROLE_EMPLOYEE, ROLE_OWNER], key="reg_role")
            
            if st.button("Register", use_container_width=True, type="primary"):
                if reg_username and reg_email and reg_password:
                    success, message = register_user(reg_username, reg_password, reg_email, reg_role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields!")
    
    st.divider()
    
    # Demo credentials for testing login 
    st.info("""
    **Demo Credentials:**
    
    User - **Store Manager:**
    - Username: `owner`
    - Password: `owner123`
    
    User - **Sales Associate:**
    - Username: `employee`
    - Password: `emp123`
    """)


# PAGE: STORE MANAGER DASHBOARD

def show_owner_dashboard():
    """Display Store Manager dashboard"""
    st.title("Store Manager Dashboard")
    st.markdown(f"Welcome, **{st.session_state.current_user['username']}**!")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Manage Products", "Add Product", "Inventory Overview", "Manage Users"])
    
    with tab1:
        section_header("Manage Products")
        products_data = load_products()
        
        if products_data["products"]:
            # Display products with edit/delete options
            for idx, product in enumerate(products_data["products"]):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{product['name']}** (ID: {product['id']})")
                        st.caption(f"Note: {product['description']}")
                        st.markdown(f"Category: `{product['category']}` | Price: `${product['price']:.2f}` | Stock: `{product['stock']}`")
                    
                    with col2:
                        if st.button("Edit", key=f"edit_{product['id']}"):
                            st.session_state[f"editing_{product['id']}"] = True
                    
                    with col3:
                        if st.button("Delete", key=f"delete_{product['id']}"):
                            products_data["products"].pop(idx)
                            # Clear editing flag for this product
                            edit_key = f"editing_{product['id']}"
                            if st.session_state.get(edit_key):
                                del st.session_state[edit_key]
                            save_products(products_data)
                            st.success("Product deleted!")
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_{product['id']}", False):
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Product Name", value=product['name'], key=f"name_{product['id']}")
                            new_price = st.number_input("Price", value=product['price'], min_value=0.0, key=f"price_{product['id']}")
                            new_stock = st.number_input("Stock", value=product['stock'], min_value=0, key=f"stock_{product['id']}")
                        
                        with col2:
                            new_desc = st.text_area("Description", value=product['description'], key=f"desc_{product['id']}")
                            new_category = st.text_input("Category", value=product['category'], key=f"cat_{product['id']}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save Changes", key=f"save_{product['id']}", use_container_width=True):
                                product['name'] = new_name
                                product['price'] = new_price
                                product['stock'] = new_stock
                                product['description'] = new_desc
                                product['category'] = new_category
                                save_products(products_data)
                                st.session_state[f"editing_{product['id']}"] = False
                                st.success("Product updated!")
                                st.rerun()
                        
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_{product['id']}", use_container_width=True):
                                st.session_state[f"editing_{product['id']}"] = False
                                st.rerun()
        else:
            st.info("No products found. Add one to get started!")
    
    with tab2:
        section_header("Add New Product")
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                with st.container():
                    st.markdown("**Product Details**")
                    product_name = st.text_input("Product Name", placeholder="e.g., Crew Neck")
                    product_desc = st.text_area("Description", placeholder="Enter product details...", height=100)
                    product_category = st.text_input("Category", placeholder="e.g., T-Shirts, Jeans, Jackets")
            
            with col2:
                st.markdown("**Pricing & Stock**")
                product_price = st.number_input("Price ($)", value=0.0, min_value=0.0, step=0.01)
                product_stock = st.number_input("Initial Stock", value=1, min_value=1, step=1)
            
            if st.button("Add Product", use_container_width=True, type="primary"):
                if product_name and product_desc and product_category:
                    if product_price <= 0:
                        st.warning("Price must be greater than 0!")
                    elif product_stock <= 0:
                        st.warning("Stock must be at least 1!")
                    else:
                        products_data = load_products()
                        new_id = f"P{str(len(products_data['products']) + 1).zfill(3)}"
                        
                        new_product = {
                            "id": new_id,
                            "name": product_name,
                            "description": product_desc,
                            "price": product_price,
                            "stock": product_stock,
                            "category": product_category
                        }
                        
                        products_data["products"].append(new_product)
                        save_products(products_data)
                        st.success(f"OK Product '{product_name}' added successfully!")
                else:
                    st.warning("Please fill in all required fields!")
    
    with tab3:
        section_header("Inventory Overview")
        products_data = load_products()
        
        if products_data["products"]:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_products = len(products_data["products"])
                st.metric("Total Products", total_products)
            
            with col2:
                total_stock = sum(p["stock"] for p in products_data["products"])
                st.metric("Total Stock", total_stock)
            
            with col3:
                low_stock = len([p for p in products_data["products"] if p["stock"] < 5])
                st.metric("Low Stock Items", low_stock, delta="Alert" if low_stock > 0 else "OK")
            
            st.divider()
            
            # Low stock alert
            low_items = [p for p in products_data["products"] if p["stock"] < 5]
            if low_items:
                st.warning("Alert - **Low Stock!**")
                for item in low_items:
                    st.markdown(f"- **{item['name']}**: Only {item['stock']} units left")
    
    with tab4:
        section_header("Manage Users")
        users_data = load_users()
        
        if users_data["users"]:
            st.markdown("**All Users:**")
            for idx, user in enumerate(users_data["users"]):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{user['username']}** (ID: {user['id']})")
                        st.caption(f"Email: {user['email']} | Role: {user['role']}")
                    
                    with col2:
                        if st.button("Delete", key=f"delete_user_{user['id']}"):
                            delete_user(user['id'])
                            st.success("User deleted!")
                            st.rerun()
        else:
            st.info("No users found.")


# PAGE: SALES ASSOCIATE DASHBOARD


def show_employee_dashboard():
    """Display Sales Associate dashboard"""
    st.title("Sales Associate Dashboard")
    st.markdown(f"Welcome, **{st.session_state.current_user['username']}**!")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["View Catalog", "Log Sale", "Inventory Assistant"])
    
    with tab1:
        section_header("Product Catalog")
        products_data = load_products()
        
        if products_data["products"]:
            # Display products (read-only for employees)
            for product in products_data["products"]:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {product['name']} (ID: {product['id']})")
                        st.caption(product['description'])
                        st.markdown(f"Price: `${product['price']:.2f}` | Category: `{product['category']}`")
                    
                    with col2:
                        if product['stock'] >= 5:
                            st.success(f"Stock: {product['stock']}")
                        elif product['stock'] < 2:
                            st.error(f"Stock: {product['stock']} - Critical")
                        else:
                            st.warning(f"Stock: {product['stock']} - Low")
        else:
            st.info("No products available.")
    
    with tab2:
        section_header("Log a Sale")
        products_data = load_products()
        
        # Filter products with stock > 0
        available_products = [p for p in products_data["products"] if p["stock"] > 0]
        
        if available_products:
            with st.container():
                product_names = {p['name']: p['id'] for p in available_products}
                selected_product_name = st.selectbox("Select Product", product_names.keys())
                selected_product_id = product_names[selected_product_name]
                
                # Get current product
                current_product = next(p for p in products_data["products"] if p['id'] == selected_product_id)
                max_quantity = current_product["stock"]
                
                col1, col2 = st.columns(2)
                with col1:
                    quantity = st.number_input(
                        "Quantity Sold",
                        value=1,
                        min_value=1,
                        max_value=max_quantity,
                        step=1
                    )
                
                with col2:
                    total_sale = quantity * current_product["price"]
                    st.metric("Sale Amount", f"${total_sale:.2f}")
                
                if st.button("Confirm Sale", use_container_width=True, type="primary"):
                    current_product["stock"] -= quantity
                    save_products(products_data)
                    st.success(f"Sale logged! {quantity}x {selected_product_name} sold for ${total_sale:.2f}")
                    st.rerun()
        else:
            st.warning("No products available to sell. All items are out of stock.")
    
    with tab3:
        section_header("Inventory Assistant")
        st.markdown("Ask the assistant about your inventory!")
        
        products_data = load_products()
        
        # Show demo queries by default
        st.info("""
        **Demo Questions:**
        
        Try asking these questions:
        - Which items are low in stock?
        - What is the total inventory value?
        - When do we need to restock?
        - What products do we have?
        - How much is each item?
        """)
        
        query = st.text_input("What would you like to know?", placeholder="Type your question here...")
        
        if query and query.strip():  # Check for non-empty query
            # Hardcoded AI responses
            query_lower = query.strip().lower()  # Strip whitespace before processing
            
            if "low" in query_lower:
                low_items = [p for p in products_data["products"] if p["stock"] < 5]
                if low_items:
                    st.info("Note - **Low Stock Alert:**\n\nThe following items are running low:\n")
                    for item in low_items:
                        st.write(f"- **{item['name']}**: {item['stock']} units remaining")
                else:
                    st.success("All items are at good stock levels!")
                       
            elif "total value" in query_lower or "inventory value" in query_lower:
                total_value = sum(p["price"] * p["stock"] for p in products_data["products"])
                st.success(f"Money - **Total Inventory Value:** ${total_value:,.2f}")
            
            elif "restock" in query_lower or "order" in query_lower:
                st.info("**Restock Recommendation:**\n\nPlease contact your store manager regarding restocking information. (Note - Items with less than 5 units should be prioritized!)")
            
            elif "products" in query_lower or "what do we have" in query_lower or "inventory" in query_lower:
                st.info("**All Available Products:**\n")
                for product in products_data["products"]:
                    st.write(f"- **{product['name']}** (${product['price']:.2f}): {product['stock']} in stock")
            
            elif "much" in query_lower or "each item" in query_lower or "price" in query_lower:
                st.info("**Individual Product Value:**\n")
                for product in products_data["products"]:
                    item_value = product["price"] * product["stock"]
                    st.write(f"- **{product['name']}**: ${item_value:,.2f} ({product['stock']} units × ${product['price']:.2f})")
            
            else:
                st.warning("I didn't understand that. Try asking about: low stock, stock levels, inventory value, restocking, or available products.")

# MAIN APP LOGIC

def main():
    # Initialize data files
    initialize_data_files()
    
    # Basic styling for spacing and readability
    st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar logout button
    if st.session_state.authenticated:
        with st.sidebar:
            st.markdown(f"**User:** {st.session_state.current_user['username']}")
            st.markdown(f"**Role:** {st.session_state.user_role}")
            st.divider()
            
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_role = None
                st.session_state.current_user = None
                st.rerun()
    
    # Main app content
    if not st.session_state.authenticated:
        st.title("District 9")
        st.divider()
        show_login_page()
    
    elif st.session_state.user_role == ROLE_OWNER:
        show_owner_dashboard()
    
    elif st.session_state.user_role == ROLE_EMPLOYEE:
        show_employee_dashboard()

if __name__ == "__main__":
    main()
