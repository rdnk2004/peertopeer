# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.contrib.auth import login, logout, authenticate
# pyrefly: ignore [missing-import]
from django.contrib.auth.decorators import login_required
# pyrefly: ignore [missing-import]
from django.db import models, transaction
from django.db.models import Avg, Count, Q
from .models import User, TutorProfile, TimeSlot, Booking, Review
from .payments import calculate_escrow_amount, process_tutor_payout, process_test_payment

# 1. Homepage & Search (with Average Ratings R19 & Rating Filtering R9)
def home(request):
    query = request.GET.get('q', '')
    max_price = request.GET.get('price', '')
    min_rating = request.GET.get('rating', '')
    
    tutors = TutorProfile.objects.filter(status='approved').annotate(
        avg_rating=Avg('user__reviews_received__rating')
    )
    if query:
        tutors = tutors.filter(Q(subjects__icontains=query) | Q(user__username__icontains=query))
    if max_price:
        tutors = tutors.filter(hourly_rate__lte=max_price)
    if min_rating:
        tutors = tutors.filter(avg_rating__gte=float(min_rating))
        
    stats = {
        'active_tutors': TutorProfile.objects.filter(status='approved').count(),
        'completed_sessions': Booking.objects.filter(status='completed').count(),
    }
    return render(request, 'home.html', {
        'tutors': tutors,
        'stats': stats,
        'query': query,
        'max_price': max_price,
        'min_rating': min_rating
    })

def tutor_detail(request, tutor_id):
    tutor_profile = get_object_or_404(TutorProfile, id=tutor_id, status='approved')
    tutor_user = tutor_profile.user
    available_slots = TimeSlot.objects.filter(tutor=tutor_user, is_booked=False)
    reviews = Review.objects.filter(tutor=tutor_user).select_related('reviewer')
    
    context = {
        'profile': tutor_profile,
        'available_slots': available_slots,
        'reviews': reviews,
    }
    return render(request, 'tutor_detail.html', context)

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
    if user.role == 'admin' or user.is_superuser:
        context['pending_tutors'] = TutorProfile.objects.filter(status='pending')
        context['all_bookings'] = Booking.objects.all()
        context['total_commission'] = sum(b.commission for b in Booking.objects.filter(status='completed'))
    elif user.role == 'tutor':
        profile, _ = TutorProfile.objects.get_or_create(user=user, defaults={'hourly_rate': 0})
        context['profile'] = profile
        context['slots'] = TimeSlot.objects.filter(tutor=user)
        context['bookings'] = Booking.objects.filter(slot__tutor=user)
        completed = context['bookings'].filter(status='completed')
        context['total_earnings'] = sum(b.amount - b.commission for b in completed)
    else:  # Student
        context['bookings'] = Booking.objects.filter(student=user)
        
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

# 5. Slot Publishing & Escrow Booking
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
    slot = get_object_or_404(TimeSlot, id=slot_id)
    amount, commission = calculate_escrow_amount(slot.tutor.tutor_profile.hourly_rate)
    
    if slot.is_booked:
        return render(request, 'book_slot.html', {'slot': slot, 'error': 'This time slot has already been booked.'})

    if request.method == 'POST':
        card_number = request.POST.get('card_number', '')
        expiry = request.POST.get('expiry', '')
        cvc = request.POST.get('cvc', '')

        success, result = process_test_payment(card_number, expiry, cvc, amount)
        if not success:
            return render(request, 'book_slot.html', {
                'slot': slot,
                'amount': amount,
                'commission': commission,
                'error': result
            })

        # Atomic transaction + select_for_update to prevent double booking race conditions (R14)
        with transaction.atomic():
            locked_slot = TimeSlot.objects.select_for_update().get(id=slot_id)
            if locked_slot.is_booked:
                return render(request, 'book_slot.html', {
                    'slot': slot,
                    'error': 'Double-booking prevented: Another student claimed this slot just moments ago.'
                })
            
            Booking.objects.create(
                student=request.user,
                slot=locked_slot,
                amount=amount,
                commission=commission,
                transaction_id=result,
                status='pending'
            )
            locked_slot.is_booked = True
            locked_slot.save()

        return redirect('dashboard')

    return render(request, 'book_slot.html', {
        'slot': slot,
        'amount': amount,
        'commission': commission
    })

@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user == booking.student or request.user == booking.slot.tutor:
        process_tutor_payout(booking)
    return redirect('dashboard')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'cancelled'
    booking.slot.is_booked = False
    booking.slot.save()
    booking.save()
    return redirect('dashboard')

# 6. Mutual Ratings & Reviews (R16)
@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status='completed')
    
    if request.user == booking.student:
        target_user = booking.slot.tutor
        role_label = "Tutor"
    elif request.user == booking.slot.tutor:
        target_user = booking.student
        role_label = "Student"
    else:
        return redirect('dashboard')

    if Review.objects.filter(booking=booking, reviewer=request.user).exists():
        return redirect('dashboard')

    if request.method == 'POST':
        Review.objects.create(
            booking=booking,
            reviewer=request.user,
            tutor=target_user,
            rating=request.POST['rating'],
            comment=request.POST['comment']
        )
        return redirect('dashboard')

    return render(request, 'add_review.html', {
        'booking': booking,
        'target_user': target_user,
        'role_label': role_label
    })
