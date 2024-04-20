from flask import Flask, render_template, request, redirect, url_for, jsonify,session,send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mani@2002'
app.config['MYSQL_DB'] = 'placement_management_system'


mysql = MySQL(app)

# Routes
@app.route('/')
def index():
    error = request.args.get('error')
    return render_template('Home.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    role = request.json['role']

    cursor = mysql.connection.cursor()

    if role == 'admin':
        cursor.execute("SELECT * FROM admin_cred WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            # Redirect to the admin dashboard without passing the error message
            return redirect(url_for('admin_dashboard'))
    elif role == 'student':
        cursor.execute("SELECT * FROM student_cred WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        print(user)
        if user:
            session['student_id']=user[0]
            # Redirect to the student dashboard without passing the error message
            return redirect(url_for('student_dashboard'))
    cursor.close()
    # If authentication fails, return an error response with the error message in the query parameters
    return redirect(url_for('index', error='Invalid credentials. Please try again.'))

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')


@app.route('/admin_cred.html', methods=['GET', 'POST'])
def admin_credentials():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM admin_cred")
    admin_cred = cursor.fetchall()
    cursor.close()
    return render_template('admin_cred.html', admin_cred=admin_cred)
@app.route('/add_admin', methods=['POST'])
def add_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO admin_cred (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/admin/get_admin_credentials', methods=['GET'])
def get_admin_credentials():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin_cred")
        admin_credentials = cursor.fetchall()
        cursor.close()
        return jsonify(admin_credentials)
    except Exception as e:
        # If any error occurs during fetching admin credentials, return a JSON response with the error message
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_admin', methods=['POST'])
def delete_admin():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from request
        admin_id = data['admin_id']  # Get admin_id from JSON data
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM admin_cred WHERE admin_id = %s", (admin_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
        except Exception as e:
            # Handle error
            return jsonify({'success': False, 'message': str(e)})

@app.route('/update_admin/<admin_id>', methods=['POST'])
def update_admin(admin_id):
    if request.method == 'POST':
        updated_username = request.json.get('username')
        updated_password = request.json.get('password')
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE admin_cred SET username = %s, password = %s WHERE admin_id = %s", (updated_username, updated_password, admin_id))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
        except Exception as e:
            # Handle error
            return jsonify({'success': False, 'message': str(e)})
@app.route('/student_profiles.html', methods=['GET', 'POST'])
def student_profiles():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM student_details")
    student_profiles = cursor.fetchall()
    cursor.close()
    return render_template('student_profiles.html', student_profiles=student_profiles)

@app.route('/get_all_students', methods=['GET'])
def get_all_students():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_details")
        student_details = cursor.fetchall()
        cursor.close()
        # Convert tuple to list of dictionaries for JSON serialization
        student_details_list = [{
            'student_id': row[0],
            'name': row[1],
            'email': row[2],
            'phone_num': row[3],
            'backlogs': row[4],
            'cgpa': row[5],
            'department': row[6],
            'year': row[7]
        } for row in student_details]
        return jsonify(student_details_list)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/search_students', methods=['GET'])
def search_students():
    try:
        search_query = request.args.get('query')
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM student_details WHERE student_id LIKE %s OR name LIKE %s OR email LIKE %s OR phone_num LIKE %s OR backlogs LIKE %s OR cgpa LIKE %s OR department LIKE %s OR year LIKE %s"
        param = ("%" + search_query + "%",) * 8
        cursor.execute(query, param)
        student_details = cursor.fetchall()
        cursor.close()
        student_details_list = [{
            'student_id': row[0],
            'name': row[1],
            'email': row[2],
            'phone_num': row[3],
            'backlogs': row[4],
            'cgpa': row[5],
            'department': row[6],
            'year': row[7]
        } for row in student_details]
        return jsonify(student_details_list)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/add_new_student', methods=['POST'])
def add_new_student():
    if request.method == 'POST':
        try:
            # Extract data from the form
            student_id = request.form['studentId']
            name = request.form['name']
            email = request.form['email']
            phone_number = request.form['phoneNumber']
            backlogs = request.form['backlogs']
            cgpa = request.form['cgpa']
            department = request.form['department']
            year = request.form['year']

            # Insert data into the database
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO student_details (student_id, name, email, phone_num, backlogs, cgpa, department, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (student_id, name, email, phone_number, backlogs, cgpa, department, year))
            mysql.connection.commit()
            cursor.close()

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    return jsonify({'success': False, 'message': 'Method not allowed'})
@app.route('/get_departments', methods=['GET'])
def get_departments():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DISTINCT department FROM student_details")
        departments = [item[0] for item in cursor.fetchall()]
        cursor.close()
        return jsonify(departments)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_students_by_department', methods=['GET'])
def get_students_by_department():
    try:
        department = request.args.get('department')
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_details WHERE department = %s", (department,))
        student_details = cursor.fetchall()
        cursor.close()
        student_details_list = [{
            'student_id': row[0],
            'name': row[1],
            'email': row[2],
            'phone_number': row[3],
            'backlogs': row[4],
            'cgpa': row[5],
            'department': row[6],
            'year': row[7]
        } for row in student_details]
        return jsonify(student_details_list)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/update_student_profile', methods=['POST'])
def update_student_profile():
    if request.method == 'POST':
        try:
            # Extract data from the form
            student_id = request.form['updateStudentId']
            name = request.form['updateName']
            email = request.form['updateEmail']
            phone_number = request.form['updatePhoneNumber']
            backlogs = request.form['updateBacklogs']
            cgpa = request.form['updateCGPA']
            department = request.form['updateDepartment']
            year = request.form['updateYear']

            # Update data in the database
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE student_details SET name=%s, email=%s, phone_num=%s, backlogs=%s, cgpa=%s, department=%s, year=%s WHERE student_id=%s", (name, email, phone_number, backlogs, cgpa, department, year, student_id))
            mysql.connection.commit()
            cursor.close()

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/delete_student_profile', methods=['DELETE'])
def delete_student_profile():
    try:
        student_id = request.args.get('student_id')
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM student_details WHERE student_id = %s", (student_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/student_cred.html', methods=['GET', 'POST'])
def student_credentials():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM student_cred")
    student_cred = cursor.fetchall()
    cursor.close()
    return render_template('student_cred.html', student_cred=student_cred)
@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['studentId']
        username = request.form['username']
        password = request.form['password']

        # Check if the student exists in student_details table
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_details WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student is None:
            # Student does not exist, show warning message
            return jsonify({'success': False, 'message': 'Please add details of this student before creating credentials for him/her.'})

        # Student exists, proceed to add credentials
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO student_cred (student_id, username, password) VALUES (%s, %s, %s)", (student_id, username, password))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/admin/get_student_credentials', methods=['GET'])
def get_student_credentials():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_cred")
        student_credentials = cursor.fetchall()
        cursor.close()
        return jsonify(student_credentials)
    except Exception as e:
        # If any error occurs during fetching student credentials, return a JSON response with the error message
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_student', methods=['POST'])
def delete_student():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from request
        student_id = data['student_id']  # Get student_id from JSON data
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM student_cred WHERE student_id = %s", (student_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
        except Exception as e:
            # Handle error
            return jsonify({'success': False, 'message': str(e)})

@app.route('/update_student/<student_id>', methods=['POST'])
def update_student(student_id):
    if request.method == 'POST':
        updated_username = request.json.get('username')
        updated_password = request.json.get('password')
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE student_cred SET username = %s, password = %s WHERE student_id = %s", (updated_username, updated_password, student_id))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
        except Exception as e:
            # Handle error
            return jsonify({'success': False, 'message': str(e)})


@app.route('/job_notifi.html', methods=['GET', 'POST'])
def job_notification():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM job_notifi")
    job_notifi = cursor.fetchall()
    cursor.close()
    return render_template('job_notifi.html', job_notifi=job_notifi)


@app.route('/get_job_postings', methods=['GET'])
def get_job_postings():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM job_notifi")
        job_postings = [dict((cursor.description[i][0], value) \
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(job_postings)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add_job_posting', methods=['POST'])
def add_job_posting():
    if request.method == 'POST':
        title = request.json['title']
        description = request.json['description']
        skills = request.json['skills']

        # Insert the job posting into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO job_notifi (title, description, skills) VALUES (%s, %s, %s)", (title, description, skills))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/get_job_details/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM job_notifi WHERE job_id = %s", (job_id,))
        job_details = cursor.fetchone()
        cursor.close()
        return jsonify(job_details)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM job_notifi WHERE job_id = %s", (job_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/student/details')
def student_details():
    error = request.args.get('error')
    return render_template('student_details.html', skills_list=skills_list, proficiency_levels=proficiency_levels, error=error)
@app.route('/get_profile_picture')
def get_profile_picture():
    # Get the student_id of the logged-in student from the session
    if 'student_id' in session:
        student_id = session['student_id']

        # Query the database to get the picture path for the logged-in student
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT picture_path FROM profile_pictures WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()
        if result:
            picture_filename = result[0]
            # Prepend the directory structure to the filename
            picture_path = f"images/db_pictures/{picture_filename}"
            # Construct the picture URL using url_for
            picture_url = url_for('static', filename=picture_path)
            print(picture_url)
            return jsonify({'picture_path': picture_url})
        else:
            return jsonify({'error': 'Profile picture not found for the logged-in student'})
    else:
        return jsonify({'error': 'Student not logged in'})
@app.route('/delete_profile_picture', methods=['DELETE'])
def delete_profile_picture():
    if 'student_id' in session:
        student_id = session['student_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT picture_path FROM profile_pictures WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()

        if result:
            picture_filename = result[0]
            picture_path = os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\images\\db_pictures', picture_filename)

            # Delete the file from the filesystem
            if os.path.exists(picture_path):
                os.remove(picture_path)

            cursor.execute("DELETE FROM profile_pictures WHERE student_id = %s", (student_id,))
            mysql.connection.commit()

            return jsonify({'success': 'Profile picture deleted successfully'})
        else:
            return jsonify({'error': 'Profile picture not found for the logged-in student'})
    else:
        return jsonify({'error': 'Student not logged in'})
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def is_file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    student_id = session.get('student_id')
    profile_picture = request.files.get('profile-picture')

    if not profile_picture:
        return jsonify({'error': 'No file part in the request'})

    if profile_picture.filename == '':
        return jsonify({'error': 'No selected file'})

    if profile_picture and is_file_allowed(profile_picture.filename):
        filename = secure_filename(profile_picture.filename)
        filename = f"{student_id}.{filename.rsplit('.', 1)[1].lower()}"

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT picture_path FROM profile_pictures WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()

        base_dir = 'C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\images\\db_pictures'
        if result:
            existing_filename = result[0]
            existing_filepath = os.path.join(base_dir, existing_filename)
            if os.path.exists(existing_filepath):
                os.remove(existing_filepath)
            cursor.execute("UPDATE profile_pictures SET picture_path = %s WHERE student_id = %s", (filename, student_id))
        else:
            cursor.execute("INSERT INTO profile_pictures (student_id, picture_path) VALUES (%s, %s)", (student_id, filename))

        mysql.connection.commit()
        profile_picture.save(os.path.join(base_dir, filename))

        return jsonify({'success': 'Profile picture uploaded successfully'})
@app.route('/get_student_details')
def get_student_details():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM student_details WHERE student_id = %s", (session['student_id'],))
    result = cursor.fetchone()
    if result:
        # Convert result to array of dictionaries for maintaining order in JavaScript
        student_details = [
            {'key': 'Student ID', 'value': result[0]},
            {'key': 'Name', 'value': result[1]},
            {'key': 'Email', 'value': result[2]},
            {'key': 'Phone Number', 'value': result[3]},
            {'key': 'Backlogs', 'value': result[4]},
            {'key': 'CGPA', 'value': result[5]},
            {'key': 'Department', 'value': result[6]},
            {'key': 'Year', 'value': result[7]}
        ]
        return jsonify({'student_details': student_details})
    else:
        return jsonify({'error': 'Student details not found'})
@app.route('/get_personal_details')
def get_personal_details():
    if 'student_id' in session:
        student_id = session['student_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_personal_details WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()
        if result:
            personal_details = [
                {'key': 'Date of Birth', 'value': result[1]},
                {'key': "Father's Name", 'value': result[2]},
                {'key': 'Gender', 'value': result[3]},
                {'key': 'Hobbies', 'value': result[4]}
            ]
            return jsonify({'personal_details': personal_details})
        else:
            return jsonify({'personal_details': []})  # No personal details found
    else:
        return jsonify({'error': 'Student not logged in'})

@app.route('/save_personal_details', methods=['POST'])
def save_personal_details():
    if 'student_id' in session:
        student_id = session['student_id']
        date_of_birth = request.form['dateOfBirth']
        father_name = request.form['fatherName']
        gender = request.form['gender']
        hobbies = request.form['hobbies']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_personal_details WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()

        if result:
            # If personal details already exist, update them
            cursor.execute("UPDATE student_personal_details SET date_of_birth = %s, father_name = %s, gender = %s, hobbies = %s WHERE student_id = %s",
                           (date_of_birth, father_name, gender, hobbies, student_id))
        else:
            # If personal details don't exist, insert them
            cursor.execute("INSERT INTO student_personal_details (student_id, date_of_birth, father_name, gender, hobbies) VALUES (%s, %s, %s, %s, %s)",
                           (student_id, date_of_birth, father_name, gender, hobbies))
        mysql.connection.commit()
        return jsonify({'success': 'Personal details saved successfully'})
    else:
        return jsonify({'error': 'Student not logged in'})
skills_list = [
    "Python",
    "JavaScript",
    "Java",
    "C++",
    "C#",
    "Ruby",
    "Swift",
    "Kotlin",
    "TypeScript",
    "HTML5",
    "CSS3",
    "React.js",
    "Angular",
    "Vue.js",
    "Node.js",
    "Express.js",
    "RESTful APIs",
    "GraphQL",
    "iOS Development (Swift, SwiftUI)",
    "Android Development (Java, Kotlin)",
    "React Native",
    "Flutter",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Firebase",
    "Amazon Web Services (AWS)",
    "Microsoft Azure",
    "Google Cloud Platform (GCP)",
    "Docker",
    "Kubernetes",
    "Jenkins",
    "Git",
    "Continuous Integration/Continuous Deployment (CI/CD)",
    "TensorFlow",
    "PyTorch",
    "scikit-learn",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Natural Language Processing (NLP)",
    "Computer Vision",
    "Ethical Hacking",
    "Network Security",
    "Cryptography",
    "Security Information and Event Management (SIEM)",
    "Penetration Testing",
    "Scrum",
    "Kanban",
    "Agile Project Management",
    "Requirements Gathering",
    "Data Analysis",
    "Process Modeling",
    "Stakeholder Management",
    "Search Engine Optimization (SEO)",
    "Social Media Marketing",
    "Content Marketing",
    "Email Marketing",
    "Google Analytics",
    "Adobe Photoshop",
    "Adobe Illustrator",
    "Adobe InDesign",
    "Sketch",
    "Figma",
    "Adobe Premiere Pro",
    "Final Cut Pro",
    "DaVinci Resolve",
    "Adobe After Effects",
    "Verbal Communication",
    "Written Communication",
    "Presentation Skills",
    "Active Listening",
    "Prioritization",
    "Task Scheduling",
    "Goal Setting",
    "Productivity Tools (e.g., Trello, Asana)",
    "Excel (Advanced Formulas, PivotTables, Macros)",
    "Word",
    "PowerPoint",
    "Outlook",
    "Tableau",
    "Power BI",
    "Google Sheets",
    "Data Cleaning and Wrangling",
    "Statistical Analysis",
    "Microsoft Project",
    "Lean Six Sigma",
    "Risk Management",
    "Financial Modeling",
    "Budgeting",
    "Forecasting",
    "QuickBooks",
    "SAP",
    "Data Warehousing",
    "ETL (Extract, Transform, Load) Processes",
    "Business Analytics",
    "Data Mining",
    "Test Planning",
    "Test Automation (Selenium, Appium)",
    "Bug Tracking Tools (Jira, Bugzilla)",
    "User Acceptance Testing (UAT)",
    "Regression Testing",
    "AutoCAD",
    "SolidWorks",
    "Finite Element Analysis (FEA)",
    "Computational Fluid Dynamics (CFD)",
    "Thermodynamics",
    "AutoCAD Civil 3D",
    "Revit",
    "Structural Analysis",
    "Geotechnical Engineering",
    "Transportation Engineering",
    "MATLAB",
    "LabVIEW",
    "Power Systems Analysis",
    "Circuit Design",
    "Control Systems",
    "PCR (Polymerase Chain Reaction)",
    "DNA Sequencing",
    "Cell Culture Techniques",
    "Bioinformatics",
    "CRISPR/Cas9 Genome Editing",
    "Electronic Medical Records (EMR) Systems",
    "Medical Billing and Coding",
    "Health Informatics",
    "Healthcare Compliance",
    "Patient Care",
    "Geographic Information Systems (GIS)",
    "Environmental Impact Assessment",
    "Sustainability Analysis",
    "Pollution Control",
    "Climate Change Mitigation Strategies",
    "Aerospace CAD Software",
    "Aerodynamics",
    "Aircraft Design",
    "Rocket Propulsion",
    "Orbital Mechanics",
    "Process Simulation (Aspen HYSYS)",
    "Chemical Reaction Engineering",
    "Process Safety Management",
    "Petrochemical Engineering",
    "Polymer Science",
    "Precision Agriculture Technologies",
    "Crop Management Systems",
    "Soil Science",
    "Pest Management",
    "Agricultural Economics"
]

proficiency_levels = [
    "10%",
    "20%",
    "30%",
    "40%",
    "50%",
    "60%",
    "70%",
    "80%",
    "90%",
    "100%"
]
@app.route('/add_skill', methods=['POST'])
def add_skill():
    if 'student_id' in session:
        student_id = session['student_id']
        skill = request.json['skill']
        proficiency_level = request.json['proficiencyLevel']

        # Insert the skill into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO student_skills (student_id, skill_name, proficiency_level) VALUES (%s, %s, %s)",
                       (student_id, skill, proficiency_level))
        mysql.connection.commit()

        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Student not logged in'}), 401
@app.route('/get_skills', methods=['GET'])
def get_skills():
    try:
        cur = mysql.connection.cursor()
        student_id=session['student_id']
        cur.execute("SELECT skill_name, proficiency_level FROM student_skills WHERE student_id = %s", (student_id,))
        skills = cur.fetchall()
        return jsonify(success=True, skills=[{'name': skill[0], 'proficiency': skill[1]} for skill in skills])
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/delete_skill', methods=['POST'])
def delete_skill():
    data = request.get_json()
    skill = data['skill']
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM student_skills WHERE skill_name=%s AND student_id=%s", (skill, student_id))
    mysql.connection.commit()

    return jsonify({'success': True})
@app.route('/save_references', methods=['POST'])
def save_references():
    try:
        data = request.get_json()
        student_id = session['student_id']
        LinkedIn = data['linkedin']
        GitHub = data['github']
        Twitter = data['twitter']
        Facebook = data['facebook']
        index = data.get('index')
        cur = mysql.connection.cursor()
        if index is not None:
            cur.execute("UPDATE student_references SET LinkedIn = %s, GitHub = %s, Twitter = %s, Facebook = %s WHERE student_id = %s ", (LinkedIn, GitHub, Twitter, Facebook, student_id))
        else:
            cur.execute("INSERT INTO student_references(student_id, LinkedIn, GitHub, Twitter, Facebook) VALUES (%s, %s, %s, %s, %s)", (student_id, LinkedIn, GitHub, Twitter, Facebook))
        mysql.connection.commit()
        cur.close()
        return 'Data saved successfully'
    except Exception as e:
        print(e)
        return str(e), 500

@app.route('/get_references', methods=['GET'])
def get_references():
    cursor = mysql.connection.cursor()
    student_id=session['student_id']
    cursor.execute("SELECT LinkedIn, GitHub, Twitter, Facebook FROM student_references WHERE student_id = %s", (student_id,))  # Use your actual table and column names
    data = cursor.fetchall()
    references = [{'linkedin': row[0], 'github': row[1], 'twitter': row[2], 'facebook': row[3]} for row in data]
    return jsonify(references)

@app.route('/job/post')
def job_post():
    error = request.args.get('error')
    return render_template('job_post.html',error=error)

@app.route('/student_cover_letter', methods=['GET'])
def student_cover_letter():
    # Check if the student is logged in
    if 'student_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Connect to the database
    cur = mysql.connection.cursor()

    # Fetch the student's cover letter based on the session
    student_id = session['student_id']
    cur.execute("SELECT student_name, student_id, cover_letter_path FROM cover_letter WHERE student_id = %s", (student_id,))

    # Fetch all rows from the query
    cover_letters = cur.fetchall()

    # Close the cursor
    cur.close()

    # Pass the data to the template
    return render_template('student_cover_letter.html', cover_letters=cover_letters)
@app.route('/student/resumes')
def student_resumes():
    error = request.args.get('error')
    return render_template('student_resumes.html',error=error)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        student_id = session['student_id']
        filename = student_id + '.' + filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\resumes', filename))
        update_resume_path(filename)
        return 'File uploaded successfully'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

def update_resume_path(filename):
    student_id = session['student_id']
    filename = student_id + '.' + filename.rsplit('.', 1)[1].lower()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO resumes(student_id, resume_path) VALUES(%s, %s)", (student_id, filename))
    mysql.connection.commit()
    cur.close()
@app.route('/delete/file', methods=['DELETE'])
def delete_file():
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT resume_path FROM resumes WHERE student_id = %s", [student_id])
    result = cur.fetchone()
    print(result)
    if result:
        file_name=result[0]
        file_path=os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\resumes\\',file_name)
        print(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            cur.execute("DELETE FROM resumes WHERE student_id = %s", [student_id])
            mysql.connection.commit()
            cur.close()
            return 'File and data deleted successfully', 200
        else:
            return 'File not found', 404
@app.route('/get_file')
def get_file():
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT resume_path FROM resumes WHERE student_id = %s", [student_id])
    result = cur.fetchone()
    if result:
        file_name=result[0]
        file_path=os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\resumes\\',file_name)
        if os.path.exists(file_path):
            return '/static/resumes/' + file_name
        else:
            return 'File not found', 404
@app.route('/applied')
def applied():
    error = request.args.get('error')
    return render_template('applied.html',error=error)
@app.route('/api/job_titles', methods=['GET'])
def get_job_titles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title FROM job_notifi")
    job_titles = [row[0] for row in cur.fetchall()]
    cur.close()
    return jsonify(job_titles)
@app.route('/api/update_status', methods=['POST'])
def update_status():
    student_id = session['student_id']
    cur = mysql.connection.cursor()
    for title in request.form:
        status = request.form[title]
        cur.execute("INSERT INTO applied (student_id, job_title, status) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE status = %s", (student_id, title, status, status))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('applied'))
@app.route('/applications.html')
def applications():
    error = request.args.get('error')
    return render_template('applications.html',error=error)
@app.route('/fetch/job_titles')
def fetch_job_titles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT job_title FROM applied")
    job_titles = [row[0] for row in cur.fetchall()]
    cur.close()

    return jsonify(job_titles)

@app.route('/fetch/application')
@app.route('/fetch/application/<job_title>')
def fetch_application(job_title='All'):
    cur = mysql.connection.cursor()
    if job_title == 'All':
        cur.execute("SELECT * FROM applied")
    else:
        cur.execute("SELECT * FROM applied WHERE job_title = %s", [job_title])
    data = cur.fetchall()
    cur.close()

    # Convert each tuple to a dictionary
    data = [dict(zip(["student_id", "job_title", "status"], row)) for row in data]

    return jsonify(data)
@app.route('/resumes.html')
def resumes():
    error = request.args.get('error')
    return render_template('resumes.html',error=error)
@app.route('/fetch/resumes')
def fetch_resumes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT student_id, resume_path FROM resumes")
    rows = cur.fetchall()
    data = []
    for row in rows:
        data.append({
            'student_id': row[0],
            'resume_path': url_for('static', filename='resumes/' + row[1])
        })
    return jsonify(data)
@app.route('/top_performer_post.html')
def top_performer_post():
    error = request.args.get('error')

    # Fetch data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM top_performer")
    performers = [dict((cur.description[i][0], value)
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()

    return render_template('top_performer_post.html', error=error, performers=performers)

# Route to handle form submission
@app.route('/add_top_student', methods=['POST'])
def add_top_student():
    if request.method == 'POST':
        name = request.form['name']
        pin = request.form['pin']
        placements_cracked = request.form['Placements_cracked']
        department = request.form['Department']
        profile_picture = request.files['file']

        # Save the profile picture with student ID as filename
        picture_extension = profile_picture.filename.rsplit('.', 1)[1].lower()  # Get file extension
        picture_filename = f"{pin}.{picture_extension}"
        picture_path = os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\images\\top_performers_pictures', picture_filename)
        profile_picture.save(picture_path)

        # Save the form data to the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO top_performer (student_name, student_id, placements_cracked, dept_name, student_profile_pic_path) VALUES (%s, %s, %s, %s, %s)", (name, pin, placements_cracked, department, picture_filename))
        mysql.connection.commit()
        cur.close()

        # Redirect to the same page after form submission
        return redirect(url_for('top_performer_post'))
@app.route('/delete_top_student', methods=['POST'])
def delete_top_student():
    if request.method == 'POST':
        student_id = request.json['student_id']

        # Fetch the file path before deleting the record
        cur = mysql.connection.cursor()
        cur.execute("SELECT student_profile_pic_path FROM top_performer WHERE student_id = %s", [student_id])
        result = cur.fetchone()
        if result is None:
            print(f"No performer found for student_id {student_id}")
            return '', 404
        file_path = result[0]

        # Delete the record from the database
        cur.execute("DELETE FROM top_performer WHERE student_id = %s", [student_id])
        mysql.connection.commit()

        # Delete the profile picture from local storage
        os.remove(os.path.join('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\images\\top_performers_pictures', file_path))

        cur.close()

        return '', 200


@app.route('/cover_letter.html', methods=['GET'])
def cover_letter():
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query
    cur.execute("SELECT student_name, student_id, cover_letter_path FROM cover_letter")

    # Fetch all rows from the query
    cover_letters = cur.fetchall()

    # Close the cursor
    cur.close()

    # Pass the data to the template
    return render_template('cover_letter.html', cover_letters=cover_letters)


# Route to handle form submission
@app.route('/add_cover_letter', methods=['POST'])
def add_cover_letter():
    if request.method == 'POST':
        name = request.form['name']
        pin = request.form['pin']
        cover_letter = request.files['file']

        # Save the profile picture with student ID as filename
        file_extension = cover_letter.filename.rsplit('.', 1)[1].lower()  # Get file extension
        file_filename = f"{pin}.{file_extension}"
        file_path = os.path.join(
            'C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\cover_letter',
            file_filename)
        cover_letter.save(file_path)

        # Save the form data to the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cover_letter (student_name, student_id, cover_letter_path) VALUES (%s, %s, %s)",
                    (name, pin, file_filename))
        mysql.connection.commit()
        cur.close()

        # Redirect to the same page after form submission
        return redirect(url_for('cover_letter'))
@app.route('/cover_letter/<filename>')
def serve_cover_letter(filename):
    return send_from_directory('static/cover_letter', filename)
@app.route('/delete_cover_letter/<student_id>', methods=['DELETE'])
def delete_cover_letter(student_id):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Get the file path before deleting the record
    cur.execute("SELECT cover_letter_path FROM cover_letter WHERE student_id = %s", [student_id])
    # Get the file path before deleting the record
    result = cur.fetchone()
    if result is None:
        print(f"No cover letter found for student_id {student_id}")
        return '', 404
    file_path = result[0]

    # Execute the query
    cur.execute("DELETE FROM cover_letter WHERE student_id = %s", [student_id])

    # Commit the transaction
    mysql.connection.commit()

    # Close the cursor
    cur.close()

    # Delete the file from the local disk
    if file_path and os.path.isfile('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\cover_letter\\'+file_path):
        os.remove('C:\\Users\\Mani chandhar Reddy\\OneDrive\\Desktop\\Placement_Management_system\\pythonProject\\static\\cover_letter\\'+file_path)

    # Return a success status
    return '', 204


@app.route('/top_performer_view')
def top_performer_view():
    # Fetch data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM top_performer")
    performers = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()

    return render_template('top_performer_view.html', performers=performers)

@app.route('/logout')
def logout():
    # Perform logout actions (e.g., clear session data)
    # Redirect to the home page (index)
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
