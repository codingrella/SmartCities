from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
from flask_socketio import SocketIO, emit
import random
import json
import socket
import webbrowser

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Verbindung zu einem externen Server herstellen, um die lokale IP zu ermitteln
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        print(f"Fehler beim Ermitteln der lokalen IP: {e}")
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def sensor_data():
    # Simulierte Sensordaten – später ersetzen durch echte Werte
    data = {
        'temperature': round(random.uniform(20, 30), 2),
        'light': random.randint(300, 800),
        'humidity': round(random.uniform(40, 60), 1)
    }
    return jsonify(data)

if __name__ == '__main__':
    port = 5000,
    local_ip = get_local_ip(),
    url = f"http://{local_ip}:{port[0]}"
    app.run(debug=True, host='0.0.0.0')
