# pyrefly: ignore [missing-import]
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TutorProfile, TimeSlot, Booking, Review
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(TutorProfile)
admin.site.register(TimeSlot)
admin.site.register(Booking)
admin.site.register(Review)