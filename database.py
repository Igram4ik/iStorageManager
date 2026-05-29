import sqlite3
import hashlib
from datetime import datetime

DB_NAME = 'warehouse.db'


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            unit TEXT DEFAULT 'шт.'
        )
    ''')

    # Таблица остатков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            product_id INTEGER PRIMARY KEY,
            quantity REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    ''')

    # Таблица транзакций – при удалении товара транзакции тоже удаляются (ON DELETE CASCADE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('IN','OUT')) NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            user_id INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Предустановленные данные
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (login, password_hash, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin'), 'admin'))
        cursor.execute("INSERT INTO users (login, password_hash, role) VALUES (?, ?, ?)",
                       ('user', hash_password('user'), 'user'))

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        for name in ['Товар А', 'Товар Б', 'Товар В']:
            cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))

    cursor.execute("SELECT COUNT(*) FROM stock")
    if cursor.fetchone()[0] == 0:
        for pid in range(1, 4):
            cursor.execute("INSERT OR IGNORE INTO stock (product_id, quantity) VALUES (?, 10)", (pid,))

    conn.commit()
    conn.close()


def authenticate(login, password):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
    conn.close()
    if user and user['password_hash'] == hash_password(password):
        return user
    return None


def register_user(login, password):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (login, password_hash, role) VALUES (?, ?, 'user')",
                     (login, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_products():
    conn = get_connection()
    products = conn.execute("SELECT id, name, unit FROM products ORDER BY name").fetchall()
    conn.close()
    return products


def get_stock(product_id=None):
    conn = get_connection()
    if product_id:
        row = conn.execute("SELECT quantity FROM stock WHERE product_id = ?", (product_id,)).fetchone()
        conn.close()
        return row['quantity'] if row else 0
    else:
        rows = conn.execute('''
            SELECT p.id, p.name, p.unit, COALESCE(s.quantity, 0) as qty
            FROM products p LEFT JOIN stock s ON p.id = s.product_id
            ORDER BY p.name
        ''').fetchall()
        conn.close()
        return rows


def add_transaction(type, product_id, quantity, user_id):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute("SELECT quantity FROM stock WHERE product_id = ?", (product_id,)).fetchone()
        current_qty = cur['quantity'] if cur else 0
        if type == 'OUT' and current_qty < quantity:
            conn.rollback()
            return False
        new_qty = current_qty + quantity if type == 'IN' else current_qty - quantity
        conn.execute("INSERT OR REPLACE INTO stock (product_id, quantity) VALUES (?, ?)",
                     (product_id, new_qty))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute('''INSERT INTO transactions (type, product_id, quantity, user_id, date_time)
                        VALUES (?, ?, ?, ?, ?)''',
                     (type, product_id, quantity, user_id, now))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ========== НОВЫЕ ФУНКЦИИ ДЛЯ АДМИНИСТРАТОРА ==========

def add_product(name: str, unit: str) -> int:
    """Добавляет новый товар, возвращает его id или None при дубликате."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO products (name, unit) VALUES (?, ?)",
            (name, unit)
        )
        product_id = cursor.lastrowid
        # Создаём запись в stock с нулевым количеством
        conn.execute(
            "INSERT INTO stock (product_id, quantity) VALUES (?, 0)",
            (product_id,)
        )
        conn.commit()
        return product_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_product(product_id: int, name: str, unit: str) -> bool:
    """Обновляет название и единицу измерения товара."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE products SET name = ?, unit = ? WHERE id = ?",
            (name, unit, product_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_product(product_id: int) -> bool:
    """
    Удаляет товар. Благодаря ON DELETE CASCADE, транзакции и остатки удалятся автоматически.
    """
    conn = get_connection()
    try:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def set_stock_quantity(product_id: int, new_quantity: float) -> bool:
    """Прямая установка количества (для администратора)."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE stock SET quantity = ? WHERE product_id = ?",
            (new_quantity, product_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()