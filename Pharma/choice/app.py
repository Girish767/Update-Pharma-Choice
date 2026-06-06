from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pharma_choice_secret_key_2026'
DB = os.path.join(os.path.dirname(__file__), 'pharma.db')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS drug (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            stock INTEGER DEFAULT 0,
            description TEXT,
            updated_date TEXT,
            FOREIGN KEY(category_id) REFERENCES category(id)
        );
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            gender TEXT,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            drug_id INTEGER,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(customer_id) REFERENCES customer(id),
            FOREIGN KEY(drug_id) REFERENCES drug(id)
        );
    ''')
    # Seed only if empty
    conn.execute("INSERT OR IGNORE INTO admin(username, password) VALUES('admin','admin123')")
    for cat in ['Antibiotics','Painkillers','Vitamins & Supplements','Cold & Flu','Diabetes Care','Cardiac Care','Skin Care','Gastro Care','Eye & Ear','First Aid']:
        conn.execute("INSERT OR IGNORE INTO category(name) VALUES(?)", (cat,))
    if conn.execute('SELECT COUNT(*) FROM drug').fetchone()[0] == 0:
        drugs = [
            # Antibiotics (cat 1)
            ('Amoxicillin 500mg', 1, 85.0, 5.0, 120, 'Broad-spectrum antibiotic for bacterial infections', '2026-04-01'),
            ('Azithromycin 500mg', 1, 120.0, 8.0, 80, 'Macrolide antibiotic for respiratory & skin infections', '2026-04-01'),
            ('Ciprofloxacin 500mg', 1, 95.0, 6.0, 60, 'Fluoroquinolone for urinary tract infections', '2026-04-01'),
            ('Doxycycline 100mg', 1, 70.0, 4.0, 50, 'Tetracycline antibiotic for chest and skin infections', '2026-04-01'),
            # Painkillers (cat 2)
            ('Paracetamol 500mg', 2, 10.0, 2.0, 250, 'Relieves fever and mild-to-moderate pain', '2026-04-01'),
            ('Ibuprofen 400mg', 2, 25.0, 3.0, 150, 'Anti-inflammatory for pain and fever', '2026-04-01'),
            ('Diclofenac 50mg', 2, 30.0, 5.0, 90, 'NSAID for joint pain and arthritis', '2026-04-01'),
            ('Tramadol 50mg', 2, 65.0, 0.0, 40, 'For moderate to severe pain relief', '2026-04-01'),
            ('Aspirin 75mg', 2, 18.0, 10.0, 200, 'Low-dose aspirin for pain and heart protection', '2026-04-01'),
            # Vitamins (cat 3)
            ('Vitamin C 500mg', 3, 40.0, 0.0, 300, 'Immunity booster and antioxidant', '2026-04-01'),
            ('Vitamin D3 60000 IU', 3, 55.0, 5.0, 200, 'Weekly dose for Vitamin D deficiency', '2026-04-01'),
            ('Vitamin B12 500mcg', 3, 45.0, 0.0, 180, 'For nerve health and energy metabolism', '2026-04-01'),
            ('Multivitamin Daily', 3, 120.0, 10.0, 250, 'Complete daily nutrition with 23 vitamins & minerals', '2026-04-01'),
            ('Calcium + D3 Tablet', 3, 85.0, 5.0, 150, 'Bone strength and calcium supplement', '2026-04-01'),
            ('Zinc 50mg', 3, 35.0, 0.0, 120, 'Immunity and wound healing support', '2026-04-01'),
            # Cold & Flu (cat 4)
            ('Vicks VapoRub 50g', 4, 85.0, 5.0, 100, 'Relief from blocked nose and chest congestion', '2026-04-01'),
            ('Cetirizine 10mg', 4, 12.0, 0.0, 180, 'Antihistamine for allergies and cold symptoms', '2026-04-01'),
            ('Levocetirizine 5mg', 4, 18.0, 5.0, 120, 'Non-drowsy antihistamine for allergic rhinitis', '2026-04-01'),
            ('Sinarest Tablet', 4, 22.0, 3.0, 90, 'Relieves cold, sinus, and headache', '2026-04-01'),
            ('Ambroxol Syrup 100ml', 4, 45.0, 0.0, 70, 'Cough expectorant for productive cough', '2026-04-01'),
            # Diabetes (cat 5)
            ('Metformin 500mg', 5, 60.0, 4.0, 150, 'First-line treatment for Type 2 Diabetes', '2026-04-01'),
            ('Glimepiride 2mg', 5, 75.0, 6.0, 80, 'Sulfonylurea for blood sugar control', '2026-04-01'),
            ('Januvia (Sitagliptin) 100mg', 5, 280.0, 8.0, 40, 'DPP-4 inhibitor for Type 2 Diabetes', '2026-04-01'),
            ('Insulin Glargine 100U/ml', 5, 650.0, 5.0, 30, 'Long-acting basal insulin pen', '2026-04-01'),
            # Cardiac (cat 6)
            ('Atorvastatin 10mg', 6, 55.0, 7.0, 120, 'Statin for cholesterol management', '2026-04-01'),
            ('Amlodipine 5mg', 6, 40.0, 5.0, 100, 'Calcium channel blocker for hypertension', '2026-04-01'),
            ('Losartan 50mg', 6, 65.0, 6.0, 80, 'ARB for high blood pressure and kidney protection', '2026-04-01'),
            ('Clopidogrel 75mg', 6, 90.0, 8.0, 60, 'Antiplatelet for heart attack prevention', '2026-04-01'),
            # Skin Care (cat 7)
            ('Clotrimazole Cream 30g', 7, 55.0, 5.0, 80, 'Antifungal cream for ringworm and athletes foot', '2026-04-01'),
            ('Betadine Ointment 20g', 7, 75.0, 0.0, 60, 'Antiseptic for wounds and minor burns', '2026-04-01'),
            ('Calamine Lotion 100ml', 7, 45.0, 0.0, 90, 'Soothes itchy rashes and insect bites', '2026-04-01'),
            # Gastro (cat 8)
            ('Omeprazole 20mg', 8, 35.0, 5.0, 200, 'PPI for acidity, GERD and ulcers', '2026-04-01'),
            ('Ranitidine 150mg', 8, 20.0, 2.0, 150, 'H2 blocker for heartburn relief', '2026-04-01'),
            ('ORS Sachet (Orange)', 8, 8.0, 0.0, 300, 'Oral rehydration salts for diarrhoea', '2026-04-01'),
            ('Domperidone 10mg', 8, 25.0, 4.0, 120, 'For nausea, vomiting and bloating', '2026-04-01'),
            # Eye & Ear (cat 9)
            ('Optive Eye Drops 15ml', 9, 95.0, 5.0, 60, 'Lubricating drops for dry eyes', '2026-04-01'),
            ('Ciprofloxacin Eye Drops', 9, 45.0, 0.0, 50, 'Antibiotic eye drops for eye infections', '2026-04-01'),
            ('Otrivin Nasal Spray', 9, 110.0, 8.0, 70, 'Decongestant nasal spray for blocked nose', '2026-04-01'),
            # First Aid (cat 10)
            ('Band-Aid Flexible Pack 30', 10, 65.0, 5.0, 150, 'Flexible fabric bandages for cuts and scrapes', '2026-04-01'),
            ('Savlon Antiseptic 500ml', 10, 120.0, 10.0, 80, 'Antiseptic liquid for cleaning wounds', '2026-04-01'),
            ('Burnol Cream 20g', 10, 55.0, 0.0, 60, 'Burn relief cream for minor burns and scalds', '2026-04-01'),
        ]
        for d in drugs:
            conn.execute('INSERT INTO drug(name,category_id,price,discount,stock,description,updated_date) VALUES(?,?,?,?,?,?,?)', d)
    conn.commit()
    conn.close()

init_db()

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            flash('Please login as admin first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def customer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('customer_id'):
            flash('Please login first.', 'danger')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated

# ── PUBLIC ──────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    db = get_db()
    drugs = db.execute('SELECT d.*, c.name as category_name FROM drug d JOIN category c ON d.category_id=c.id LIMIT 6').fetchall()
    return render_template('home.html', drugs=drugs)

# ── ADMIN AUTH ───────────────────────────────────────────────────────────────
@app.route('/loginpage', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username','')
        password = request.form.get('password','')
        if role == 'Admin':
            db = get_db()
            admin = db.execute('SELECT * FROM admin WHERE username=? AND password=?', (username, password)).fetchone()
            if admin:
                session['admin'] = True
                session['admin_name'] = admin['username']
                return redirect(url_for('dashboard'))
            flash('Invalid admin credentials!', 'danger')
        else:
            flash('Please select Admin role.', 'warning')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route('/dashboard')
@admin_required
def dashboard():
    db = get_db()
    low_stock = db.execute('SELECT d.*, c.name as category_name FROM drug d JOIN category c ON d.category_id=c.id WHERE d.stock < 10').fetchall()
    total_drugs    = db.execute('SELECT COUNT(*) FROM drug').fetchone()[0]
    total_orders   = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_cats     = db.execute('SELECT COUNT(*) FROM category').fetchone()[0]
    total_customers= db.execute('SELECT COUNT(*) FROM customer').fetchone()[0]
    rev_row        = db.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status != 'Cancelled'").fetchone()
    total_revenue  = rev_row[0] if rev_row else 0
    return render_template('dashboard.html', low_stock=low_stock,
        total_drugs=total_drugs, total_orders=total_orders,
        total_cats=total_cats, total_customers=total_customers,
        total_revenue=total_revenue)

# ── CATEGORY ─────────────────────────────────────────────────────────────────
@app.route('/addcategory', methods=['GET','POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        if name:
            try:
                db = get_db()
                db.execute('INSERT INTO category(name) VALUES(?)', (name,))
                db.commit()
                flash(f'Category "{name}" added!', 'success')
            except:
                flash('Category already exists!', 'danger')
        else:
            flash('Name cannot be empty!', 'warning')
        return redirect(url_for('add_category'))
    return render_template('add_category.html')

@app.route('/viewcategory')
@admin_required
def view_category():
    db = get_db()
    cats = db.execute('SELECT c.*, COUNT(d.id) as drug_count FROM category c LEFT JOIN drug d ON c.id=d.category_id GROUP BY c.id ORDER BY c.name').fetchall()
    return render_template('view_category.html', categories=cats)

@app.route('/deletecategory/<int:cid>')
@admin_required
def delete_category(cid):
    db = get_db()
    db.execute('DELETE FROM category WHERE id=?', (cid,))
    db.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('view_category'))

# ── DRUGS ─────────────────────────────────────────────────────────────────────
@app.route('/adddrug', methods=['GET','POST'])
@admin_required
def add_drug():
    db = get_db()
    categories = db.execute('SELECT * FROM category ORDER BY name').fetchall()
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        cat_id   = request.form.get('category_id')
        price    = request.form.get('price')
        discount = request.form.get('discount', 0) or 0
        stock    = request.form.get('stock', 0) or 0
        desc     = request.form.get('description','').strip()
        if name and cat_id and price:
            db.execute('INSERT INTO drug(name,category_id,price,discount,stock,description,updated_date) VALUES(?,?,?,?,?,?,?)',
                (name, cat_id, float(price), float(discount), int(stock), desc, datetime.now().strftime('%Y-%m-%d')))
            db.commit()
            flash(f'Drug "{name}" added!', 'success')
            return redirect(url_for('add_drug'))
        flash('Please fill all required fields!', 'warning')
    return render_template('add_drug.html', categories=categories)

@app.route('/aviewdrugs')
@admin_required
def view_drugs():
    db = get_db()
    category_id = request.args.get('category_id','')
    search = request.args.get('search','')
    sort   = request.args.get('sort','name')
    categories = db.execute('SELECT * FROM category ORDER BY name').fetchall()
    query = 'SELECT d.*, c.name as category_name FROM drug d JOIN category c ON d.category_id=c.id WHERE 1=1'
    params = []
    if category_id:
        query += ' AND d.category_id=?'; params.append(category_id)
    if search:
        query += ' AND d.name LIKE ?'; params.append(f'%{search}%')
    valid_sorts = {'name','price','stock'}
    sort = sort if sort in valid_sorts else 'name'
    query += f' ORDER BY d.{sort}'
    drugs = db.execute(query, params).fetchall()
    return render_template('view_drugs.html', drugs=drugs, categories=categories,
                           sel_cat=category_id, search=search, sort=sort)

@app.route('/updatedrug/<int:did>', methods=['GET','POST'])
@admin_required
def update_drug(did):
    db = get_db()
    drug = db.execute('SELECT * FROM drug WHERE id=?', (did,)).fetchone()
    categories = db.execute('SELECT * FROM category ORDER BY name').fetchall()
    if not drug:
        flash('Drug not found!', 'danger')
        return redirect(url_for('view_drugs'))
    if request.method == 'POST':
        name     = request.form.get('name')
        cat_id   = request.form.get('category_id')
        price    = request.form.get('price')
        discount = request.form.get('discount', 0) or 0
        stock    = request.form.get('stock', 0) or 0
        desc     = request.form.get('description','')
        db.execute('UPDATE drug SET name=?,category_id=?,price=?,discount=?,stock=?,description=?,updated_date=? WHERE id=?',
            (name, cat_id, float(price), float(discount), int(stock), desc, datetime.now().strftime('%Y-%m-%d'), did))
        db.commit()
        flash('Drug updated!', 'success')
        return redirect(url_for('view_drugs'))
    return render_template('update_drug.html', drug=drug, categories=categories)

@app.route('/deletedrug/<int:did>')
@admin_required
def delete_drug(did):
    db = get_db()
    db.execute('DELETE FROM drug WHERE id=?', (did,))
    db.commit()
    flash('Drug deleted.', 'success')
    return redirect(url_for('view_drugs'))

# ── ORDERS (ADMIN) ────────────────────────────────────────────────────────────
@app.route('/avieworders')
@admin_required
def view_orders():
    db = get_db()
    orders = db.execute('''
        SELECT o.*, c.name as customer_name, c.email, c.phone,
               d.name as drug_name, cat.name as category_name
        FROM orders o
        JOIN customer c ON o.customer_id=c.id
        JOIN drug d ON o.drug_id=d.id
        JOIN category cat ON d.category_id=cat.id
        ORDER BY o.date DESC
    ''').fetchall()
    return render_template('view_orders.html', orders=orders)

@app.route('/updateorderstatus/<int:oid>', methods=['POST'])
@admin_required
def update_order_status(oid):
    status = request.form.get('status')
    db = get_db()
    db.execute('UPDATE orders SET status=? WHERE id=?', (status, oid))
    db.commit()
    flash('Order status updated!', 'success')
    return redirect(url_for('view_orders'))

# ── CUSTOMER AUTH ─────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        phone    = request.form.get('phone','')
        gender   = request.form.get('gender','')
        if name and email and password:
            try:
                db = get_db()
                db.execute('INSERT INTO customer(name,email,password,phone,gender) VALUES(?,?,?,?,?)',
                           (name, email, password, phone, gender))
                db.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('customer_login'))
            except:
                flash('Email already registered!', 'danger')
        else:
            flash('Please fill all required fields!', 'warning')
    return render_template('register.html')

@app.route('/customerlogin', methods=['GET','POST'])
def customer_login():
    if request.method == 'POST':
        email    = request.form.get('email','')
        password = request.form.get('password','')
        db = get_db()
        customer = db.execute('SELECT * FROM customer WHERE email=? AND password=?', (email, password)).fetchone()
        if customer:
            session['customer_id']   = customer['id']
            session['customer_name'] = customer['name']
            return redirect(url_for('shop'))
        flash('Invalid credentials!', 'danger')
    return render_template('customer_login.html')

@app.route('/customerlogout')
def customer_logout():
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    return redirect(url_for('home'))

# ── SHOP ──────────────────────────────────────────────────────────────────────
@app.route('/shop')
def shop():
    db = get_db()
    category_id = request.args.get('category_id','')
    search = request.args.get('search','')
    categories = db.execute('SELECT * FROM category ORDER BY name').fetchall()
    query = 'SELECT d.*, c.name as category_name FROM drug d JOIN category c ON d.category_id=c.id WHERE d.stock > 0'
    params = []
    if category_id:
        query += ' AND d.category_id=?'; params.append(category_id)
    if search:
        query += ' AND d.name LIKE ?'; params.append(f'%{search}%')
    query += ' ORDER BY d.name'
    drugs = db.execute(query, params).fetchall()
    return render_template('shop.html', drugs=drugs, categories=categories,
                           sel_cat=category_id, search=search)

@app.route('/placeorder/<int:did>', methods=['GET','POST'])
@customer_required
def place_order(did):
    db = get_db()
    drug = db.execute('SELECT d.*, c.name as category_name FROM drug d JOIN category c ON d.category_id=c.id WHERE d.id=?', (did,)).fetchone()
    if not drug:
        flash('Drug not found!', 'danger')
        return redirect(url_for('shop'))
    if request.method == 'POST':
        qty = int(request.form.get('qty', 1))
        if qty < 1 or qty > drug['stock']:
            flash(f'Invalid quantity. Available: {drug["stock"]}', 'danger')
            return redirect(url_for('place_order', did=did))
        # Server-side enforcement: only COD is accepted regardless of what was submitted
        payment_method = request.form.get('payment_method', 'COD').strip()
        if payment_method != 'COD':
            flash('Only Cash on Delivery is available at this time. Your order has been placed with COD.', 'warning')
            payment_method = 'COD'
        disc_price = drug['price'] - (drug['price'] * drug['discount'] / 100)
        total = round(disc_price * qty, 2)
        db.execute('INSERT INTO orders(customer_id,drug_id,qty,price,total,date,status) VALUES(?,?,?,?,?,?,?)',
            (session['customer_id'], did, qty, disc_price, total, datetime.now().strftime('%Y-%m-%d'), 'Pending'))
        db.execute('UPDATE drug SET stock=stock-? WHERE id=?', (qty, did))
        db.commit()
        flash(f'Order placed via Cash on Delivery! Total: ₹{total}', 'success')
        return redirect(url_for('my_orders'))
    discount   = drug['discount'] or 0
    disc_price = round(drug['price'] - (drug['price'] * discount / 100), 2)
    return render_template('place_order.html', drug=drug, disc_price=disc_price)

@app.route('/myorders')
@customer_required
def my_orders():
    db = get_db()
    orders = db.execute('''
        SELECT o.*, d.name as drug_name, c.name as category_name
        FROM orders o JOIN drug d ON o.drug_id=d.id JOIN category c ON d.category_id=c.id
        WHERE o.customer_id=? ORDER BY o.date DESC
    ''', (session['customer_id'],)).fetchall()
    return render_template('my_orders.html', orders=orders)

@app.route('/profile', methods=['GET','POST'])
@customer_required
def profile():
    db = get_db()
    customer = db.execute('SELECT * FROM customer WHERE id=?', (session['customer_id'],)).fetchone()
    if request.method == 'POST':
        name    = request.form.get('name','').strip()
        phone   = request.form.get('phone','')
        gender  = request.form.get('gender','')
        address = request.form.get('address','')
        db.execute('UPDATE customer SET name=?,phone=?,gender=?,address=? WHERE id=?',
                   (name, phone, gender, address, session['customer_id']))
        db.commit()
        session['customer_name'] = name
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', customer=customer)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
