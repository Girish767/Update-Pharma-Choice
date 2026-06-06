# Pharma Choice 💊
**Online Pharmacy Management System**
Built with Python Flask | SQLite | HTML/CSS

---

## 🚀 How to Run

### 1. Install Python (if not installed)
Download from https://python.org (Python 3.8+)

### 2. Install Flask
```bash
pip install flask
```

### 3. Run the App
```bash
cd pharma_choice
python app.py
```

### 4. Open in Browser
```
http://127.0.0.1:5000
```

---

## 🔐 Login Credentials

### Admin Login
- URL: http://127.0.0.1:5000/loginpage
- Role: Admin
- Username: **admin**
- Password: **admin123**

### Customer
- Register at: http://127.0.0.1:5000/register
- Login at: http://127.0.0.1:5000/customerlogin

---

## 📋 Features

### Admin Panel
| Feature | URL |
|---|---|
| Dashboard | /dashboard |
| Add Category | /addcategory |
| View Categories | /viewcategory |
| Add Drug | /adddrug |
| View Drugs | /aviewdrugs |
| View & Update Orders | /avieworders |

### Customer Panel
| Feature | URL |
|---|---|
| Home | / |
| Shop | /shop |
| Place Order | /placeorder/<id> |
| My Orders | /myorders |
| Profile | /profile |

---

## 🗂️ Project Structure
```
pharma_choice/
├── app.py              # Main Flask application
├── pharma.db           # SQLite database (auto-created)
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── dashboard.html
    ├── add_category.html
    ├── view_category.html
    ├── add_drug.html
    ├── view_drugs.html
    ├── update_drug.html
    ├── view_orders.html
    ├── customer_login.html
    ├── register.html
    ├── shop.html
    ├── place_order.html
    ├── my_orders.html
    └── profile.html
```

---

## 🌿 Sample Data (Auto-Seeded)
- Categories: Antibiotics, Painkillers, Vitamins, Cold & Flu, Diabetes
- Drugs: Paracetamol, Vicks, Amoxicillin, Ibuprofen, Vitamin C, Metformin
