# pyrefly: ignore [missing-import]
from enum import unique
#pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (('student','Student'), ('tutor','Tutor'), ('admin','Admin'))
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class TutorProfile(models.Model):
    STATUS_CHOICES = (('pending','Pending'), ('approved','Approved'),('rejected','Rejected'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    subjects = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits = 6, decimal_places = 2)
    marksheet = models.FileField(upload_to='marksheets/')
    github_link = models.URLField(blank = True)
    project_showcase = models.TextField(blank = True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
class TimeSlot(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'time_slots')
    subject = models.CharField(max_length = 100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default = False)
    def __str__(self):
        return f"{self.tutor.email} | {self.subject} | {self.date}"

class Booking(models.Model):
    STATUS_CHOICES = (('pending', 'Pending (Escrow)'), ('completed', 'Completed'), ('cancelled','Cancelled'))
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    commission = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()