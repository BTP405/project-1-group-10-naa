import threading
import time
import mysql.connector
import vars;

class Database: 

    def __init__(self, 
                 conn_str : dict, 
                 maxInner : int, 
                 maxOuter : int) -> None:
        """
        * This class allows you to create a connection with a MySQL Database
        * and allows for operations such as:
            - Adding/Getting a Comment
            - Getting avaliable Parking spaces
            - Adding/Getting a User
            - Removing/Getting/Adding a Reservation
        
        Parameters:
        ------------
        * conn_str : dict
            The connection string needed to actually connect to a database
        * maxInner : int 
            The maximum amount of open parking spaces in the "inner" part of the lot
        * maxOuter : int
            The maximum amount of open parking spaces in the "outer" part of the lot
        
        Attributes:
        ------------
        * connection : PooledMySQLConnection
            - opens a pooled connection with the database
        * cursor : MySQLCursorAbstract
            - initializes a cursor to read and write to the database
        * maxInner : int
            - the number that will determine the amount of Slots in the "Inner" Parking spaces
        * maxOuter : int
            - the number that will determine the amount of Slots in the "Outer" Parking spaces
        * expirty_thread : threading.Thread
            - Replicates the behaviour of a TTL for a relation DB, will delete any outgoing expiries in the Reservations table 

        Example:
        from database import Database;
        conn_string = {
            "host": "your host",
            "database": "your db",
            "user": "your username",
            "password": "your password",
            "port": [your port number],
        }

        db = Database(conn_str=conn_string, maxInner=20, maxOuter=30);
        """
        self.connection = mysql.connector.connect(**conn_str)
        self.cursor = self.connection.cursor()
        self.maxInner = maxInner
        self.maxOuter = maxOuter
        
        self.expiry_thread = threading.Thread(target=self.__check_reservation_expiry)
        print(type(self.expiry_thread))
        #When main program ends, the thread will be finished 
        self.expiry_thread.daemon = True
        self.__createTables()
    
    def close_resources(self) -> None:
        """
        * This function closes the resources and ensures no loose ends left
        * by closing the cursor then the connection.
        * Ensures the cursor is closed before the connection.
        * (Should be called at the end of a program)
        Example:
        close_resources();
        """
        self.cursor.close()
        self.connection.close()

    
    def clear_cursor(self) -> None:
        """
        * Ensures no dangling data on the cursor by forcefully getting any remaining data
        * (Should be called after any modification/reading)
        """
        self.cursor.fetchall();
   
    def db_add_comment(self, 
                       comment : str, 
                       SlotID : int) -> None:
        """
        * Adds a comment assoicated with a specific Slot into the database. 
        * 
        Parameters:
        ------------
        * comment : str
            - The content of the 'comment' to be assoicated with a Slot
        * SlotID : int
            - the actual Slot that will be assoicated with a 'comment'
        """

        query = "INSERT INTO Comments (description, Slot_ID) VALUES (%s, %s)"
        self.cursor.execute(query, (comment, SlotID))
        self.connection.commit()
        print('Successfully added comment...')
        #Free any dangling values
        self.clear_cursor();

    def db_get_comments(self, 
                        SlotID : int) -> list:
        """
        * Grabs all comments assoicated from a specific Slot into the database. 
        * 
        Parameters:
        ------------
        * SlotID : int
            - the actual Slot that will be assoicated with a 'comment'
        """

        query = "SELECT * FROM Comments WHERE Slot_ID = %s"
        self.cursor.execute(query, (SlotID,))
        return self.cursor.fetchall()


    def db_get_available_locations(self, 
                                   condition:str = "all") -> list:
        """
        * Grabs all the free parking spaces that aren't reserved and are the type 'condition'

        Parameters:
        ------------
        * condition : str
            - The type of parking space to be returned
            - By default, is set to all types of parking spaces
        """
        
        match condition.lower():
            case "inner":
                query = "SELECT * FROM ParkingLots WHERE type = %s AND booked = %s";
                self.cursor.execute(query, ("inner", 0,));
            case "outer":
                query = "SELECT * FROM ParkingLots WHERE type = %s AND booked = %s";
                self.cursor.execute(query, ("outer", 0,));
            case _:
                query = "SELECT * FROM ParkingLots WHERE booked = %s";
                self.cursor.execute(query, (0,));
        return self.cursor.fetchall();


    def get_type_of_slot(self, 
                         slotID : int) -> tuple:
        
        """
        * Returns the type of a Slot ("inner" or "outer") from a given Slot

        Parameters:
        ------------
        * slotID : int
            - The specific slot to find which type it is
        """

        query = "SELECT type from ParkingLots WHERE SlotID = %s";
        self.cursor.execute(query, (slotID,));
        res = self.cursor.fetchone();
        self.clear_cursor();
        return res;

    def authenticate_user(self, 
                          username : str, 
                          password : str) -> tuple:
        """
        * Checks if the entered username and password exist in the Datbase. 
        * Return None if no user exists otherwise return the user as a tuple.

        Parameters:
        ------------
        * username : str
            - The username of the user
        * password : str
            - the password of the respective user
        """

        query = "SELECT username, password FROM Consumer WHERE username = %s AND password = %s";
        self.cursor.execute(query, (username, password,))
        res = self.cursor.fetchone();
        self.clear_cursor();
        return res;

    def db_get_user(self,
                 username : str) -> tuple:
        """
        * Ensures two users with the same username cannot exist

        Parameters:
        ------------
        * username : str
            - the username that will be registered
        """
        query = "SELECT username FROM Consumer WHERE username = %s"
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.clear_cursor();
        print(f'res is {res}')
        return res;


    def db_add_user(self, 
                    username : str, 
                    password : str) -> None:
        """
        * Adds a new user into the Consumer table 

        Parameters:
        ------------
        * username : str
            - the username to be added to the Database
        * password : str
            - the password to be added to the Database
        """

        if self.db_get_user(username):
            raise Exception("User already exists")
        query = "INSERT INTO Consumer (username, password) VALUES (%s, %s)"
        self.cursor.execute(query, (username, password))
        self.connection.commit()
        self.clear_cursor();

    
    def db_remove_reservation(self, 
                              Slot_ID : int) -> None:
        """
        * removes a reservation for a specific Slot from the Reservation table

        Parameters:
        ------------
        * Slot_ID : int
            - The slot being removed from the reservation 
        """

        query = "DELETE FROM Reservations WHERE Slot_ID = %s"
        self.cursor.execute(query, (Slot_ID,))
        query = "UPDATE ParkingLots SET booked = 0 WHERE SlotID = %s"
        self.cursor.execute(query, (Slot_ID,))
        self.connection.commit()
        print("Reservation removed successfully")
        self.clear_cursor();

    def db_get_your_reservations(self, 
                                 username : str) -> list:
        """
        * Returns a list of all the reservations associated to a user

        Parameters:
        ------------
        * condition : str
            - The type of parking space to be returned
            - By default, is set to all types of parking spaces
        """

        query = """
        SELECT r.* 
        FROM Reservations AS r
        INNER JOIN Consumer AS c ON c.username = %s
        WHERE r.userID = c.UID 
        """
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def db_add_reservation(self, 
                           username : str, 
                           slot_id : int, 
                           expiry_hours : int) -> None:
        """
        * MAY RAISE AN EXCEPTION 
        * (Use with try & Except)
        * Adds a reservation for a specific user to the Reservations table from the Database

        Parameters:
        ------------
        * username : str
            - the user that will actually be added to the Reservation table
        * slot_id : int
            - the slot that will be marked as booked and associated with the Reservation
        * expiry_hours : int   
            - the amount of time the user will have reserved in hours
        """

        #Ensure that the slot chosen is not already booked
        query = "SELECT booked FROM ParkingLots where SlotID = %s"
        self.cursor.execute(query, (slot_id,))
        #Grab the slot
        res = self.cursor.fetchone()
        self.clear_cursor();
        #If the booked value is 1 then it's already booked
        if res[0] == 1:
            raise Exception("Slot is already booked")

        #Select the hourly increase from the Price table and ensure it matches the type of the parking lot 
        query = "SELECT cost, hourly_increase FROM Price INNER JOIN ParkingLots ON Price.type = ParkingLots.type WHERE ParkingLots.SlotID = %s"
        self.cursor.execute(query, (slot_id,))
        price_info = self.cursor.fetchone()
        self.clear_cursor();

        if price_info:
            #Update the booked for the slot to set it as booked
            query = "UPDATE ParkingLots SET booked = 1 WHERE SlotID = %s";
            self.cursor.execute(query, (slot_id,));
            self.clear_cursor();
            cost, hourly_increase = price_info
            #Calculate the price
            initial_price = hourly_increase * expiry_hours
            insert_query = "INSERT INTO Reservations (price, expiry, Slot_ID, userID) VALUES (%s, DATE_ADD(NOW(), INTERVAL %s HOUR), %s, (SELECT UID FROM Consumer WHERE username = %s))"
            self.cursor.execute(insert_query, (initial_price, expiry_hours, slot_id, username))
            self.connection.commit()
            self.clear_cursor();
        else:
            raise Exception("Slot type not found in Price table")

        print("Reservation added successfully")


    def __createTables(self) -> None:
        """
        * Creates the Tables, 
        * initializes the data for the ParkingLots table 
        * and starts the expiry thread
        """

        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Consumer (
                    UID INT AUTO_INCREMENT PRIMARY KEY,
                    username varchar(30) NOT NULL,
                    password varchar(30) NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ParkingLots (
                    SlotID INT AUTO_INCREMENT PRIMARY KEY,
                    type varchar(10) NOT NULL,
                    booked BIT DEFAULT 0
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Comments (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    description varchar(250),
                    Slot_ID INT,
                    FOREIGN KEY (Slot_ID) REFERENCES ParkingLots(SlotID)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Price (
                    type varchar(10) PRIMARY KEY,
                    cost FLOAT,
                    hourly_increase FLOAT 
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Reservations (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    price FLOAT,
                    expiry DATETIME,
                    Slot_ID INT,
                    userID INT,
                    FOREIGN KEY (Slot_ID) REFERENCES ParkingLots(SlotID),
                    FOREIGN KEY (userID) REFERENCES Consumer(UID)
                )
            """)

            self.expiry_thread.start() #Start the expiry thread when the user first opens the application

            #If the tables already have values, skip this process
            #Used for when users start up the application multiple times
            #Avoids re-entering data upon re-opening application
            self.cursor.execute("SELECT * FROM ParkingLots")
            output = self.cursor.fetchone()
            self.clear_cursor();
            if output:
                print(f'output: {output}')
                print(f'Leaving Early... (as you should...)')
                return
            
            insertQuery = "INSERT INTO ParkingLots (type) VALUES (%s)"
            for i in range(1, self.maxInner + 1):
                self.cursor.execute(insertQuery, ("inner",))

            for i in range(1, self.maxOuter + 1):
                self.cursor.execute(insertQuery, ("outer",))
            
            insertQuery = "INSERT INTO Price (type, cost, hourly_increase) VALUES (%s, %s, %s)"

            self.cursor.execute(insertQuery, ("inner", 20.25, 2.35))
            self.cursor.execute(insertQuery, ("outer", 30.19, 4.32))
            
            self.connection.commit();
        except Exception as e:
            print("Error in initialize_db:", e)

    def __check_reservation_expiry(self) -> None:
        """
        * Replicate TLL behaviour, 
        *   create a seperate connection and cursor as to not get in the way of the 
        *   main cursor and connection. (also incase of any errors)
        *   -> Delete any expiries that have already passed
        *   -> Update their booked status back to 0
        *   -> Sleep for 3hrs
        *   -> Close the connection everything is done
        """

        conn = None
        cursor = None
        try:
            # Create a new connection and cursor inside the thread
            conn = mysql.connector.connect(**vars.connection_string)
            cursor = conn.cursor()

            while True:
                try:
                    # Your existing code for handling reservations expiry
                    query = "DELETE FROM Reservations WHERE expiry <= NOW()"
                    cursor.execute(query)
                    query = "UPDATE ParkingLots SET booked = 0 WHERE SlotID NOT IN (SELECT Slot_ID FROM Reservations)"
                    cursor.execute(query)
                    conn.commit()
                    time.sleep(3600 * 3)  # Sleep for 3 hours
                except Exception as e:
                    print("Error in check_reservation_expiry:", e)
        finally:
            # Close the cursor and connection when the thread exits
            if cursor:
                cursor.close()
            if conn:
                conn.close()

