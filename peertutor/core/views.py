# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.contrib.auth import login, logout, authenticate
# pyrefly: ignore [missing-import]
from django.contrib.auth.decorators import login_required
# pyrefly: ignore [missing-import]
from django.db.models import Avg, Count, Q
# pyrefly: ignore [missing-import]
from .models import User, TutorProfile, TimeSlot, Booking, Review

# 1. Homepage & Search
def home(request):
    query = request.GET.get('q', '')
    max_price = request.GET.get('price', '')
    
    tutors = TutorProfile.objects.filter(status='approved')
    if query:
        tutors = tutors.filter(Q(subjects__icontains=query) | Q(user__first_name__icontains=query))
    if max_price:
        tutors = tutors.filter(hourly_rate__lte=max_price)
        
    stats = {
        'active_tutors': TutorProfile.objects.filter(status='approved').count(),
        'completed_sessions': Booking.objects.filter(status='completed').count(),
    }
    return render(request, 'home.html', {'tutors': tutors, 'stats': stats, 'query': query})

# 2. Registration & Authentication
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role', 'student')
        
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

# 3. Role-Based Dashboard
@login_required
def dashboard(request):
    user = request.user
    context = {}
    if user.role == 'student':
        context['bookings'] = Booking.objects.filter(student=user)
    elif user.role == 'tutor':
        profile, _ = TutorProfile.objects.get_or_create(user=user, defaults={'hourly_rate': 0})
        context['profile'] = profile
        context['slots'] = TimeSlot.objects.filter(tutor=user)
        context['bookings'] = Booking.objects.filter(slot__tutor=user)
        # Calculate total earnings minus 10% commission
        completed = context['bookings'].filter(status='completed')
        context['total_earnings'] = sum(b.amount - b.commission for b in completed)
    elif user.role == 'admin' or user.is_superuser:
        context['pending_tutors'] = TutorProfile.objects.filter(status='pending')
        context['all_bookings'] = Booking.objects.all()
        context['total_commission'] = sum(b.commission for b in Booking.objects.filter(status='completed'))
    return render(request, 'dashboard.html', context)

# 4. Tutor Profile Submission & Admin Verification
@login_required
def apply_tutor(request):
    if request.method == 'POST':
        profile, _ = TutorProfile.objects.get_or_create(user=request.user)
        profile.subjects = request.POST['subjects']
        profile.hourly_rate = request.POST['hourly_rate']
        profile.github_link = request.POST.get('github_link', '')
        profile.project_showcase = request.POST.get('project_showcase', '')
        if 'marksheet' in request.FILES:
            profile.marksheet = request.FILES['marksheet']
        profile.status = 'pending'
        profile.save()
        return redirect('dashboard')
    return render(request, 'apply_tutor.html')

@login_required
def verify_tutor(request, profile_id, action):
    if request.user.role == 'admin' or request.user.is_superuser:
        profile = get_object_or_404(TutorProfile, id=profile_id)
        profile.status = 'approved' if action == 'approve' else 'rejected'
        profile.save()
    return redirect('dashboard')

# 5. Slot Publishing & Booking (Escrow Payment)
@login_required
def add_slot(request):
    if request.user.role == 'tutor' and request.user.tutor_profile.status == 'approved':
        if request.method == 'POST':
            TimeSlot.objects.create(
                tutor=request.user,
                subject=request.POST['subject'],
                date=request.POST['date'],
                start_time=request.POST['start_time'],
                end_time=request.POST['end_time']
            )
            return redirect('dashboard')
    return render(request, 'add_slot.html')

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id, is_booked=False)
    if request.method == 'POST':
        # Simulate payment gateway success
        amount = slot.tutor.tutor_profile.hourly_rate
        commission = amount * 10 / 100  # 10% platform fee
        Booking.objects.create(
            student=request.user,
            slot=slot,
            amount=amount,
            commission=commission,
            status='pending'  # Escrow state
        )
        slot.is_booked = True
        slot.save()
        return redirect('dashboard')
    return render(request, 'book_slot.html', {'slot': slot})

@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user == booking.student or request.user == booking.slot.tutor:
        booking.status = 'completed'  # Releases escrow payout
        booking.save()
    return redirect('dashboard')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'cancelled'
    booking.slot.is_booked = False
    booking.slot.save()
    booking.save()
    return redirect('dashboard')
