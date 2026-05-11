# District 9 - Phase 1

A multi-page Streamlit web application for managing District 9 clothing store inventory with role-based access control. Store Managers can manage clothing inventory while Sales Associates can view the catalog, log sales, and use an AI-powered inventory assistant.

## Project Requirements Met

### Multi-Page Application
- Built with Streamlit using session state management for navigation
- Dynamic routing based on user role (Store Manager vs Sales Associate)
- Separate dashboards for each role with distinct functionality

### User Authentication
- **Registration System**: New users can register with username, email, password, and role selection
- **Login System**: Secure login with credential validation
- **Logout Functionality**: Users can securely log out from the sidebar
- **Session State Management**: User session persists across page interactions

###  Role-Based Access & Functionality
- **Store Manager**: Full CRUD operations on clothing inventory (Create, Read, Update, Delete)
- **Sales Associate**: View-only catalog access, sales logging, and inventory assistant access

### JSON-Based Data Storage
- `data/users.json`: Stores user accounts with credentials and roles
- `data/products.json`: Stores product inventory with pricing and stock information
- Automatic file initialization with sample data on first run

### Meaningful CRUD Operations

#### **Store Manager:**
- **Create**: Add new clothing items with name, description, price, stock, and size/category
- **Read**: View all clothing inventory with detailed information
- **Update**: Edit existing item details (name, price, stock, description, category)
- **Delete**: Remove discontinued clothing items

#### **Sales Associate:**
- **Read**: View clothing catalog (read-only)
- **Logging Sales**: Records sales which automatically decrease stock
- **Inventory Assistant**: Pre-built AI responses to common inventory questions

### Design & Layout
- **Organized Containers**: Uses `st.container(border=True)` for visual separation
- **Responsive Layout**: Column-based layouts for optimal viewing
- **Visual Hierarchy**: Headers, subheaders, dividers, and color-coded status indicators
- **Intuitive Navigation**: Tabs, buttons, and sidebar organization
- **Color-Coded Stock Status**: Green (adequate) Yellow (warning) Red (critical low)
## Phase 1: Simulated AI Assistant

The Inventory Assistant includes **5 hardcoded responses** for common questions:

1. **"What items are low on stock?"** → Lists items with stock < 5
2. **"How many items in stock?"** → Displays all products with current stock levels
3. **"What is the total inventory value?"** → Calculates total value of all inventory
4. **"When do we need to restock?"** → Provides restock recommendations
5. **Other questions** → Helpful prompt for supported queries

## Getting Started

### Installation
```bash
# Install required package
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 👤 Demo Credentials

### Store Manager
- **Username**: `owner`
- **Password**: `owner123`

### Sales Associate
- **Username**: `employee`
- **Password**: `emp123`

## Data Files & Storage

Data is stored as JSON files in the `data/` directory:

```
data
users.json = User accounts
products.json = Product inventory
```

Files are auto-created on first run with demo accounts and sample products.


## User Interface Components

### Authentication Page
- Two-column layout with Login and Registration forms
- Demo credentials display
- Form validation and error messages

### Store Manager Dashboard
- **Manage Products Tab**: View, edit, and delete clothing items
- **Add Product Tab**: Create new clothing items with form inputs
- **Inventory Overview Tab**: Summary metrics and low-stock alerts

### Sales Associate Dashboard
- **View Catalog Tab**: Browse all clothing items with stock indicators
- **Log Sale Tab**: Record sales with automatic stock reduction
- **Inventory Assistant Tab**: AI-powered inventory queries


The app stores two types of objects:

**User**: `id`, `username`, `password`, `role`, `email`

**Product**: `id`, `name`, `description`, `price`, `stock`, `category`

## Security Notes

**Phase 1 Implementation**: This is a simulation with plaintext password storage for educational purposes.

### Demo Credentials (Pre-loaded)
```
Store Manager:
  Username: owner
  Password: owner123
  
Sales Associate:
  Username: employee
  Password: emp123
```

### Known Limitations:
- Passwords stored in plaintext — not secure, will use hashing in Phase 2
- File-based JSON storage (not concurrent-safe)
- Single-user per session (not designed for multi-user production use)