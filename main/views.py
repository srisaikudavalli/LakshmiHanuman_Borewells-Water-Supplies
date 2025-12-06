from django.core.mail import send_mail
from datetime import datetime # <--- New import needed for calendar
from django.contrib.auth.decorators import user_passes_test # <--- Import this
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Sum # <--- New Import
from .models import Service, Review  # <-- We added Review here
from .forms import BookingForm
from .forms import BookingForm, ReviewForm
from .models import Worker, Attendance, Advance # <--- Add Advance
from .forms import BookingForm, ReviewForm, UserUpdateForm, ProfileUpdateForm

from .models import Service, Review, GalleryItem # <-- Import GalleryItem

# This line blocks anyone who is not logged in!

def home(request):
    services = Service.objects.all()
    reviews = Review.objects.all()
    gallery_items = GalleryItem.objects.all()
    
    return render(request, 'main/home.html', {
        'services': services, 
        'reviews': reviews,
        'gallery_items': gallery_items
    })

def success(request):
    return render(request, 'main/success.html')


def book_service(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # --- START EMAIL ALERT ---
            subject = f"🔔 New Booking Alert: {booking.customer_name}"
            message = f"""
            You have received a new order on your website!
            
            ------------------------------------
            👤 Customer: {booking.customer_name}
            📞 Phone:    {booking.phone_number}
            📍 Location: {booking.location}
            🛠 Service:  {booking.service}
            ------------------------------------
            
            Login to your Admin Panel to update the status.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'srisaikudavalli@gmail.com',    # From (Your Email)
                    ['srisaikudavalli@gmail.com'],  # To (Your Email - You get the alert)
                    fail_silently=False,
                )
                print("Email sent successfully!")
            except Exception as e:
                print(f"Error sending email: {e}")
            # --- END EMAIL ALERT ---

            return redirect('success')
    else:
        form = BookingForm()
    
    return render(request, 'main/book.html', {'form': form})
    
    return render(request, 'main/book.html', {'form': form})
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') # Go back to home after submitting
    else:
        form = ReviewForm()
    
    return render(request, 'main/review.html', {'form': form})
# --- AUTHENTICATION VIEWS ---

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # CHANGED MESSAGE HERE
            messages.success(request, "Account created successfully") 
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def login_user(request):
    # --- NEW CHECK: If already logged in, go straight to Home ---
    if request.user.is_authenticated:
        return redirect('home')
    # ------------------------------------------------------------

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                
                # Logic: If they just logged in now
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_user(request):
    logout(request)
    # CHANGED MESSAGE HERE
    messages.success(request, "Logged out successfully")
    return redirect('login') # It's better to go to Login page after logout

# --- WORKER DASHBOARD (ADMIN ONLY) ---

@user_passes_test(lambda u: u.is_superuser, login_url='home')
def worker_dashboard(request):
    workers = Worker.objects.all()
    
    # 1. HANDLE CALENDAR
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    present_worker_ids = Attendance.objects.filter(date=selected_date).values_list('worker_id', flat=True)

    # 2. SAVE ATTENDANCE & ADVANCE (POST REQUEST)
    if request.method == 'POST':
        for worker in workers:
            # A. Handle Attendance Checkbox
            is_present = request.POST.get(f'attendance_{worker.id}')
            if is_present == 'on':
                Attendance.objects.get_or_create(worker=worker, date=selected_date, defaults={'status': 'Present'})
            else:
                Attendance.objects.filter(worker=worker, date=selected_date).delete()

            # B. Handle Advance Input (NEW!)
            advance_amount = request.POST.get(f'advance_{worker.id}')
            if advance_amount and float(advance_amount) > 0:
                # Create a record for this advance
                Advance.objects.create(
                    worker=worker,
                    date=selected_date,
                    amount=advance_amount,
                    reason="Daily Entry"
                )
        
        messages.success(request, f"Data Updated for {selected_date}!")
        return redirect(f'/workers/?date={selected_date}')

    # 3. SALARY REPORT 
    salary_report = []
    for worker in workers:
        attendance_records = Attendance.objects.filter(worker=worker, status='Present').order_by('date')
        days_worked = attendance_records.count()
        work_pay = days_worked * worker.daily_wage
        dates_list = [record.date.strftime('%b %d') for record in attendance_records]
        
        advance_records = Advance.objects.filter(worker=worker).order_by('date')
        total_advance = advance_records.aggregate(Sum('amount'))['amount__sum'] or 0
        advance_list = [f"{adv.date.strftime('%b %d')}: ₹{int(adv.amount)}" for adv in advance_records]

        net_payable = work_pay - total_advance
        
        salary_report.append({
            'name': worker.name,
            'role': worker.role,
            'daily_wage': worker.daily_wage,
            'days_worked': days_worked,
            'dates_list': dates_list,
            'work_pay': work_pay,
            'advance_list': advance_list,
            'total_advance': total_advance,
            'net_payable': net_payable
        })

    return render(request, 'main/workers.html', {
        'workers': workers, 
        'selected_date': selected_date,
        'present_worker_ids': present_worker_ids,
        'salary_report': salary_report,
    })

@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'main/profile.html', context)