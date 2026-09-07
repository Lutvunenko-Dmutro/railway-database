import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from database import get_db_connection, init_db

load_dotenv()

app = Flask(__name__)

# --- Роути сторінок ---
@app.route('/')
def index():
    """Повертає головну сторінку Dashboard."""
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """Кастомна 404 помилка з голограмою."""
    return render_template('404.html'), 404

# --- API Роути ---
@app.route('/api/users', methods=['GET'])
def get_users():
    """Повертає список всіх користувачів."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM users ORDER BY id DESC;')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    """Додає нового користувача."""
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Відсутній обов'язковий параметр username"}), 400

    username = data.get('username')
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')

    # Валідація віку
    if age is not None and age != "":
        try:
            age = int(age)
            if age < 18 or age > 120:
                return jsonify({"error": "Вік повинен бути від 18 до 120 років"}), 400
        except ValueError:
            return jsonify({"error": "Некоректний формат віку"}), 400
    else:
        age = None

    # Валідація email
    if email:
        email = email.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return jsonify({"error": "Некоректний формат email адреси"}), 400
    else:
        email = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO users (username, name, email, age) VALUES (%s, %s, %s, %s) RETURNING id;',
            (username, name, email, age)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Користувача успішно створено",
            "user": {
                "id": new_id,
                "username": username,
                "name": name,
                "age": age,
                "email": email
            }
        }), 201
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        error_msg = str(e)
        if 'unique_email' in error_msg:
            return jsonify({"error": f"Користувач з email '{email}' вже існує"}), 409
        return jsonify({"error": f"Користувач з username '{username}' вже існує"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Оновлює дані існуючого користувача."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Дані не надано"}), 400
        
    username = data.get('username')
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')

    if not username:
        return jsonify({"error": "Username є обов'язковим"}), 400

    # Валідація
    if age is not None and age != "":
        try:
            age = int(age)
            if age < 18 or age > 120:
                return jsonify({"error": "Вік повинен бути від 18 до 120 років"}), 400
        except ValueError:
            return jsonify({"error": "Некоректний формат віку"}), 400
    else:
        age = None

    if email:
        email = email.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return jsonify({"error": "Некоректний формат email адреси"}), 400
    else:
        email = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE id = %s;', (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Користувача не знайдено"}), 404
            
        cursor.execute(
            'UPDATE users SET username = %s, name = %s, age = %s, email = %s WHERE id = %s;',
            (username, name, age, email, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Дані користувача оновлено"}), 200
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        error_msg = str(e)
        if 'unique_email' in error_msg:
            return jsonify({"error": f"Цей email вже використовується іншим користувачем"}), 409
        return jsonify({"error": f"Користувач з username '{username}' вже існує"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Видаляє користувача з бази даних за його ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE id = %s;', (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Користувача не знайдено"}), 404
            
        cursor.execute('DELETE FROM users WHERE id = %s;', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Користувача успішно видалено"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Запуск Flask сервера (debug вмикається тільки якщо FLASK_DEBUG=true)
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    init_db()
    app.run(host='0.0.0.0', port=port, debug=is_debug)
