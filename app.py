from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
from flask_socketio import SocketIO, emit
import random
import json
import socket
import webbrowser
import psycopg2
import datetime
import threading
import time

app = Flask(__name__, template_folder='template', static_folder='frontend')
socketio = SocketIO(app)

def get_connection():
    try:
        conn = psycopg2.connect(database = "SmartCities25", 
                        user = "postgres", 
                        host= '100.116.69.214',
                        password = "Tn#2SKSS25",
                        port = 5432)
        return conn
    except Exception as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Styles/<filename>')
def serve_css(filename):
    return send_from_directory('frontend/Styles', filename)

@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    if not conn:
        return "Datenbankverbindung fehlgeschlagen", 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.rooms")
        rooms = cur.fetchall()

        cur.execute("SELECT * FROM public.seatoccupied")
        seat_occupied = cur.fetchall()

        cur.execute("SELECT * FROM public.airconditioning")
        aircon = cur.fetchall()

        cur.execute("SELECT * FROM public.blinds")
        blinds = cur.fetchall()

        cur.execute("SELECT * FROM public.door")
        door = cur.fetchall()

        cur.execute("SELECT * FROM public.humidity")
        humidity = cur.fetchall()

        cur.execute("SELECT * FROM public.lamps")
        lamps = cur.fetchall()

        cur.execute("SELECT * FROM public.sunlight")
        sunlight = cur.fetchall()

        cur.execute("SELECT * FROM public.temperature")
        temperature = cur.fetchall()

        cur.execute("SELECT * FROM public.volumelevel")
        volume_level = cur.fetchall()

        conn.commit()
        conn.close()

        return render_template('dashboard.html', 
                               rooms=rooms, 
                               seat_occupied=seat_occupied, 
                               aircon=aircon, 
                               blinds=blinds, 
                               door=door, 
                               humidity=humidity, 
                               lamps=lamps, 
                               sunlight=sunlight, 
                               temperature=temperature, 
                               volume_level=volume_level)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error: {e}")
        return f"Database error: {e}", 500


@app.route('/api/data')
def sensor_data():
    # Simulierte Sensordaten – später ersetzen durch echte Werte
    data = {
        'temperature': round(random.uniform(20, 30), 2),
        'light': random.randint(300, 800),
        'humidity': round(random.uniform(40, 60), 1)
    }
    return jsonify(data)

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

def open_browser(url):
    """Open the web browser after a short delay to ensure Flask server is running."""
    time.sleep(1.5)  # Wait for Flask server to start
    webbrowser.open(url)

if __name__ == '__main__':
    port = 7000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"
    print(f"Starting Flask server at: {url}")
    
    # Start browser in a separate thread to avoid blocking Flask startup
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host="0.0.0.0", port=port, debug=True)