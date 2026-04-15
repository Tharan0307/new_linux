from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# In-memory "database" of users
users = {
    1: {"id": 1, "name": "Alice Johnson", "role": "Admin", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob Smith",    "role": "Editor", "email": "bob@example.com"},
    3: {"id": 3, "name": "Carol White",  "role": "Viewer", "email": "carol@example.com"},
}
next_id = 4


# ─── Serve frontend ───────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# ─── GET all users ────────────────────────────────────────────────────────────
@app.route('/api/users', methods=['GET'])
def get_users():
    """GET  →  Read all resources"""
    return jsonify({
        "method": "GET",
        "description": "Fetches ALL users from the server. Safe & idempotent — calling it multiple times never changes data.",
        "data": list(users.values())
    })


# ─── GET single user ──────────────────────────────────────────────────────────
@app.route('/api/users/<int:uid>', methods=['GET'])
def get_user(uid):
    """GET  →  Read one resource"""
    user = users.get(uid)
    if not user:
        return jsonify({"error": f"User {uid} not found"}), 404
    return jsonify({
        "method": "GET",
        "description": f"Fetches the single user with id={uid}.",
        "data": user
    })


# ─── POST — create ────────────────────────────────────────────────────────────
@app.route('/api/users', methods=['POST'])
def create_user():
    """POST  →  Create a new resource"""
    global next_id
    body = request.get_json(force=True)
    if not body or not body.get('name'):
        return jsonify({"error": "name is required"}), 400
    new_user = {
        "id":    next_id,
        "name":  body.get('name', ''),
        "role":  body.get('role', 'Viewer'),
        "email": body.get('email', '')
    }
    users[next_id] = new_user
    next_id += 1
    return jsonify({
        "method": "POST",
        "description": "Creates a brand-new user. NOT idempotent — each call creates another record.",
        "data": new_user
    }), 201


# ─── PUT — full replace ───────────────────────────────────────────────────────
@app.route('/api/users/<int:uid>', methods=['PUT'])
def replace_user(uid):
    """PUT  →  Fully replace a resource (all fields required)"""
    if uid not in users:
        return jsonify({"error": f"User {uid} not found"}), 404
    body = request.get_json(force=True)
    if not body or not body.get('name') or not body.get('role') or not body.get('email'):
        return jsonify({"error": "PUT requires name, role, and email (full replacement)"}), 400
    users[uid] = {"id": uid, "name": body['name'], "role": body['role'], "email": body['email']}
    return jsonify({
        "method": "PUT",
        "description": "Fully replaces the user. All fields are overwritten. Idempotent — same request = same result.",
        "data": users[uid]
    })


# ─── PATCH — partial update ───────────────────────────────────────────────────
@app.route('/api/users/<int:uid>', methods=['PATCH'])
def update_user(uid):
    """PATCH  →  Partially update a resource (only changed fields)"""
    if uid not in users:
        return jsonify({"error": f"User {uid} not found"}), 404
    body = request.get_json(force=True)
    user = users[uid]
    for key in ('name', 'role', 'email'):
        if key in body:
            user[key] = body[key]
    return jsonify({
        "method": "PATCH",
        "description": "Updates ONLY the fields you send. Other fields stay untouched. Great for partial edits.",
        "data": user
    })


# ─── DELETE ───────────────────────────────────────────────────────────────────
@app.route('/api/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    """DELETE  →  Remove a resource"""
    if uid not in users:
        return jsonify({"error": f"User {uid} not found"}), 404
    deleted = users.pop(uid)
    return jsonify({
        "method": "DELETE",
        "description": "Permanently removes the user from the server. Idempotent — deleting twice still results in 'gone'.",
        "data": deleted
    })


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5000)
