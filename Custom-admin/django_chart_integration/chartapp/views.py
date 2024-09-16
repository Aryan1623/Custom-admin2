from django.shortcuts import render, redirect
from .models import UserAttendance
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth import logout
from .firebase import save_attendance_to_firebase, get_user_attendances_from_firebase

# Create your views here.
def index(request):
    return render(request, 'chartapp/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format!')
            return render(request, 'chartapp/register.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'chartapp/register.html')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'User registered successfully!')
            return redirect('login')  # Redirect to login page
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'chartapp/register.html')
    else:
        return render(request, 'chartapp/register.html')

@login_required
def attendance_list(request):
    username = request.user.username  # Fetch the logged-in user's username

    # Get attendance data from Firebase
    attendances = get_user_attendances_from_firebase(username)
    
    # Convert data to a list and prepare for pagination
    attendance_list = [
        {'date': data['date'], 'status': data['status']}
        for key, data in attendances.items()
    ]

    # Pagination
    paginator = Paginator(attendance_list, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate attendance statistics
    present_days = sum(1 for record in attendance_list if record['status'] == 'Present')
    absent_days = sum(1 for record in attendance_list if record['status'] == 'Absent')
    total_days = present_days + absent_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    # Prepare data for charts
    monthly_attendance_data = {
        'labels': [],
        'data': []
    }
    # Populate `monthly_attendance_data` with data for the bar chart (optional)

    context = {
        'attendances': page_obj,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': attendance_percentage,
        'monthly_attendance_data': monthly_attendance_data,
    }
    
    return render(request, 'chartapp/attendence_list.html', context)

@login_required
def user_attendance_view(request):
    # Fetch all attendance records
    attendance_records = UserAttendance.objects.values('user').annotate(
        total_days=Count('id'),
        present_days=Count('id', filter=Q(status='Present'))
    )

    # Calculate attendance percentage for each user
    user_attendance_data = [
        {
            'user': record['user'],
            'attendance_percentage': (record['present_days'] / record['total_days'] * 100) if record['total_days'] > 0 else 0
        }
        for record in attendance_records
    ]
    
    # Render the data in a template
    return render(request, 'admin/user_attendance.html', {'user_attendance_data': user_attendance_data})

def custom_logout_view(request):
    logout(request)
    return redirect('index')  # Redirect to the home page after logging out

def custom_login_view(request):
    return redirect('index')
