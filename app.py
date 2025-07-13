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
import cryptography.fernet
import rsa
import hashlib

app = Flask(__name__, template_folder='template', static_folder='static')
socketio = SocketIO(app)

def get_connection():
    try:
        print("Attempting to connect to database...")
        conn = psycopg2.connect(
            database="SmartCities25",
            user="postgres",
            host="172.20.10.13",
            password="Tn#2SKSS25",
            port=5432,
            connect_timeout=10  # 10 second timeout
        )
        print("Database connection successful!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed (timeout/network): {e}")
        return None
    except Exception as e:
        print(f"Unexpected database error: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Styles/<filename>')
def serve_css(filename):
    return send_from_directory('static/Styles', filename)

@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    if not conn:
        # Fallback: Return dashboard with sample data when database is unavailable
        print("Database unavailable, using sample data")
        return render_template('dashboard.html', 
                               rooms=[], 
                               seat_occupied=[], 
                               aircon=[], 
                               blinds=[], 
                               door=[], 
                               humidity=[], 
                               lamps=[], 
                               sunlight=[], 
                               temperature=[], 
                               volume_level=[],
                               db_error=True)

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
                               volume_level=volume_level,
                               db_error=False)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error: {e}")
        return render_template('dashboard.html', 
                               rooms=[], 
                               seat_occupied=[], 
                               aircon=[], 
                               blinds=[], 
                               door=[], 
                               humidity=[], 
                               lamps=[], 
                               sunlight=[], 
                               temperature=[], 
                               volume_level=[],
                               db_error=True)


@app.route('/dashboard/booking')
def seat_booking():
    # Generate time slots for the booking form
    time_slots = generate_time_slots()
    
    conn = get_connection()
    if not conn:    
        # Fallback with sample data if database is unavailable
        sample_rooms = [
            {'id': 1, 'name': 'SR1', 'capacity': 20},
            {'id': 2, 'name': 'SR2', 'capacity': 15}
        ]
        sample_seats = [
            {'id': i, 'name': f'Seat {i}', 'room_id': 1, 'occupied': False} 
            for i in range(1, 21)
        ] + [
            {'id': i, 'name': f'Seat {i-20}', 'room_id': 2, 'occupied': False} 
            for i in range(21, 36)
        ]
        return render_template('bookingPopUp.html', rooms=sample_rooms, seats=sample_seats, time_slots=time_slots)
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.rooms")
        rooms = cur.fetchall()
        
        cur.execute("SELECT * FROM public.seatoccupied")
        seats = cur.fetchall()
        
        conn.close()
        
        return render_template('bookingPopUp.html', rooms=rooms, seats=seats, time_slots=time_slots)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error in booking: {e}")
        # Return with sample data on error
        sample_rooms = [
            {'id': 1, 'name': 'SR1', 'capacity': 20},
            {'id': 2, 'name': 'SR2', 'capacity': 15}
        ]
        return render_template('bookingPopUp.html', rooms=sample_rooms, seats=[], time_slots=time_slots)

@app.route('/admin')
def admin_page():
    # Generate time slots for the booking form
    time_slots = generate_time_slots()
    
    conn = get_connection()
    if not conn:    
        # Fallback with sample data if database is unavailable
        sample_rooms = [
            {'id': 1, 'name': 'SR1', 'capacity': 20},
            {'id': 2, 'name': 'SR2', 'capacity': 15}
        ]
        sample_seats = [
            {'id': i, 'name': f'Seat {i}', 'room_id': 1, 'occupied': False} 
            for i in range(1, 21)
        ] + [
            {'id': i, 'name': f'Seat {i-20}', 'room_id': 2, 'occupied': False} 
            for i in range(21, 36)
        ]
        return render_template('adminPage.html', rooms=sample_rooms, seats=sample_seats, time_slots=time_slots)

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.rooms")
        rooms = cur.fetchall()
        
        cur.execute("SELECT * FROM public.seatoccupied")
        seats = cur.fetchall()
        
        conn.close()

        return render_template('adminPage.html', rooms=rooms, seats=seats, time_slots=time_slots)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error in booking: {e}")
        # Return with sample data on error
        sample_rooms = [
            {'id': 1, 'name': 'SR1', 'capacity': 20},
            {'id': 2, 'name': 'SR2', 'capacity': 15}
        ]
        sample_seats = [
            {'id': i, 'name': f'Seat {i}', 'room_id': 1, 'occupied': False} 
            for i in range(1, 21)
        ] + [
            {'id': i, 'name': f'Seat {i-20}', 'room_id': 2, 'occupied': False} 
            for i in range(21, 36)
        ]
        return render_template('adminPage.html', rooms=sample_rooms, seats=sample_seats, time_slots=time_slots)

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

@app.route('/api/test-db')
def test_db():
    """Test database connectivity"""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            conn.close()
            return jsonify({"status": "success", "message": "Database connection successful", "result": result})
        except Exception as e:
            if conn:
                conn.close()
            return jsonify({"status": "error", "message": f"Database query failed: {e}"})
    else:
        return jsonify({"status": "error", "message": "Could not connect to database"})

@app.route('/api/book-seat', methods=['POST'])
def book_seat():
    try:
        data = request.get_json()
        seat_id = data.get('seatId')
        room_id = data.get('roomId')
        seat_name = data.get('seatName')
        
        if not seat_id or not room_id:
            return jsonify({'success': False, 'message': 'Missing seat or room ID'})
        
        conn = get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'})
        
        try:
            cur = conn.cursor()
            # Check if seat is already occupied
            cur.execute("SELECT * FROM public.seatoccupied WHERE roomid = %s AND seatid = %s", (room_id, seat_id))
            existing_booking = cur.fetchone()
            
            if existing_booking and existing_booking[3]:  # Assuming occupied status is at index 3
                return jsonify({'success': False, 'message': 'Seat is already occupied'})
            
            # Update or insert seat booking
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            if existing_booking:
                cur.execute("""
                    UPDATE public.seatoccupied 
                    SET status = 'occupied', date = %s 
                    WHERE roomid = %s AND seatid = %s
                """, (today, room_id, seat_id))
            else:
                cur.execute("""
                    INSERT INTO public.seatoccupied (roomid, seatid, status, date) 
                    VALUES (%s, %s, 'occupied', %s)
                """, (room_id, seat_id, today))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': f'Seat {seat_name} booked successfully'})
            
        except Exception as e:
            if conn:
                conn.close()
            print(f"Database error during booking: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
            
    except Exception as e:
        print(f"Booking API error: {e}")
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/data')
def sensor_data():
    # Simulierte Sensordaten – später ersetzen durch echte Werte
    data = {
        'temperature': round(random.uniform(20, 30), 2),
        'light': random.randint(300, 800),
        'humidity': round(random.uniform(40, 60), 1)
    }
    return jsonify(data)

@app.route('/api/light-level', methods=['POST'])
def update_light_level():
    try:
        data = request.get_json()
        level = data.get('level', 0)
        
        # You can store this in database if needed
        # For now, just return success
        level_names = ['Dark', 'Sunny', 'Very Sunny']
        level_name = level_names[level] if 0 <= level < len(level_names) else 'Unknown'
        
        return jsonify({
            'success': True,
            'level': level,
            'level_name': level_name
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/seating-plan')
def seating_plan():
    conn = get_connection()
    if not conn:
        # Return sample data if database is unavailable
        sample_data = [
            {'id': i, 'name': f'Seat {i}', 'occupied': random.choice([True, False]), 'room': 'SR1'}
            for i in range(1, 21)
        ]
        return jsonify(sample_data)
    
    try:
        cur = conn.cursor()
        # Get seat occupancy data
        cur.execute("SELECT roomid, seatid, status FROM public.seatoccupied WHERE roomid = %s", ('SR1',))
        seat_data = cur.fetchall()
        
        # Create seating plan
        seating_plan = []
        for i in range(1, 21):  # 20 seats for SR1
            occupied = False
            for seat in seat_data:
                if seat[1] == i and seat[2] == 'occupied':
                    occupied = True
                    break
            
            seating_plan.append({
                'id': i,
                'name': f'Seat {i}',
                'occupied': occupied,
                'room': 'SR1'
            })
        
        conn.close()
        return jsonify(seating_plan)
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error loading seating plan: {e}")
        # Return sample data on error
        sample_data = [
            {'id': i, 'name': f'Seat {i}', 'occupied': random.choice([True, False]), 'room': 'SR1'}
            for i in range(1, 21)
        ]
        return jsonify(sample_data)

def generate_time_slots():
    """Generate time slots in 5-minute intervals from 8:00 AM to 8:00 PM"""
    time_slots = []
    start_hour = 8  # 8 AM
    end_hour = 20   # 8 PM
    
    for hour in range(start_hour, end_hour + 1):
        for minute in range(0, 60, 5):  # 5-minute intervals
            # Format time as HH:MM
            time_str = f"{hour:02d}:{minute:02d}"
            time_slots.append(time_str)
    
    return time_slots

if __name__ == '__main__':
    port = 7000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"
    print(f"Starting Flask server at: {url}")
    
    # Start browser in a separate thread to avoid blocking Flask startup
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    # use socketio.run to start the Flask app to get real-time updates
    socketio.run(app, host="0.0.0.0", port=port, debug=True)