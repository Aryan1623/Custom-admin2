import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Firebase configuration
cred = credentials.Certificate('config/serviceAccountKey.json')  # Update this path to match your file location
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance3-1d9b0-default-rtdb.firebaseio.com/'
})

def save_attendance_to_firebase(user, date, status):
    """
    Save attendance data to Firebase Realtime Database using a composite key of 'user_date'.
    """
    data = {
        "user": user,
        "date": date.strftime('%Y-%m-%d'),
        "status": status
    }
    # Create a unique key combining user and date
    key = f"{user}_{date.strftime('%Y-%m-%d')}"
    db.reference('attendances').child(key).set(data)
    print(f"Attendance record saved: {data}")

def get_attendance_data():
    """
    Fetch all attendance data from Firebase Realtime Database.
    """
    ref = db.reference('attendances')
    data = ref.get()
    return data

def get_user_attendance(username):
    """
    Fetch a specific user's attendance records from Firebase Realtime Database.
    """
    ref = db.reference('attendances')
    all_attendances = ref.get()

    if not all_attendances:
        return {}

    # Filter the attendance records for the given user
    user_attendance = {
        key: record for key, record in all_attendances.items()
        if record['user'] == username
    }
    return user_attendance

def add_test_data():
    """
    Add test data to Firebase Realtime Database.
    """
    test_data = [
        ("john_doe", datetime(2024, 9, 15), "present"),
        ("jane_doe", datetime(2024, 9, 16), "absent"),
        ("alice_smith", datetime(2024, 9, 17), "present"),
        ("bob_johnson", datetime(2024, 9, 18), "absent"),
        ("carol_doe", datetime(2024, 9, 19), "present")
    ]
    
    for user, date, status in test_data:
        save_attendance_to_firebase(user, date, status)

if __name__ == "__main__":
    # Add test data
    add_test_data()
