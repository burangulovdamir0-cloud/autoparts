import sqlite3
import os

if os.path.exists('db/autoparts.db'):
    os.remove('db/autoparts.db')

conn = sqlite3.connect('db/autoparts.db')
cursor = conn.cursor()


cursor.executescript('''
CREATE TABLE brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    brand_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (brand_id) REFERENCES brands(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
''')


brands = [('Bosch',), ('Brembo',), ('Mobil',), ('Michelin',)]
categories = [('Тормозная система',), ('Моторное масло',), ('Шины',), ('Фильтры',)]

cursor.executemany('INSERT INTO brands (name) VALUES (?)', brands)
cursor.executemany('INSERT INTO categories (name) VALUES (?)', categories)

conn.commit()
conn.close()
print("УСПЕХ! База данных успешно создана и заполнена тестовыми данными.")
