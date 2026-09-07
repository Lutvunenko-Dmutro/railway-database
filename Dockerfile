# Використовуємо офіційний легкий образ Python
FROM python:3.10-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Встановлюємо системні залежності для psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Копіюємо файл залежностей та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# Відкриваємо порт, на якому працюватиме Flask
EXPOSE 5000

# Запускаємо сервер
CMD ["python", "app.py"]
