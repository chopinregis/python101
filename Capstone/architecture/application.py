from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import os
import pymysql
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages

# ... (keep the existing imports and configuration)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    try:
        # Store data in MySQL
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO patients 
                         (name, last_name, dob, hospital, symptoms) 
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (data['name'], data['lastName'], data['dob'], 
                                     data['hospital'], data['symptoms']))
            connection.commit()
        
        # Make API call to Lambda function via API Gateway
        response = requests.post(f"{API_ENDPOINT}/submit", json=data)
        result = response.json()
        
        # If everything is successful, redirect to patients page
        flash('Patient information submitted successfully!', 'success')
        return redirect(url_for('patients'))
    
    except pymysql.Error as e:
        # Database error
        error_message = f"Database error: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    except requests.RequestException as e:
        # API call error
        error_message = f"API error: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    except Exception as e:
        # Any other error
        error_message = f"An unexpected error occurred: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    
    # If there was an error, re-render the form
    return render_template('form.html', hospital=data['hospital'])

@app.route('/patients')
def patients():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM patients")
                patients = cursor.fetchall()
        return render_template('patients.html', patients=patients)
    except Exception as e:
        flash(f"Error retrieving patients: {e}", 'error')
        return redirect(url_for('index'))

# ... (keep the rest of your routes)