import pyrebase
import logging

# Firebase configuration
config = {
    "apiKey": "AIzaSyAwRFHuBqwMYm0fkf9tLDcMfYu8ciYe-Aw",
    "authDomain": "attendance3-1d9b0.firebaseapp.com",
    "databaseURL": "https://attendance3-1d9b0-default-rtdb.firebaseio.com/",  # Add your database URL here
    "projectId": "attendance3-1d9b0",
    "storageBucket": "attendance3-1d9b0.appspot.com",
    "messagingSenderId": "864825196534",
    "appId": "1:864825196534:web:fabf918f8822faac6e91d7",
    "measurementId": "G-WWXHP64LSF"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def save_attendance_to_firebase(attendance):
    """
    Save attendance data to Firebase Realtime Database.
    """
    data = {
        "user": attendance.user.username,  # Storing username for simplicity
        "date": attendance.date.strftime('%Y-%m-%d'),
        "status": attendance.status
    }
    # Using a composite key of user and date
    key = f"{attendance.user.username}_{attendance.date.strftime('%Y-%m-%d')}"
    db.child("attendances").child(key).set(data)

def get_user_attendances_from_firebase(username):
    """
    Retrieve attendance records for a specific user from Firebase Realtime Database.
    """
    try:
        all_attendances = db.child("attendances").get().val()
        if not all_attendances:
            return {}

        user_attendances = {}
        for key, value in all_attendances.items():
            if value['user'] == username:
                user_attendances[key] = value

        logging.info(f"Retrieved {len(user_attendances)} records for user: {username}")
        return user_attendances
    
    except Exception as e:
        logging.error(f"Error retrieving data from Firebase: {e}")
        return {}


