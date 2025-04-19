import sqlite3
import psycopg2
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# -------------------- ROUTE TO FRONTEND --------------------
@app.route('/')
def home():
    return render_template('flowers.html')

# -------------------- SQLITE SETUP (FOR FLOWERS) --------------------
def get_db_connection():
    cx = sqlite3.connect("team12_flowers.db")
    cx.row_factory = sqlite3.Row
    return cx

@app.route('/flowers', methods=['GET'])
def get_flowers():
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required, image_url FROM team12_flowers;")
    flowers = cur.fetchall()
    cur.close()
    cx.close()
    return jsonify([{
        "id": flower["id"],
        "name": flower["name"],
        "last_watered": flower["last_watered"],
        "water_level": flower["water_level"],
        "needs_watering": flower["water_level"] < flower["min_water_required"],
        "image_url": flower["image_url"]
    } for flower in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required FROM team12_flowers WHERE water_level < min_water_required;")
    flowers = cur.fetchall()
    cur.close()
    cx.close()
    return jsonify([{
        "id": flower["id"],
        "name": flower["name"],
        "last_watered": flower["last_watered"],
        "water_level": flower["water_level"],
        "needs_watering": True,
        "img_url": flower["image_url"]
    } for flower in flowers])

@app.route('/flowers', methods=['POST'])
def add_flower():
    data = request.json
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("""
        INSERT INTO team12_flowers (name, last_watered, water_level, min_water_required)
        VALUES (?, ?, ?, ?);
    """, (data['name'], data['last_watered'], data['water_level'], data['min_water_required']))
    cx.commit()
    cur.close()
    cx.close()
    return jsonify({"message": "Flower added successfully!"})

@app.route('/flowers/<int:id>', methods=['PUT'])
def update_flower(id):
    data = request.json
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("""
        UPDATE team12_flowers
        SET last_watered = ?, water_level = ?
        WHERE id = ?;
    """, (data['last_watered'], data['water_level'], id))
    cx.commit()
    cur.close()
    cx.close()
    return jsonify({"message": "Flower updated successfully!"})

@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("DELETE FROM team12_flowers WHERE id = ?;", (id,))
    cx.commit()
    cur.close()
    cx.close()
    return jsonify({"message": "Flower deleted successfully!"})

# -------------------- POSTGRESQL SETUP FOR PERFORMANCE TEST --------------------
PG_CONN = {
    "dbname": "team12_db",
    "user": "postgres",
    "password": "flower123",  # <-- Replace with your actual PostgreSQL password
    "host": "localhost",
    "port": "5432"
}

def run_pg_query(query):
    conn = psycopg2.connect(**PG_CONN)
    cur = conn.cursor()
    start = time.time()
    cur.execute(query)
    conn.commit()
    end = time.time()
    cur.close()
    conn.close()
    return {
        "query": query,
        "execution_time": round((end - start) * 1000, 2)  # in milliseconds
    }

@app.route('/slow-query')
def slow_query():
    query = """
        SELECT 
            pgp_sym_encrypt(c.name, 'secretkey') AS encrypted_name,
            c.email,
            f.name AS flower_name,
            o.order_date
        FROM team12_orders o
        JOIN team12_customers c ON o.customer_id = c.id
        JOIN team12_flowers f ON o.flower_id = f.id
        ORDER BY o.order_date DESC;
    """
    return jsonify(run_pg_query(query))

@app.route('/fast-query')
def fast_query():
    query = """
        SELECT 
            c.name,
            c.email,
            f.name AS flower_name,
            o.order_date
        FROM team12_orders o
        JOIN team12_customers c ON o.customer_id = c.id
        JOIN team12_flowers f ON o.flower_id = f.id
        LIMIT 100;
    """
    return jsonify(run_pg_query(query))

# -------------------- FLASK MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)
