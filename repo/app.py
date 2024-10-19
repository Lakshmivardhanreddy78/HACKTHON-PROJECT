from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    hackathon_count = db.Column(db.Integer, nullable=False)
    paper_presentations = db.Column(db.Integer, nullable=False)
    ta_contributions = db.Column(db.Integer, nullable=False)
    core_course_performance = db.Column(db.Float, nullable=False)
    consistency_over_semesters = db.Column(db.Float, nullable=False)

# Create the database
@app.before_request
def create_tables():
    db.create_all()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# API to add a student
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = Student(
        name=data['name'],
        department=data['department'],
        year=data['year'],
        cgpa=data['cgpa'],
        hackathon_count=data['hackathon_count'],
        paper_presentations=data['paper_presentations'],
        ta_contributions=data['ta_contributions'],
        core_course_performance=data['core_course_performance'],
        consistency_over_semesters=data['consistency_over_semesters']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student added successfully!"})

# API to fetch and rank students based on year and department
@app.route('/rank_students', methods=['GET'])
def rank_students():
    year = request.args.get('year', type=int)
    department = request.args.get('department', type=str)
    students = Student.query.filter_by(year=year, department=department).all()

    student_data = [
        [student.name, student.cgpa, student.hackathon_count, student.paper_presentations, 
         student.ta_contributions, student.core_course_performance, student.consistency_over_semesters]
        for student in students
    ]

    # Normalize the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform([[s[1], s[2], s[3], s[4], s[5], s[6]] for s in student_data])

    # Rank students using a weighted sum formula
    ranked_students = sorted(
        [
            {"name": student[0], "score": (scaled[0] * 0.3) + (scaled[1] * 0.2) + 
                       (scaled[2] * 0.1) + (scaled[3] * 0.1) + 
                       (scaled[4] * 0.2) + (scaled[5] * 0.1)}
            for student, scaled in zip(student_data, scaled_data)
        ], key=lambda x: x["score"], reverse=True
    )

    return jsonify(ranked_students[:3])

# API to fetch students based on year and department
@app.route('/students', methods=['GET'])
def get_students():
    year = request.args.get('year', type=int)
    department = request.args.get('department', type=str)

    query = Student.query
    if year:
        query = query.filter(Student.year == year)
    if department:
        query = query.filter(Student.department == department)

    students = query.all()
    student_data = [
        {
            "name": student.name,
            "department": student.department,
            "year": student.year,
            "cgpa": student.cgpa,
            "hackathon_count": student.hackathon_count,
            "paper_presentations": student.paper_presentations,
            "ta_contributions": student.ta_contributions,
            "core_course_performance": student.core_course_performance,
            "consistency_over_semesters": student.consistency_over_semesters
        }
        for student in students
    ]

    return jsonify(student_data)

# API to clear the entire student database
@app.route('/clear_database', methods=['DELETE'])
def clear_database():
    db.session.query(Student).delete()
    db.session.commit()
    return jsonify({"message": "All student records cleared successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
