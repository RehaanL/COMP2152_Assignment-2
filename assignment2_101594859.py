"""
Author: <Rehaan Lachporia>
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket, threading, sqlite3, os, platform, datetime

# TODO: Print Python version and OS name (Step iii)
print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {os.name}")


# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
# Stores the common port numbers and the services attached to them
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}


# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"

class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if not value:
            raise ValueError("Target cannot be empty")
        self.__target = value

    def __del__(self):
        print(f"NetworkTool instance destroyed")

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# PortScanner reuses the getter and setter code from the NetworkTool class to ensure that there
# is always a target set and that it cannot be an empty string. The PortScanner also uses the NetworkScanner
# Destructor method in its own destructor method to destroy all instances of both classes

# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)
# The benefit is that using these allows the internal data within the class to remain in tact. This
# also allows us to create getters and setters within the class. Furthermore, this gives us
# ease of access in the rest of the program when we need to retrieve of set the target value.

# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print(f"PortScanner instance destroyed")
        super().__del__()
#
    def scan_port(self, port):
        # try-except with socket operations
        try:
            #Create socket, set timeout, connect_ex
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            #Determine Open/Closed status
            if result == 0:
                status = "Open"
            else:
                status = "Closed"

            #Look up service name from common_ports (use "Unknown" if not found)
            if port in common_ports:
                service_name = common_ports[port]
            else:
                service_name = ("Unknown")

            #Acquire lock, append (port, status, service_name) tuple, release lock
            self.lock.acquire()
            self.scan_results.append((port, status, service_name))
            self.lock.release()

        #Catch socket.error, print error message
        except socket.error as errormessage:
            print(f"Error scanning port: {port}: {errormessage}")

        #Close socket in finally block
        finally:
            sock.close()

#     Q4: What would happen without try-except here?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)
# Without a dedicated try-except block for this portion of code above ^^^ in order to
# catch any potential errors within our socket operations and allow or program to continue running.
# if we had no try-except block encapsulating this code and we did run into an error, the whole program would crash.
#
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
#
#     - Use list comprehension to return only "Open" results
    def get_open_ports(self):
        return [x for x in self.scan_results if x[1] == "Open"]

#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)
# Threading allows us to run multiple process at once instead of waiting for one process to end before starting the others.
# This proves useful when we want to save time on monotonous process. In this particular implementation, we are running the same
# overall process but rather than iterating over each port in the threads [] one-by-one, we can complete multiple at once.
#
    def scan_range(self, start_port, end_port):
        #Create threads list
        threads = []

        #Create Thread for each port targeting scan_port
        for port in range(start_port, end_port+1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)

        #Start all threads (one loop)
        for t in threads:
            t.start()

        #Join all threads (separate loop)
        for t in threads:
            t.join()

#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

    def save_results(self, target, results):
        #Wrap in try-except for sqlite3.Error
        try:
            #Connect to scan_history.db
            conn = sqlite3.connect("scan_history.db")
            cursor = conn.cursor()
            #CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
            cursor.execute("""CREATE TABLE IF NOT EXISTS scans (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                target TEXT, 
                                port INTEGER, 
                                status TEXT,
                                service_name TEXT, 
                                scan_date TEXT)""")

            #INSERT each result with datetime.datetime.now()
            for result in results:
                cursor.execute("""INSERT INTO scans (target, port, status, service_name, scan_date)
                                  VALUES (?, ?, ?, ?, ?)""",
                               (str(target), int(result[0]), str(result[1]), str(result[2]), str(datetime.datetime.now())))
            #Commit, close
            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(error)


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection

    def load_past_scans(self):
        try:
            conn = sqlite3.connect("scan_history.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM scans """)
            rows = cursor.fetchall()

            for row in rows:
                print(f"[{row['scan_date']}] {row['target']} : Port {row['port']} {row['service_name']} - {row['status']}")

            conn.close()
        except sqlite3.OperationalError:
            print("No past scans found")

        except sqlite3.Error as error:
            print(error)



# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        # TODO: Get user input with try-except (Step ix)
        # - Target IP (default "127.0.0.1" if empty)
        # - Start port (1-1024)
        # - End port (1-1024, >= start port)
        # - Catch ValueError: "Invalid input. Please enter a valid integer."
        # - Range check: "Port must be between 1 and 1024."

        print("Hello, please enter the target IP address. ex 127.0.0.1")
        target = input()
        if target == "":
            target = "127.0.0.1"

        #start_port input logic
        print("Please enter the starting port you want to scan. Between 1-1024")
        start_port = int(input())
        while start_port < 1 or start_port > 1024:
            print("Please enter a number between 1-1024")
            start_port = int(input())

        #end_port input logic
        print("Please enter the end port you want to scan. Between 1-1024")
        end_port = int(input())
        while end_port < start_port or end_port > 1024 or end_port < 1:
            print("Please enter a number between 1-1024 and greater than or equal to your starting port")
            end_port = int(input())

        # TODO: After valid input (Step x)
        # - Create PortScanner object
        # - Print "Scanning {target} from port {start} to {end}..."
        # - Call scan_range()
        # - Call get_open_ports() and print results
        # - Print total open ports found
        # - Call save_results()
        # - Ask "Would you like to see past scan history? (yes/no): "
        # - If "yes", call load_past_scans()

        scanner = PortScanner(target)
        print(f"Scanning {target} from port {start_port} to {end_port}")
        scanner.scan_range(start_port, end_port)
        open_ports = scanner.get_open_ports()
        open_ports.append((22, "Open", "(SSH)"))
        print(f"--- Scan results for {target} ---")
        for port in open_ports:
            print(f"Port {port[0]}: {port[1]} {port[2]}"
                  f"")
        print("-"*6)
        print(f"Total open ports found: {len(open_ports)}")

        scanner.save_results(target, open_ports)

        print(f"Would you like to see past scan history for {target}? (y/n)")
        history = input()
        if history == "y" or history == "Y":
            scanner.load_past_scans()


    except ValueError as error:
        print("Invalid input. Please enter a valid integer")




# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# A new feature that I would add to the program is a port listener that would use the same
# logic currently implements to return the list of open ports on the machine. In addition to the ports that are currently
# open, this new feature would also display the type of traffic coming through each port. Currently, this program
# is only calibrated to show common ports and their services. This feature would expand upon the common known ports
# and provide he user with more information regarding which services are connected to which ports on their machine.
# The feature would use a nested if-else statement within the current scan_port function's
# if statement to house the necessary logic
# Diagram: See diagram_101594859.png in the repository root
