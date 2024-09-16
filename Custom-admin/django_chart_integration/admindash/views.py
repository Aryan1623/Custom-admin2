import pyrebase
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from datetime import datetime

# Firebase configuration
config = {
    "apiKey": "AIzaSyAwRFHuBqwMYm0fkf9tLDcMfYu8ciYe-Aw",
    "authDomain": "attendance3-1d9b0.firebaseapp.com",
    "databaseURL": "https://attendance3-1d9b0-default-rtdb.firebaseio.com/",
    "projectId": "attendance3-1d9b0",
    "storageBucket": "attendance3-1d9b0.appspot.com",
    "messagingSenderId": "864825196534",
    "appId": "1:864825196534:web:fabf918f8822faac6e91d7",
    "measurementId": "G-WWXHP64LSF"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def get_attendances_from_firebase():
    """
    Retrieve all attendance records from Firebase Realtime Database.
    """
    attendances = db.child("attendances").get().val()
    if attendances:
        return attendances
    return {}

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
@login_required
def dash(request):
    """
    Dashboard view to display all users' attendance percentage.
    """
    # Fetch data from Firebase
    firebase_data = get_attendances_from_firebase()
    
    # Transform the data into a format suitable for the template
    user_attendance = {}
    for key, value in firebase_data.items():
        user = value['user']
        attendance_status = value['status']
        
        if user not in user_attendance:
            user_attendance[user] = {
                'total_days': 0,
                'days_present': 0
            }
        
        user_attendance[user]['total_days'] += 1
        if attendance_status == 'present':
            user_attendance[user]['days_present'] += 1
    
    # Calculate the attendance percentage for each user
    for user, data in user_attendance.items():
        total_days = data['total_days']
        days_present = data['days_present']
        data['attendance_percent'] = (days_present / total_days) * 100 if total_days > 0 else 0
    
    # Convert the dictionary to a list of dictionaries for easier template rendering
    user_attendance_list = [
        {'user': user, 'attendance_percent': round(data['attendance_percent'], 2)}
        for user, data in user_attendance.items()
    ]

    context = {
        'user_attendance': user_attendance_list
    }

    return render(request, 'dash.html', context)

@login_required
def user_list_view(request):
    """
    View to list all users.
    """
    # Fetch all users
    users = User.objects.all()
    
    # Pass the user data to the template
    return render(request, 'user.html', {'users': users})

@login_required
def attendance(request, username):
    """
    View to display the attendance records of a specific user.
    """
    # Get the user object
    user = get_object_or_404(User, username=username)
    
    # Fetch the user's attendance records from Firebase
    firebase_data = db.child("attendances").get().val()
    
    # Prepare the user's attendance data
    attendance_data = []
    if firebase_data:
        # Extract attendance records specific to the user
        for key, value in firebase_data.items():
            if value.get('user') == username:
                attendance_data.append({
                    'user': value.get('user'),
                    'date': value.get('date'),
                    'status': value.get('status')
                })

    context = {
        'attendance_data': attendance_data,
        'username': username
    }

    return render(request, 'attendance.html', context)
