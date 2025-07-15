## RFID Simulation Script to simulate RFID tag reading and writing and to lock and open doors

import random
import time
import threading
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime

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
        return conn
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        return None

def get_data_from_db():
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_data")
            rfid_data = cursor.fetchall()
            return rfid_data
    except psycopg2.Error as e:
        print(f"Database query failed: {e}")
        return None
    finally:
        conn.close()
    return None

# class RFIDTag:
#     def __init__(self):
#         self.id = self.get_id()
#         self.data = {}
#         self.locked = False

#     def get_id(self):
#         # Get Id from the db
#         rfid_data = get_data_from_db()
#         if rfid_data:
#             self.id = rfid_data[0][0]
#             self.data = rfid_data[0][1]
#             return self.id
#         else:
#             return None
#         #return random.randint(100000, 999999)

#     def read(self):
#         if not self.locked:
#             return self.data
#         else:
#             return {"error": "Tag is locked"}

#     def write(self, data):
#         if not self.locked:
#             self.data = data
#             return {"status": "success"}
#         else:
#             return {"error": "Tag is locked"}

#     def lock(self):
#         self.locked = True
#         return {"status": "locked"}

#     def unlock(self):
#         self.locked = False
#         return {"status": "unlocked"}

# class Door:
#     def __init__(self):
#         self.locked = False

#     def lock(self):
#         self.locked = True
#         return {"status": "locked"}

#     def unlock(self):
#         self.locked = False
#         return {"status": "unlocked"}

#     def read(self):
#         if not self.locked:
#             return {"status": "unlocked"}
#         else:
#             return {"status": "locked"}
#     def open(self):
#         if not self.locked:
#             return {"status": "opened"}
#         else:
#             return {"error": "Door is locked, cannot open"}
#     def close(self):
#         return {"status": "closed"}

# class RFIDSimulation:
#     def __init__(self):
#         self.tag = RFIDTag()
#         self.door = Door()
#         self.log_file = "rfid_log.json"
#         self.lock = threading.Lock()

#     def simulate_read_tag(self):
#         with self.lock:
#             data = self.tag.read()
#             self.log_action("read_tag", data)
#             return data

#     def simulate_write_tag(self, data):
#         with self.lock:
#             result = self.tag.write(data)
#             self.log_action("write_tag", result)
#             return result

#     def simulate_lock_tag(self):
#         with self.lock:
#             result = self.tag.lock()
#             self.log_action("lock_tag", result)
#             return result

#     def simulate_unlock_tag(self):
#         with self.lock:
#             result = self.tag.unlock()
#             self.log_action("unlock_tag", result)
#             return result

#     def simulate_lock_door(self):
#         with self.lock:
#             result = self.door.lock()
#             self.log_action("lock_door", result)
#             return result

#     def simulate_unlock_door(self):
#         with self.lock:
#             result = self.door.unlock()
#             self.log_action("unlock_door", result)
#             return result

#     def simulate_open_door(self):
#         with self.lock:
#             result = self.door.open()
#             self.log_action("open_door", result)
#             return result

#     def simulate_close_door(self):
#         with self.lock:
#             result = self.door.close()
#             self.log_action("close_door", result)
#             return result

#     def log_action(self, action, data):
#         log_entry = {
#             "timestamp": datetime.now().isoformat(),
#             "action": action,
#             "data": data
#         }
#         with open(self.log_file, 'a') as f:
#             f.write(json.dumps(log_entry) + "\n")
#     def read_log(self):
#         with open(self.log_file, 'r') as f:
#             logs = f.readlines()
#         return [json.loads(log.strip()) for log in logs]
#     def clear_log(self):
#         with open(self.log_file, 'w') as f:
#             f.write("")
#         return {"status": "log cleared"}
#     def run_simulation(self):
#         # Example simulation sequence
#         print(self.simulate_write_tag({"name": "Cindy", "access_level": "admin"}))
#         print(self.simulate_read_tag())
#         print(self.simulate_lock_tag())
#         print(self.simulate_read_tag())
#         print(self.simulate_unlock_tag())
#         print(self.simulate_open_door())
#         print(self.simulate_lock_door())
#         print(self.simulate_close_door())
#         print(self.read_log())
#         print(self.clear_log())

# if __name__ == "__main__":

#     simulation = RFIDSimulation()
#     simulation.run_simulation()

# # This code simulates RFID tag reading and writing, locking and unlocking tags, and managing door states.
# # It also logs actions to a file and provides methods to read and clear the log.
# # The simulation can be extended or modified to include more complex behaviors or additional features as needed.
# # The RFIDTag and Door classes encapsulate the functionality of RFID tags and doors, respectively.
# # The RFIDSimulation class orchestrates the simulation and manages the interactions between tags and doors.
# # The script can be run directly, and it will execute a sequence of RFID operations, demonstrating the functionality.
# # The log file is stored in JSON format for easy readability and parsing.
# # The simulation can be extended with more features such as error handling, user authentication, or real-time monitoring.
# # The threading lock ensures that operations on the RFID tag and door are thread-safe, preventing data corruption or inconsistencies.
# # The simulation can be integrated with a user interface or a web service for real-time interaction.
# # The RFID tag ID is randomly generated, and the data can be modified as needed.