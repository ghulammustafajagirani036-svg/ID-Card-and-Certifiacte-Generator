from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Create upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------
# STORAGE
# -------------------------
users = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'fullname': 'Administrator',
        'is_admin': True
    }
}

id_cards = {}
certificates = {}   # ✅ ADDED
next_card_id = 1
next_cert_id = 1    # ✅ ADDED


# -------------------------
# HOME
# -------------------------
@app.route('/')
def home():
    return render_template('home.html')


# -------------------------
# SIGNUP
# -------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        
        if username in users:
            flash('Username already exists!', 'error')
            return render_template('signup.html')
        
        users[username] = {
            'username': username,
            'password': password,
            'fullname': fullname,
            'is_admin': False
        }
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


# -------------------------
# LOGIN
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['fullname'] = users[username]['fullname']
            session['is_admin'] = users[username]['is_admin']
            flash(f'Welcome {users[username]["fullname"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')


# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


# -------------------------
# DASHBOARD
# -------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# -------------------------
# CREATE ID CARD
# -------------------------
@app.route('/create', methods=['GET', 'POST'])
def create():
    global next_card_id
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        photo_filename = ''
        photo = request.files.get('photo')
        if photo and photo.filename:
            photo_filename = f"{random.randint(1000,9999)}_{photo.filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        card = {
            'id': next_card_id,
            'username': session['user'],
            'full_name': request.form['full_name'],
            'father_name': request.form['father_name'],
            'cnic': request.form['cnic'],
            'dob': request.form['dob'],
            'gender': request.form['gender'],
            'course': request.form['course'],
            'nationality': request.form['nationality'],
            'address': request.form['address'],
            'phone': request.form.get('phone', ''),
            'email': request.form.get('email', ''),
            'blood_group': request.form.get('blood_group', ''),
            'class_rules': request.form.get('class_rules', ''),
            'signature_name': request.form.get('signature_name', 'Administrator'),
            'card_number': f"ID-{random.randint(1000,9999)}-{random.randint(100,999)}",
            'photo': photo_filename,
            'template_design': request.form.get('template_design', '1')
        }
        
        id_cards[next_card_id] = card
        next_card_id += 1
        
        flash('ID Card created successfully!', 'success')
        return redirect(url_for('view_card', card_id=card['id']))
    
    return render_template('create.html')


# -------------------------
# VIEW ID CARD
# -------------------------
@app.route('/view_card/<int:card_id>')
def view_card(card_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    card = id_cards.get(card_id)

    if not card:
        flash('Card not found!', 'error')
        return redirect(url_for('my_cards'))
    
    if card['username'] != session['user'] and not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('my_cards'))
    
    return render_template('id_card.html', card=card)


# -------------------------
# MY CARDS
# -------------------------
@app.route('/my_cards')
def my_cards():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_cards = [
        card for card in id_cards.values()
        if card['username'] == session['user']
    ]
    return render_template('my_cards.html', cards=user_cards)


# -------------------------
# DELETE CARD
# -------------------------
@app.route('/delete_card/<int:card_id>')
def delete_card(card_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if card_id in id_cards:
        del id_cards[card_id]
        flash('Card deleted!', 'success')
    
    return redirect(url_for('my_cards'))


# =========================================================
# 🎓 CERTIFICATE SYSTEM (ADDED FULLY)
# =========================================================

# -------------------------
# CREATE CERTIFICATE
# -------------------------
@app.route('/create_certificate', methods=['GET', 'POST'])
def create_certificate():
    global next_cert_id

    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cert = {
            'id': next_cert_id,
            'username': session['user'],
            'name': request.form['name'],
            'course': request.form['course'],
            'date': request.form['date'],
            'template': request.form['template']
        }

        certificates[next_cert_id] = cert
        next_cert_id += 1

        flash('Certificate created successfully!', 'success')
        return redirect(url_for('view_certificate', cert_id=cert['id']))

    return render_template('create_certificate.html')


# -------------------------
# VIEW CERTIFICATE
# -------------------------
@app.route('/view_certificate/<int:cert_id>')
def view_certificate(cert_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cert = certificates.get(cert_id)

    if not cert:
        flash('Certificate not found!', 'error')
        return redirect(url_for('create_certificate'))

    if cert['username'] != session['user'] and not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('create_certificate'))

    return render_template('certificate.html', cert=cert)


# -------------------------
# MY CERTIFICATES
# -------------------------
@app.route('/my_certificates')
def my_certificates():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_certs = [
        cert for cert in certificates.values()
        if cert['username'] == session['user']
    ]

    return render_template('my_certificates.html', certificates=user_certs)


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ Server Started!")
    print("📱 Open: http://127.0.0.1:5000")
    print("👑 Admin: admin / admin123")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)