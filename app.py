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
                SELECT t.title, t.description, t.is_completed, t.created_at, c.name AS category_name, s.status_name
                FROM tasks t
                LEFT JOIN categories c ON c.id = t.category_id
                LEFT JOIN task_status s ON s.id = t.status_id
                ORDERY BY t.created_at DESC;
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


# Execute the app
if __name__ == '__main__':
    app.run(debug=True)