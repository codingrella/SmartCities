from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
from flask_socketio import SocketIO, emit as socketio
import random
import json
import socket
import webbrowser
import psycopg2
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():


@app.route('/booking', methods=['GET', 'POST'])
def booking_seat():
    room_id = request.form.get('roomid')
    seat_id = int(request.form.get('seatid'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.seatoccupied WHERE roomid = %s AND seatid = %s", (room_id, seat_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# @app.route('/api/data')
# def sensor_data():
#     # Simulierte Sensordaten – später ersetzen durch echte Werte
#     data = {
#         'temperature': round(random.uniform(20, 30), 2),
#         'light': random.randint(300, 800),
#         'humidity': round(random.uniform(40, 60), 1)
#     }
#     return jsonify(data)

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

if __name__ == '__main__':
    port = 7000,
    local_ip = get_local_ip(),
    url = f"http://{local_ip}:{port}"
    webbrowser.open(url)
    socketio.run(app, host="0.0.0.0", port=7000, debug=False)


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
    # """Get the local IP address of the current machine."""
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try:
    #     # Doesn't have to be reachable
    #     s.connect(("10.255.255.255", 1))
    #     IP = s.getsockname()[0]
    # except Exception:
    #     IP = "127.0.0.1"
    # finally:
    #     s.close()
    # return IP

# def reset_seat_status():
#     conn = get_connection()
#     # reset the seat status every day at midnight
#     today = datetime.today().strftime("%Y-%m-%d")
#     cur = conn.cursor()
#     cur.execute("UPDATE public.seatoccupied SET status = 'free' WHERE date != %s", (today,))
#     conn.commit()
#     cur.close()
#     conn.close()
    