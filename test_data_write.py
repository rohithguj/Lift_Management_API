import requests
import json

# Define the base URL for the Flask API
base_url = "http://127.0.0.1:5000/update_lift"

# Sample lift data to be sent to the backend (replace with your microcontroller's data)
lift_data = {
    "id": "LIFT_1",              # Lift ID (replace with an actual lift ID)
    "door_open": 1,              # 1 for open, 0 for closed (door state)
    "current_floor": 5,          # Current floor of the lift
    "alarm": 0                   # 0 for no alarm, 1 for alarm triggered
}

# Make the POST request to the Flask API
response = requests.post(base_url, json=lift_data)

# Check the response status code
if response.status_code == 200:
    print("Lift data successfully updated.")
else:
    print(f"Failed to update lift data. Status code: {response.status_code}")
    try:
        # Try to print the response JSON for better debugging
        print("Response JSON:", response.json())
    except Exception as e:
        print(f"Failed to parse response JSON: {e}")
