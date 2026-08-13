from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, TutorProfile, TimeSlot, Booking, Review
from core.payments import calculate_escrow_amount, process_test_payment, process_tutor_payout

class PeerTutorTestCase(TestCase):
    def setUp(self):
        # Create users for testing
        self.student = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='Password123!',
            role='student'
        )
        self.tutor_user = User.objects.create_user(
            username='tutor1',
            email='tutor1@test.com',
            password='Password123!',
            role='tutor'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin1',
            email='admin1@test.com',
            password='Password123!',
            role='admin'
        )

        # Create approved tutor profile
        self.tutor_profile = TutorProfile.objects.create(
            user=self.tutor_user,
            subjects='Python, Django, Data Structures',
            hourly_rate=50.00,
            github_link='https://github.com/tutor1',
            project_showcase='Built a full stack peer tutoring platform.',
            status='approved'
        )

        # Create available time slot
        self.slot = TimeSlot.objects.create(
            tutor=self.tutor_user,
            subject='Python',
            date='2026-09-01',
            start_time='10:00:00',
            end_time='11:00:00',
            is_booked=False
        )

    def test_payment_escrow_calculation(self):
        amount, commission = calculate_escrow_amount(50.00, 10.0)
        self.assertEqual(amount, 50.00)
        self.assertEqual(commission, 5.00)

    def test_test_mode_payment_gateway(self):
        success, txn_id = process_test_payment('4242-4242-4242-4242', '12/28', '123', 50.00)
        self.assertTrue(success)
        self.assertTrue(txn_id.startswith('TXN-ESCROW-'))

    def test_tutor_detail_view(self):
        response = self.client.get(reverse('tutor_detail', args=[self.tutor_profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tutor1')
        self.assertContains(response, 'Python, Django, Data Structures')

    def test_book_slot_flow(self):
        self.client.login(username='student1@test.com', password='Password123!')
        response = self.client.post(reverse('book_slot', args=[self.slot.id]), {
            'card_number': '4242-4242-4242-4242',
            'expiry': '12/28',
            'cvc': '123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify slot is marked booked and booking record created
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)
        booking = Booking.objects.get(slot=self.slot)
        self.assertEqual(booking.student, self.student)
        self.assertEqual(booking.status, 'pending')

    def test_payout_and_mutual_review(self):
        # Create booking and complete payout
        booking = Booking.objects.create(
            student=self.student,
            slot=self.slot,
            amount=50.00,
            commission=5.00,
            status='pending'
        )
        payout = process_tutor_payout(booking)
        self.assertEqual(payout, 45.00)
        self.assertEqual(booking.status, 'completed')

        # Student reviews Tutor
        self.client.login(username='student1@test.com', password='Password123!')
        response = self.client.post(reverse('add_review', args=[booking.id]), {
            'rating': 5,
            'comment': 'Great Python tutor!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
