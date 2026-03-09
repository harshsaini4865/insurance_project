from flask import Flask, render_template, request, jsonify
import json
import uuid
from datetime import datetime
import sqlite3
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# Create database if it doesn't exist
def init_db():
    conn = sqlite3.connect('insurance_applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  reference_id TEXT UNIQUE,
                  first_name TEXT,
                  last_name TEXT,
                  email TEXT,
                  phone TEXT,
                  insurance_type TEXT,
                  coverage_amount TEXT,
                  duration TEXT,
                  birth_date TEXT,
                  address TEXT,
                  city TEXT,
                  zip_code TEXT,
                  message TEXT,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-application', methods=['POST','GET'])
def submit_application():
    try:
        data = request.get_json()
        
        # Generate unique reference ID
        reference_id = 'INS' + str(uuid.uuid4())[:8].upper()
        
        # Store in database
        conn = sqlite3.connect('insurance_applications.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO applications 
                     (reference_id, first_name, last_name, email, phone, 
                      insurance_type, coverage_amount, duration, birth_date, 
                      address, city, zip_code, message)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (reference_id, data['firstName'], data['lastName'], 
                   data['email'], data['phone'], data['insuranceType'], 
                   data['coverageAmount'], data['duration'], data['birthDate'], 
                   data['address'], data['city'], data['zipCode'], 
                   data.get('message', '')))
        
        conn.commit()
        conn.close()
        
        # Here you would typically send an email notification
        # or integrate with other systems
        
        return jsonify({
            'success': True,
            'referenceId': reference_id,
            'message': 'Application submitted successfully'
        })
        
    except Exception as e:
        print(f"Error submitting application: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/applications')
def get_applications():
    try:
        conn = sqlite3.connect('insurance_applications.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM applications ORDER BY created_at DESC')
        applications = c.fetchall()
        
        conn.close()
        
        # Convert to list of dictionaries
        app_list = []
        for app in applications:
            app_dict = {
                'id': app[0],
                'reference_id': app[1],
                'first_name': app[2],
                'last_name': app[3],
                'email': app[4],
                'phone': app[5],
                'insurance_type': app[6],
                'coverage_amount': app[7],
                'duration': app[8],
                'birth_date': app[9],
                'address': app[10],
                'city': app[11],
                'zip_code': app[12],
                'message': app[13],
                'status': app[14],
                'created_at': app[15]
            }
            app_list.append(app_dict)
        
        return jsonify(app_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/application/<reference_id>')
def get_application(reference_id):
    try:
        conn = sqlite3.connect('insurance_applications.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM applications WHERE reference_id = ?', (reference_id,))
        application = c.fetchone()
        
        conn.close()
        
        if application:
            app_dict = {
                'id': application[0],
                'reference_id': application[1],
                'first_name': application[2],
                'last_name': application[3],
                'email': application[4],
                'phone': application[5],
                'insurance_type': application[6],
                'coverage_amount': application[7],
                'duration': application[8],
                'birth_date': application[9],
                'address': application[10],
                'city': application[11],
                'zip_code': application[12],
                'message': application[13],
                'status': application[14],
                'created_at': application[15]
            }
            return jsonify(app_dict)
        else:
            return jsonify({'error': 'Application not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-status/<reference_id>', methods=['POST'])
def update_status(reference_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'approved', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400
        
        conn = sqlite3.connect('insurance_applications.db')
        c = conn.cursor()
        
        c.execute('UPDATE applications SET status = ? WHERE reference_id = ?', 
                  (new_status, reference_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True, port=5000)
