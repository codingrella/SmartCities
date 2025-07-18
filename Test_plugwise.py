##script to test plugwise functions

import serial
import serial.tools.list_ports
import sys
import time

def list_available_com_ports():
    """List all available COM ports"""
    print("Available COM ports:")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"  {port.device}: {port.description}")
    return [port.device for port in ports]

def test_com_port_access(port_name):
    """Test if we can access a specific COM port"""
    try:
        print(f"\nTesting access to {port_name}...")
        ser = serial.Serial(port_name, 115200, timeout=1)
        print(f"✓ Successfully opened {port_name}")
        ser.close()
        print(f"✓ Successfully closed {port_name}")
        return True
    except serial.SerialException as e:
        print(f"✗ Failed to access {port_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error with {port_name}: {e}")
        return False

def find_plugwise_device():
    """Try to find Plugwise device on available ports"""
    available_ports = list_available_com_ports()
    
    for port in available_ports:
        print(f"\nTrying to connect to Plugwise on {port}...")
        if test_com_port_access(port):
            try:
                # Try to initialize Plugwise connection
                from plugwise import Stick
                stick = Stick(port)
                print(f"✓ Plugwise device found on {port}")
                return port
            except Exception as e:
                print(f"✗ No Plugwise device on {port}: {e}")
    
    return None

def test_plugwise_connection(port, mac_address):
    """Test actual Plugwise connection"""
    try:
        print(f"\nTesting Plugwise connection on {port}...")
        from plugwise import Stick, Circle
        
        # Create stick connection
        stick = Stick(port)
        
        # Create circle connection
        circle = Circle(mac_address, stick)
        
        # Try to get power usage
        power = circle.get_power_usage()
        print(f"✓ Power usage: {power}W")
        
        return True
        
    except Exception as e:
        print(f"✗ Plugwise connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Plugwise Connection Diagnostic ===")
    
    # Step 1: List available ports
    available_ports = list_available_com_ports()
    
    if not available_ports:
        print("No COM ports found!")
        sys.exit(1)
    
    # Step 2: Test access to each port
    accessible_ports = []
    for port in available_ports:
        if test_com_port_access(port):
            accessible_ports.append(port)
    
    if not accessible_ports:
        print("\n❌ No accessible COM ports found!")
        print("Solutions:")
        print("1. Run as Administrator")
        print("2. Close other applications using COM ports")
        print("3. Check Device Manager for COM port conflicts")
        sys.exit(1)
    
    # Step 3: Try to find Plugwise device
    plugwise_port = find_plugwise_device()
    
    if plugwise_port:
        # Step 4: Test with your specific MAC address
        mac_address = "000D6F0005A9062F"
        test_plugwise_connection(plugwise_port, mac_address)
    else:
        print("\n❌ No Plugwise device found on any accessible port")

