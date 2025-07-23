import os
import json
import yaml
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# ---------------- Load Config ----------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

LIFT_IDS = config["lift_ids"]
DATA_FOLDER = config["data_folder"]
MAX_FLOORS = config["max_floor"]

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# ---------------- Flask App ----------------
app = Flask(__name__)
socketio = SocketIO(app)

# Enable CORS for localhost:3000
CORS(app, origins="http://localhost:3000")  # Allow only localhost:3000

# Allow specific origins to connect to Socket.IO
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"])  # Only allow local hosts 3000 and 5000


# -------- Save Lift Data to JSON File --------
def save_lift_data(lift_id, data):
    data = dict(data)
    lift_file = os.path.join(DATA_FOLDER, f"{lift_id}.json")
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Check if the data has changed before saving
    if os.path.exists(lift_file):
        with open(lift_file, 'r') as f:
            existing_data = json.load(f)
        
        if existing_data == data:  # No change in data, no need to save or emit
            return False

    with open(lift_file, 'w') as f:
        json.dump(data, f)
    return True

# -------- REST API: POST /update_lift --------
@app.route('/update_lift', methods=['POST'])
def update_lift():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Invalid JSON: {e}'}), 400

    lift_id = data.get('id')
    if lift_id not in LIFT_IDS:
        return jsonify({'status': 'error', 'message': 'Invalid lift id'}), 400

    # Save data and check if it has changed
    new_data = save_lift_data(lift_id, data)

    if new_data:
        socketio.emit('lift_data_update', data, room=lift_id)

    return jsonify({'status': 'success'}), 200

# -------- REST API: GET /get_max_floor --------
@app.route('/intialize_data', methods=['GET'])
def get_max_floor():
    # Return max floor and lift IDs
    return jsonify({'max_floor': MAX_FLOORS, 'lift_ids': LIFT_IDS})

# ---------------- API: Get Data for a Specific Lift ----------------
@app.route('/get_lift_data/<lift_id>', methods=['GET'])
def get_lift_data(lift_id):
    if lift_id not in LIFT_IDS:
        return jsonify({'status': 'error', 'message': 'Invalid lift id'}), 400

    lift_file = os.path.join(DATA_FOLDER, f"{lift_id}.json")
    if not os.path.exists(lift_file):
        return jsonify({'status': 'error', 'message': 'No data found'}), 404

    with open(lift_file, 'r') as f:
        data = json.load(f)

    return jsonify({'status': 'success', 'data': data}), 200

# ---------------- API: Get Data for All Lifts ----------------
@app.route('/get_all_lifts', methods=['GET'])
def get_all_lifts():
    all_data = {}
    for lift_id in LIFT_IDS:
        lift_file = os.path.join(DATA_FOLDER, f"{lift_id}.json")
        if os.path.exists(lift_file):
            with open(lift_file, 'r') as f:
                all_data[lift_id] = json.load(f)
        else:
            all_data[lift_id] = {}  # Mark as blocked if no data

    return jsonify({'status': 'success', 'data': all_data}), 200

# -------- WebSocket: Join/Leave Room --------
@socketio.on('join_lift')
def on_join_lift(lift_id):
    print(f"Client joined room for {lift_id}")
    join_room(lift_id)
    emit('message', {'message': f'Joined room for {lift_id}'}, room=lift_id)

@socketio.on('leave_lift')
def on_leave_lift(lift_id):
    print(f"Client left room for {lift_id}")
    leave_room(lift_id)

# ---------------- Run Server ----------------
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
