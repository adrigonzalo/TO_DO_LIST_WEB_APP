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