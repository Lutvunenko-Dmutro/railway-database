
# Практична Робота 4: Створення віддаленої БД на Railway.app

Цей проект демонструє процес створення віддаленої бази даних на платформі Railway.app. В роботі використано PostgreSQL як тип бази даних.

## Кроки виконання:

### 1. Реєстрація та створення проекту на Railway.app
1. Зареєструйтеся на платформі [Railway.app](https://railway.app/).
2. Створіть новий проект, використовуючи опцію "New Project".
3. Виберіть шаблон для PostgreSQL бази даних.

### 2. Налаштування бази даних
1. Після створення проекту додайте плагін PostgreSQL.
2. Отримайте дані для підключення до вашої бази даних, зокрема:
   - Хост
   - Порт
   - Ім'я користувача
   - Пароль
   - URL для підключення

### 3. Підключення до БД
1. Використовуйте отримані дані для підключення до бази даних через **pgAdmin** або інший SQL клієнт.
2. Перевірте доступність бази даних, підключившись до неї.

### 4. Створення таблиці
1. Використовуючи SQL консоль, створіть таблицю в базі даних:
   ```sql
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100),
       email VARCHAR(100)
   );
   ```
2. Перевірте, чи таблиця була успішно створена, використовуючи запит:
   ```sql
   SELECT * FROM users;
   ```

### 5. Підключення через Python
1. Використовуйте Python бібліотеку `psycopg2` для підключення до бази даних:
   ```python
   import psycopg2

   connection = psycopg2.connect(
       dbname='railway',
       user='postgres',
       password='your_password',
       host='junction.proxy.rlwy.net',
       port='19910'
   )

   cursor = connection.cursor()
   cursor.execute("SELECT * FROM users;")
   result = cursor.fetchall()
   print(result)

   cursor.close()
   connection.close()
   ```
2. Запустіть Python скрипт для виведення даних з таблиці.

### 6. Перевірка роботи
1. Перевірте, чи база даних працює коректно через pgAdmin або ваш Python скрипт.
2. Переконайтесь, що запити до бази даних виконуються без помилок.

## Висновки
Цей проект дозволяє створити віддалену базу даних за допомогою Railway.app, налаштувати підключення та виконувати SQL запити для роботи з даними. Все налаштовано для використання в Python додатках або через SQL клієнти.
