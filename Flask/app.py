from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file, Response
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import io
import json
import os

from utils.scraper import extract_text_from_url
from utils.llm_api import verify_claims_with_gemini
from utils.report_gen import generate_pdf

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') 
app.config['MYSQL_DB'] = 'bytehunters_db'

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, hashed_password))
            mysql.connection.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            flash('Email already exists.', 'error')
            return redirect(url_for('signup'))
        finally:
            cursor.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user_obj)
            return redirect(url_for('input_page')) 
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/input', methods=['GET', 'POST']) 
@login_required
def input_page():
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        content = request.form.get('content')
        
        text_to_analyze = ""
        if input_type == 'url':
            text_to_analyze = extract_text_from_url(content)
        else:
            text_to_analyze = content

        result_json = verify_claims_with_gemini(text_to_analyze)
        
        return render_template('results.html', 
                               result=result_json, 
                               original_content=content, 
                               input_type=input_type,
                               raw_text=text_to_analyze)

    return render_template('input.html', user=current_user)

@app.route('/save_result', methods=['POST'])
@login_required
def save_result():
    content = request.form['content']
    input_type = request.form['input_type']
    json_str = request.form['json_data']
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO verification_history (user_id, input_type, input_content, json_result)
        VALUES (%s, %s, %s, %s)
    """, (current_user.id, input_type, content, json_str))
    mysql.connection.commit()
    cursor.close()
    
    flash("Analysis saved to your dashboard!", "success")
    return redirect(url_for('dashboard'))

@app.route('/download_report', methods=['POST'])
@login_required
def download_report():
    json_str = request.form['json_data']
    data = json.loads(json_str)
    pdf_bytes = generate_pdf(data)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='ByteHunters_Report.pdf'
    )

@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM verification_history WHERE user_id = %s ORDER BY created_at DESC", (current_user.id,))
    history = cursor.fetchall()
    
    for item in history:
        if isinstance(item['json_result'], str):
            item['json_result'] = json.loads(item['json_result'])
            
    return render_template('dashboard.html', history=history)

@app.route('/delete_result/<int:report_id>', methods=['POST'])
@login_required
def delete_result(report_id):
    cursor = mysql.connection.cursor()
    
    cursor.execute("DELETE FROM verification_history WHERE id = %s AND user_id = %s", 
                   (report_id, current_user.id))
    
    mysql.connection.commit()
    cursor.close()
    
    flash("Report deleted successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)