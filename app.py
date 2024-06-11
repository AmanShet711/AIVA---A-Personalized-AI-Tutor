from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from sql import create_connection, insert_student
import re
# from transformers import BertForQuestionAnswering, BertTokenizer
# import torch
from model import extract_text_from_pdf, answer_question
import QuestionAnswer as qa

model_path = "C:/Users/prajwal mr/Music/AIVA Code/textbook_models/pytorch_model.bin"
config_path = "C:/Users/prajwal mr/Music/AIVA Code/textbook_models/config.json"
# tokenizer = BertTokenizer.from_pretrained(config_path)
# model = BertForQuestionAnswering.from_pretrained(model_path)

app = Flask(__name__)
DATABASE = "textbooks.db"

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = create_connection(DATABASE)
    return conn

# Route for the login page

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        phone_no = request.form['phone_no']
        # Query the database to check if the email and phone number combination exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor.execute("SELECT * FROM student WHERE email = ? AND phone_no = ?", (email, phone_no))
        cursor1.execute("SELECT studentname FROM student WHERE email = ? AND phone_no = ?", (email, phone_no))
        student = cursor.fetchone()
        student_name = cursor1.fetchone()
        conn.close()
        if student:
            # Redirect to dashboard if login successful
            return redirect(url_for('dashboard', student_name=student_name[0]))  # Assuming student_id is the first column
        else:
            # Return error message if login fails
            error = "Invalid email or password"
            return render_template('login.html')
    return render_template('login.html')

# Route for the registration page
def is_valid_email(email):
    # Simple regex for email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_phone(phone):
    # Simple regex for phone number validation (assuming 10 digits)
    phone_regex = r'^\d{10}$'
    return re.match(phone_regex, phone) is not None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        studentname = request.form['studentname']
        grade = request.form['grade']
        education_board = request.form['education_board']
        email = request.form['email']
        phone_no = request.form['phone_no']
        
        if not is_valid_email(email):
            error_message = 'Invalid email format.'
            return render_template('register.html', error=error_message)
        
        if not is_valid_phone(phone_no):
            error_message = 'Invalid phone number format. It should be 10 digits.'
            return render_template('register.html', error=error_message)
        
        conn = get_db_connection()
        student = (studentname, grade, education_board, email, phone_no)
        insert_student(conn, student)
        conn.close()
        # Redirect to login page after registration
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Route for the student dashboard
@app.route('/dashboard/<student_name>', methods=['GET', 'POST'])
def dashboard(student_name):
    if request.method == 'POST':
        subject = request.form.get('subject')
        question = request.form.get('question')

        if not subject or not question:
            return render_template('dashboard.html', error="Please select a subject and ask a question.", student_name=student_name)

        model_path = f"./{subject}_model2"  # Ensure your PDFs are stored in a folder named 'pdfs'
        pipeline, tokenizer = qa.load_model(model_path)
        chunks_file_path = f"{subject}_preprocessed_chunks.json"
        chunks = qa.load_chunks_from_file(chunks_file_path)
        preprocess_chunks = qa.preprocess_chunks(chunks)
        context = qa.find_relevant_chunks(preprocess_chunks, question, tokenizer)
        
        answer = qa.iterative_ask_question(pipeline, tokenizer, question, context)

        return render_template('dashboard.html', answer=answer,question=question, student_name=student_name)

    # GET request: just show the form
    return render_template('dashboard.html', student_name=student_name)

    

if __name__ == '__main__':
    app.run(debug=True)
