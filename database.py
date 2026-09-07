import os
import psycopg2
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

def get_db_connection():
    """Створює та повертає з'єднання з базою даних."""
    env = os.environ.get('ENVIRONMENT', 'local').lower()
    
    if env == 'railway':
        prefix = 'RAILWAY_'
    else:
        prefix = 'LOCAL_'
        
    return psycopg2.connect(
        host=os.environ.get(f'{prefix}DB_HOST', 'localhost'),
        database=os.environ.get(f'{prefix}DB_NAME', 'postgres'),
        user=os.environ.get(f'{prefix}DB_USER', 'postgres'),
        password=os.environ.get(f'{prefix}DB_PASSWORD', 'postgres'),
        port=os.environ.get(f'{prefix}DB_PORT', '5432')
    )

def init_db():
    """Ініціалізує базу даних: створює таблицю та додає унікальні обмеження."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) NOT NULL,
                name VARCHAR(100),
                email VARCHAR(120),
                age INTEGER
            );
        ''')
        
        # Унікальність username
        cursor.execute("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'users' AND constraint_type = 'UNIQUE' AND constraint_name = 'unique_username';
        """)
        if not cursor.fetchone():
            print("Додаю унікальне обмеження для username...")
            cursor.execute("""
            DELETE FROM users
            WHERE id NOT IN (
                SELECT MIN(id) FROM users GROUP BY username
            );
            """)
            cursor.execute('ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (username);')
            
        # Унікальність email
        cursor.execute("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'users' AND constraint_type = 'UNIQUE' AND constraint_name = 'unique_email';
        """)
        if not cursor.fetchone():
            print("Додаю унікальне обмеження для email...")
            cursor.execute("""
            DELETE FROM users
            WHERE id NOT IN (
                SELECT MIN(id) FROM users GROUP BY email HAVING email IS NOT NULL
            ) AND email IS NOT NULL;
            """)
            cursor.execute('ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);')

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ База даних успішно ініціалізована та готова до роботи.")
    except Exception as e:
        print(f"❌ Помилка ініціалізації бази даних: {e}")
