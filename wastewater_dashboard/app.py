import logging
from flask import Flask, render_template, request, send_from_directory
from flask.json import jsonify
from json import JSONEncoder
from flask_socketio import SocketIO
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simulated data storage
pump_data = pd.DataFrame(columns=['timestamp', 'pump_id', 'power', 'optimized_power', 'efficiency', 'optimized_efficiency'])
aeration_data = pd.DataFrame(columns=['timestamp', 'basin_id', 'power', 'optimized_power', 'dissolved_oxygen', 'optimized_dissolved_oxygen'])
grid_data = pd.DataFrame(columns=['timestamp', 'demand', 'price'])

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/')
def index():
    try:
        logger.info("Index route accessed")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    send_initial_data()

def send_initial_data():
    logger.info("Sending initial data")
    socketio.emit('initial_data', {
        'pump_data': json.loads(pump_data.to_json(orient='records', date_format='iso')),
        'aeration_data': json.loads(aeration_data.to_json(orient='records', date_format='iso')),
        'grid_data': json.loads(grid_data.to_json(orient='records', date_format='iso'))
    })

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        logger.info("Received update_data request")
        data = request.get_json(force=True)
        if data is None:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        logger.info(f"Received data: {json.dumps(data, indent=2)}")
        handle_update_data(data)
        return jsonify({"message": "Data updated successfully"}), 200
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        return jsonify({"error": error_message}), 500

def handle_update_data(data):
    global pump_data, aeration_data, grid_data

    logger.info("Processing update_data")
    timestamp = datetime.now()

    try:
        # Validate the incoming data structure
        if 'pumps' not in data or 'aeration_basins' not in data or 'grid' not in data:
            raise ValueError("Invalid data structure. Missing 'pumps', 'aeration_basins', or 'grid'.")

        # Update pump data
        for pump in data['pumps']:
            new_pump_data = pd.DataFrame({
                'timestamp': [timestamp],
                'pump_id': [pump['id']],
                'power': [pump['power']],
                'optimized_power': [pump['optimized_power']],
                'efficiency': [pump['efficiency']],
                'optimized_efficiency': [pump['optimized_efficiency']]
            })
            pump_data = pd.concat([pump_data, new_pump_data], ignore_index=True)

        # Update aeration data
        for basin in data['aeration_basins']:
            new_aeration_data = pd.DataFrame({
                'timestamp': [timestamp],
                'basin_id': [basin['id']],
                'power': [basin['power']],
                'optimized_power': [basin['optimized_power']],
                'dissolved_oxygen': [basin['dissolved_oxygen']],
                'optimized_dissolved_oxygen': [basin['optimized_dissolved_oxygen']]
            })
            aeration_data = pd.concat([aeration_data, new_aeration_data], ignore_index=True)

        # Update grid data
        new_grid_data = pd.DataFrame({
            'timestamp': [timestamp],
            'demand': [data['grid']['demand']],
            'price': [data['grid']['price']]
        })
        grid_data = pd.concat([grid_data, new_grid_data], ignore_index=True)

        # Keep only the last 24 hours of data
        cutoff_time = timestamp - timedelta(hours=24)
        pump_data = pump_data[pump_data['timestamp'] > cutoff_time]
        aeration_data = aeration_data[aeration_data['timestamp'] > cutoff_time]
        grid_data = grid_data[grid_data['timestamp'] > cutoff_time]

        # Convert timestamp column to datetime
        pump_data['timestamp'] = pd.to_datetime(pump_data['timestamp'])
        aeration_data['timestamp'] = pd.to_datetime(aeration_data['timestamp'])
        grid_data['timestamp'] = pd.to_datetime(grid_data['timestamp'])

        logger.info("Data processing completed successfully")
        # Send updated data to clients
        send_initial_data()
    except Exception as e:
        logger.error(f"Error in handle_update_data: {str(e)}\n{traceback.format_exc()}")
        raise

@socketio.on('update_data')
def socket_update_data(data):
    logger.info("Received update data via WebSocket")
    handle_update_data(data)

if __name__ == '__main__':
    logger.info("Starting the server...")
    socketio.run(app, debug=True)