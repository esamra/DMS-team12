import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection function
def get_db_connection():
    cx = sqlite3.connect("team12_flowers.db")
    cx.row_factory = sqlite3.Row  # enables name-based access to columns
    return cx

# get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required FROM team12_flowers;")
    flowers = cur.fetchall()
    cur.close()
    cx.close()
    
    # return all flowers with their details
    return jsonify([{
        "id": flower["id"],
        "name": flower["name"],
        "last_watered": flower["last_watered"],
        "water_level": flower["water_level"],
        "needs_watering": flower["water_level"] < flower["min_water_required"]
    } for flower in flowers])

# gets flowers that need watering
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
        "needs_watering": True 
    } for flower in flowers])

# adds a flower
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

# update a flower (by ID)
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

# delete a flower (by ID)
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    cx = get_db_connection()
    cur = cx.cursor()
    cur.execute("DELETE FROM team12_flowers WHERE id = ?;", (id,))
    cx.commit()
    cur.close()
    cx.close()
    return jsonify({"message": "Flower deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
