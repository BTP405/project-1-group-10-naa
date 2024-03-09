from database import Database
import vars

# Connect to the database
db = Database(conn_str=vars.connection_string, maxInner=20, maxOuter=30)

def get_spots(location):
    try:
        return db.db_get_available_locations(location)
    except Exception as e:
        print("Error adding comment:", e)
        return None


def add_comment(comment, SlotID):
    """
    Add a comment for a specific parking slot.

    Parameters:
    - comment: str, the content of the comment
    - SlotID: int, the ID of the specific parking slot

    Example:
    add_comment(comment="This is a test comment", SlotID=1)
    """
    try:
        db.db_add_comment(comment=comment, SlotID=SlotID)
        print("Comment added successfully.")
    except Exception as e:
        print("Error adding comment:", e)

def get_available_locations(condition="all"):
    """
    Get available parking locations based on condition.

    Parameters:
    - condition: str, optional, condition for filtering parking locations (default: "all")

    Returns:
    - list of tuples containing available parking locations

    Example:
    available_inner = get_available_locations(condition="inner")
    available_outer = get_available_locations(condition="outer")
    """
    try:
        return db.db_get_available_locations(condition=condition)
    except Exception as e:
        print("Error getting available locations:", e)
        return []

def add_user(username, password):
    """
    Add a user to the database.

    Parameters:
    - username: str, the username of the user
    - password: str, the password of the user

    Example:
    add_user(username="testuser", password="testpassword")
    """
    try:
        db.db_add_user(username=username, password=password)
        print("User added successfully.")
        return True
    except Exception as e:
        print("Error adding user:", e)
        return False

def get_user(username,password):
    """
    Get user information based on username.

    Parameters:
    - username: str, the username of the user

    Returns:
    - tuple containing user information if found, None otherwise

    Example:
    user = get_user(username="testuser")
    """
    try:
        return db.authenticate_user(username=username,password=password)
    except Exception as e:
        print("Error getting user information:", e)
        return None

def add_reservation(username, slot_id, expiry_hours):
    """
    Add a reservation for a user.

    Parameters:
    - username: str, the username of the user making the reservation
    - slot_id: int, the ID of the parking slot to reserve
    - expiry_hours: int, the number of hours until the reservation expires

    Example:
    add_reservation(username="testuser", slot_id=1, expiry_hours=2)
    """
    try:
        db.db_add_reservation(username=username, slot_id=slot_id, expiry_hours=expiry_hours)
        print("Reservation added successfully.")
        return True
    except Exception as e:
        print("Error adding reservation:", e)
        return False

def get_reservations(username):
    """
    Get reservations for a specific user.

    Parameters:
    - username: str, the username of the user

    Returns:
    - list of tuples containing reservations for the user

    Example:
    reservations = get_reservations(username="testuser")
    """
    try:
        return db.db_get_your_reservations(username=username)
    except Exception as e:
        print("Error getting reservations:", e)
        return []

def remove_reservation(Slot_ID):
    """
    Remove a reservation for a parking slot.

    Parameters:
    - Slot_ID: int, the ID of the parking slot to remove the reservation for

    Example:
    remove_reservation(Slot_ID=1)
    """
    try:
        db.db_remove_reservation(Slot_ID=Slot_ID)
        print("Reservation removed successfully.")
    except Exception as e:
        print("Error removing reservation:", e)

def close_database_connection():
    """
    Close the database connection.
    
    Example:
    close_database_connection()
    """
    db.close_resources()