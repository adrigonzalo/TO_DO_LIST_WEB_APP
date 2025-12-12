"""
In this script we are going to code all the Flask logic and the DB

"""

import mysql.connector
import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# DB CONNECTION CREDENTIALS

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Initialize Flask app
app = Flask(__name__)

# Basic DB Security
app.secret_key = os.getenv('FLASK_SECRET_KEY', '9999')


# Function to communicate with the database to get data 
def get_db_connection():

    # Set and return a connection to the database
    try:
        connection = mysql.connector.connect(**DB_CONFIG) # Using '**' to unpack the DB_CONFIG dictionary as arguments to the connect() function.
        return connection
    
    except mysql.connector.Error as err:
        print(f'Error al conectar a MySQL: {err}')
        return None
    
# Flask decorator to associate the application's root URL with the index() function 
@app.route('/')

# Main root to show all the tasks
def index():

    # Connection to the database
    conn = get_db_connection()

    # Initialize an empty list for the tasks
    tasks = []

    if conn:
        try:

            # 1. Define a cursor. The "dictionary = True" parameter is very useful since the results will be returned like Python 
            # dictionaries, making it easier to access them by the column name
            cursor = conn.cursor(dictionary=True)

            # 2. Define the SQL query with all the tasks.
            query = """
                SELECT t.id, t.title, t.description, t.is_completed, t.created_at, c.name AS category_name, s.status_name
                FROM tasks t
                LEFT JOIN categories c ON c.id = t.category_id
                LEFT JOIN task_status s ON s.id = t.status_id
                ORDER BY t.created_at DESC;
            """ 

            # 3. Execute the query
            cursor.execute(query)
            tasks = cursor.fetchall() 

        except mysql.connector.Error as err:
            
            print(f'Error executing SQL query: {err}')

        finally:

            # 4. Close resources: It is a good practice to realise the cursor and the connection immediately
            if 'cursor' in locals() and cursor:

                cursor.close()

            if conn:
                
                conn.close()

    # 5. Render the HTML template, giving the tasks list
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])

# Handle the form submission to create a new task.
def add_task():

    # 1. Get the data from the form
    title = request.form['title']
    description = request.form.get('description', '')  # Use .get to prevent failure if it isn't sended.

    # 2. Connect to the database using the get_db_connection()
    conn = get_db_connection()

    if conn:
        try:

            cursor = conn.cursor()

            # 3. Define the INSERT query with the '%s' placeholders for the SQL security
            query = """
                INSERT INTO tasks (user_id, status_id, category_id, title, description)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Data which will be used in the SQL query. We have defined the data separated of the SQL query variable because the Python 'mysql-connector-python' requires it to prevent the SQL Injection
            data_to_insert = (1, 1, None, title, description)

            # 4. Execute query
            cursor.execute(query, data_to_insert)

            # 5. Transaction Confirmation: Saves changes in the DB
            conn.commit()

        except mysql.connector.Error as err:

            print(f'Error inserting task: {err}')
            conn.rollback() # If fails, undo any partial change

        finally:

            # 6. Free up Resources
            if 'cursor' in locals() and cursor:

                cursor.close()

            if conn:
                
                conn.close()

    # 7. User redirection to the main web with the updated list
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>', methods=['POST'])

# Function to complete and update the tasks list after a task is completed.
def complete_task(task_id):

    # 1. Database connection
    conn = get_db_connection()

    if conn:
        try:

            # 2. Get the cursor
            cursor = conn.cursor()

            # 3. Define the query
            query = """
                UPDATE tasks SET is_completed = 1 WHERE id = %s
            """

            # 4. Execute the query
            cursor.execute(query, (task_id,))

            # 5. Transaction Confirmation
            conn.commit()


        except mysql.connector.Error as err:
            print(f"Error updating the task:{err}")
            conn.rollback()

        finally:

            # 6. Free up Resources
            if 'cursor' in locals() and cursor:

                cursor.close()

            if conn:
                
                conn.close()            

    # 7. User redirection to the main web with the updated list
    return redirect(url_for('index'))


@app.route('/delete_task/<int:task_id>', methods=['POST'])

# Function to delete a specific task by ID permanently.
def delete_task(task_id):

    # 1. Database connection
    conn = get_db_connection()

    if conn:
        try:

            # 2. Get the cursor
            cursor = conn.cursor()

            # 3. Define the query
            query = """
                DELETE FROM tasks WHERE id = %s
            """

            # 4. Execute the query
            cursor.execute(query, (task_id,))

            # 5. Transaction Confirmation
            conn.commit()


        except mysql.connector.Error as err:
            print(f"Error deletin the task:{err}")
            conn.rollback()

        finally:

            # 6. Free up Resources
            if 'cursor' in locals() and cursor:

                cursor.close()

            if conn:
                
                conn.close()            

    # 7. User redirection to the main web with the updated list
    return redirect(url_for('index'))

# Execute the app
if __name__ == '__main__':
    app.run(debug=True)