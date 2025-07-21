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
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='template', static_folder='static')
socketio = SocketIO(app)


def get_connection_to_db():
    try:
        print("Attempting to connect to database...")
        conn = psycopg2.connect(
            database="SmartCities25",
            user="postgres",
            host="192.168.153.247",
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
    
@app.route('/user')
def user_page():
    return render_template('userPage.html')

@app.route('/validate_user', methods=['POST'])
def validate_user():
    data = request.get_json()
    userId = data.get('userId')
    password = data.get('password')

    conn = get_connection_to_db()
    if not conn:
        return jsonify({"valid": False, "error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.users WHERE userid = %s", (userId,))
        user = cur.fetchone()

        if user and check_password_hash(user[1], password):  # Assuming password is in the 2nd column
            #print(f"User {userId} validated successfully.")
            return jsonify({"valid": True}), 200
        else:
            return jsonify({"valid": False}), 401
    except Exception as e:
        print(f"Error validating user: {e}")
        return jsonify({"valid": False, "error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Styles/<filename>')
def serve_css(filename):
    return send_from_directory('static/Styles', filename)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/booking')
def seat_booking():
    # Generate time slots for the booking form
    time_slots = generate_time_slots()
    
    conn = get_connection_to_db()
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.rooms")
        rooms = cur.fetchall()
        
        cur.execute("SELECT * FROM public.seats")
        seats = cur.fetchall()
        
        conn.close()
        
        return render_template('bookingPopUp.html', rooms=rooms, seats=seats, time_slots=time_slots)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error in booking: {e}")

@app.route('/admin')
def admin_page():
    # Generate time slots for the booking form
    time_slots = generate_time_slots()
    
    conn = get_connection_to_db()
    if not conn:
        # Fallback: Return admin page with empty data when database is unavailable
        print("Database unavailable, using empty data for admin page")
        return render_template('adminPage.html', rooms=[], seats=[], time_slots=time_slots)

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.rooms")
        rooms = cur.fetchall()
        
        cur.execute("SELECT * FROM public.seats")
        seats = cur.fetchall()
        
        conn.close()

        return render_template('adminPage.html', rooms=rooms, seats=seats, time_slots=time_slots)
    except Exception as e:
        if conn:
            conn.close()
        print(f"Database error in booking: {e}")

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

@app.route('/api/book-seat', methods=['POST'])
def book_seat():
    try:
        data = request.get_json()
        room_id = "SR_1"
        user_id = data.get('userId')
        # seat_id to string to "Seat_1_01"
        # bookedseat = data.get('bookedseat').split()[-1]  # Get the last part of the string
        bookedseat = f"Seat_1_{str(data.get('bookedseat').split()[-1])}"
        print(f"Booked seat: {bookedseat}")
        seat_id = str(bookedseat)
        startTime = data.get('startTime')
        endTime = data.get('endTime')

        if not seat_id:
            return jsonify({'success': False, 'message': 'Missing seat ID'})

        conn = get_connection_to_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'})
        
        try:
            cur = conn.cursor()

            # First, ensure we have a valid user_id
            if user_id and user_id != 'anonymous':
                # Check if user exists
                cur.execute("SELECT userid FROM public.users WHERE userid = %s", (user_id,))
                if not cur.fetchone():
                    # User doesn't exist, create a temporary one or use anonymous
                    user_id = 'anonymous'
            
            cur.execute("""
                UPDATE public.seats 
                SET isoccupied = TRUE
                WHERE roomid = %s AND seatid = %s
            """, (room_id, seat_id))
            # else:
            cur.execute("""
                INSERT INTO public.seatbookings (userid, bookedseat, starttime, endtime) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, bookedseat, startTime, endTime))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': f'Seat {seat_id} booked successfully'})

        except Exception as e:
            if conn:
                conn.close()
            print(f"Database error during booking: {e}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
            
    except Exception as e:
        print(f"Booking API error: {e}")
        return jsonify({'success': False, 'message': 'Server error'})

# @app.route('/api/data')
# def sensor_data():
    
#     # Simulierte Sensordaten – später ersetzen durch echte Werte
#     # data = {
#     #     'temperature': round(random.uniform(20, 30), 2),
#     #     'light': random.randint(300, 800),
#     #     'humidity': round(random.uniform(40, 60), 1)
#     # }
#     return jsonify(data)

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
    conn = get_connection_to_db()
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
        cur.execute("""SELECT roomid, seatid, isoccupied FROM public.seats WHERE roomid = 'SR_1' 
                    ORDER BY seatid""")
        seat_data = cur.fetchall()
        print(seat_data)

        # Create seating plan
        seating_plan = []
        
        for i in range(1,13):
            # get occupancy status for each seat from the database
            occupied = seat_data[i-1][2]
            seating_plan.append({
                #'id': i,
                'name': f'Seat {str(i).zfill(2)}',
                'occupied': occupied,
                'room': 'SR1'
            })
        conn.close()
        #print(seating_plan)
        return seating_plan
        #print(seating_plan)
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error loading seating plan: {e}")
        # Return sample data on error
        # sample_data = [
        #     {'id': i, 'name': f'Seat {i}', 'occupied': random.choice([True, False]), 'room': 'SR1'}
        #     for i in range(1, 21)
        # ]
        # return jsonify(sample_data)

@app.route('/api/get-booking-info', methods=['GET'], )
def get_booking_info():
    try:
        data = request.get_json()
        seat_id = f"Seat_1_{str(data.get('seat').split()[-1])}"
        # room_id = request.args.get('roomId')

        # Fetch booking info from the database
        conn = get_connection_to_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500

        cur = conn.cursor()
        cur.execute("SELECT * FROM public.seatbookings WHERE bookedseat = %s", (seat_id,))
        booking_info = cur.fetchall()
        print(f"Booking info for seat {seat_id}: {booking_info}")
        conn.close()

        if booking_info:
            return jsonify({'success': True, 'data': booking_info})
        else:
            return jsonify({'success': False, 'message': 'No booking found'}), 404

    except Exception as e:
        print(f"Error fetching booking info: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    
@app.route('/api/delete-booking', methods=['POST'],)
def delete_booking():
    try:
        data = request.get_json()
        seat_id = f"Seat_1_{str(data.get('bookedseat').split()[-1])}"
        conn = get_connection_to_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        cur = conn.cursor()
        # Delete booking from the database  
        cur.execute("DELETE FROM public.seatbookings WHERE bookedseat = %s", (seat_id,))
        conn.commit()
        cur.execute("""UPDATE public.seats SET isoccupied = FALSE WHERE seatid = %s""", (seat_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Booking for seat {seat_id} deleted successfully'})
    except Exception as e:
        print(f"Error deleting booking: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

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
    socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=False)