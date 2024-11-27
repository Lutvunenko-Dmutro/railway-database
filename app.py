import os
import psycopg2
from flask import Flask

app = Flask(__name__)

# Підключення до бази даних
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('DB_NAME')
    )
    return conn

@app.route('/')
def index():
    # Підключення до БД і виконання запиту
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM your_table_name;')
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
