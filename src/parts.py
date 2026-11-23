from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os

parts_bp = Blueprint("parts", __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'autoparts.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@parts_bp.route("/parts/add", methods=["GET"])
def add_part_form():
    conn = get_db()
    brands = conn.execute("SELECT id, name FROM brands ORDER BY name").fetchall()
    categories = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    conn.close()
    return render_template("add_part.html", brands=brands, categories=categories)

@parts_bp.route("/parts/add", methods=["POST"])
def add_part():
    article = request.form.get("article", "").strip()
    name = request.form.get("name", "").strip()
    brand_id = request.form.get("brand_id", "").strip()
    category_id = request.form.get("category_id", "").strip()
    price_raw = request.form.get("price", "").strip()
    stock_raw = request.form.get("stock", "").strip()
    description = request.form.get("description", "").strip()

    errors = []
    if not article: errors.append("Укажите артикул.")
    if not name: errors.append("Укажите наименование.")
    if not brand_id: errors.append("Выберите бренд.")
    if not category_id: errors.append("Выберите категорию.")

    try:
        price = float(price_raw.replace(",", "."))
        if price < 0: 
            errors.append("Цена должна быть больше нуля.")
    except ValueError:
        price = None
        errors.append("Цена должна быть числом.")

    try:
        stock = int(stock_raw)
        if stock < 0: errors.append("Остаток не может быть отрицательным.")
    except ValueError:
        stock = None
        errors.append("Остаток должен быть целым числом.")

    if errors:
        for e in errors: flash(e, "error")
        return redirect(url_for("parts.add_part_form"))

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO parts (article, name, brand_id, category_id, price, stock, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (article, name, brand_id, category_id, price, stock, description),
        )
        conn.commit()
        flash("Запчасть добавлен в каталог.", "success") 
    except sqlite3.IntegrityError:
        flash("Запчасть с таким артикулом уже существует.", "error")
    finally:
        conn.close()

    return redirect(url_for("parts.catalog"))

@parts_bp.route("/catalog")
def catalog():
    search_query = request.args.get("search", "").strip()
    brand_filter = request.args.get("brand_id", "").strip()
    
    conn = get_db()
    
    query = """
        SELECT p.*, b.name as brand_name, c.name as category_name 
        FROM parts p
        JOIN brands b ON p.brand_id = b.id
        JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (p.name LIKE ? OR p.article LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if brand_filter:
        query += " AND p.brand_id = ?"
        params.append(brand_filter)
        
    query += " ORDER BY p.id DESC"
    
    parts = conn.execute(query, params).fetchall()
    brands = conn.execute("SELECT id, name FROM brands ORDER BY name").fetchall()
    
    total_value = sum(p['price'] * p['stock'] for p in parts)
    
    conn.close()
    return render_template("catalog.html", parts=parts, brands=brands, total_value=total_value, search_query=search_query, brand_filter=brand_filter)

@parts_bp.route("/dashboard")
def dashboard(): return "<h2>Дашборд директора</h2><a href='/catalog'>Вернуться в каталог</a>"

@parts_bp.route("/directory")
def directory(): return "<h2>Справочник</h2><a href='/catalog'>Вернуться в каталог</a>"

@parts_bp.route("/cart")
def cart(): return "<h2>Корзина</h2><a href='/catalog'>Вернуться в каталог</a>"
