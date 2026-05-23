from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .forms import FeedbackForm
from .models import BlogPost, Transaction, VolunteerPayment, donation, feedback, program, volunteer
from .services.payment_service import PaymentService


class VolunteerFeeTests(SimpleTestCase):
    def test_fee_uses_selected_program_pricing(self):
        selected_program = program(
            title='Community Support',
            program_description='Support program',
            two_week_fee=Decimal('100.00'),
            four_week_fee=Decimal('180.00'),
            eight_week_fee=Decimal('320.00'),
            extra_week_fee=Decimal('45.00'),
        )
        applicant = volunteer(
            first_name='Amina',
            last_name='Otieno',
            email='amina@example.com',
            occupation='Teacher',
            phone_number='0700000000',
            id_pass_no='ABC123',
            starting_date=date(2026, 1, 1),
            end_date=date(2026, 3, 12),
            residence='Nairobi',
            emergency_contact_name='Jane',
            emergency_contact_phone='0711111111',
            program_id=selected_program,
        )

        self.assertEqual(applicant.duration_weeks, 10)
        self.assertEqual(applicant.fee, Decimal('410.00'))

    def test_string_handles_missing_program(self):
        applicant = volunteer(
            first_name='Amina',
            last_name='Otieno',
            email='amina@example.com',
            occupation='Teacher',
            phone_number='0700000000',
            id_pass_no='ABC123',
            starting_date=date(2026, 1, 1),
            end_date=date(2026, 1, 15),
            residence='Nairobi',
            emergency_contact_name='Jane',
            emergency_contact_phone='0711111111',
        )

        self.assertIn('No Program', str(applicant))


class AdminVolunteerUrlTests(SimpleTestCase):
    def test_admin_volunteer_actions_accept_email_keys(self):
        self.assertEqual(
            reverse('admin_volunteer_edit', args=['amina@example.com']),
            '/admin-portal/volunteers/amina@example.com/edit/',
        )
        self.assertEqual(
            reverse('admin_volunteer_delete', args=['amina@example.com']),
            '/admin-portal/volunteers/amina@example.com/delete/',
        )


class FormSanitizationTests(SimpleTestCase):
    def test_feedback_form_strips_html_and_normalizes_email(self):
        form = FeedbackForm(data={
            'name': '<b>Amina</b>',
            'email': 'AMINA@EXAMPLE.COM',
            'message': '<script>alert(1)</script>Hello\n\nworld',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['name'], 'Amina')
        self.assertEqual(form.cleaned_data['email'], 'amina@example.com')
        self.assertNotIn('<script>', form.cleaned_data['message'])


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicWorkflowTests(TestCase):
    def setUp(self):
        self.program = program.objects.create(
            title='Demo Mentorship',
            program_description='Mentorship program',
            two_week_fee=Decimal('1000.00'),
            four_week_fee=Decimal('1800.00'),
            eight_week_fee=Decimal('3200.00'),
            extra_week_fee=Decimal('400.00'),
        )

    def test_volunteer_submission_creates_payment_record(self):
        response = self.client.post(reverse('volunteer_signup'), {
            'first_name': 'Amina',
            'last_name': 'Otieno',
            'email': 'amina@example.com',
            'occupation': 'Teacher',
            'phone_number': '0700000000',
            'id_pass_no': 'ABC123',
            'residence': 'Meru',
            'starting_date': '2026-01-01',
            'end_date': '2026-01-15',
            'emergency_contact_name': 'Jane',
            'emergency_contact_phone': '0711111111',
            'program_id': self.program.program_id,
        })

        self.assertEqual(response.status_code, 302)
        applicant = volunteer.objects.get(email='amina@example.com')
        self.assertEqual(applicant.status, 'payment_pending')
        self.assertTrue(VolunteerPayment.objects.filter(volunteer=applicant).exists())

    def test_donation_demo_payment_can_complete(self):
        response = self.client.post(reverse('donate'), {
            'donor_name': 'Demo Donor',
            'donor_email': 'demo@example.com',
            'donor_phone_number': '0712345678',
            'donation_type': 'children',
            'donation_reason': 'Demo',
            'amount': '500.00',
            'payment_method': 'paypal',
        })

        self.assertEqual(response.status_code, 302)
        gift = donation.objects.get(donor_email='demo@example.com')
        self.assertEqual(gift.status, 'pending')
        self.assertEqual(gift.currency, 'USD')

        response = self.client.post(
            reverse('donation_payment', args=[gift.donation_id]),
            {'action': 'confirm_demo_payment'},
        )

        gift.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(gift.status, 'completed')
        self.assertEqual(gift.transaction.status, 'paid')

    def test_career_detail_renders_existing_demo_opening(self):
        response = self.client.get(reverse('career_detail', args=[1]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Volunteer Program Coordinator')

    def test_career_detail_404s_unknown_opening(self):
        response = self.client.get(reverse('career_detail', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_blog_listing_and_detail_render_published_posts(self):
        post = BlogPost.objects.create(
            title='Regenerative field note',
            excerpt='A short field note from Tiriji.',
            body='A longer story about community action.',
            is_published=True,
        )

        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.title)

        response = self.client.get(reverse('blog_detail', args=[post.blog_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A longer story')

    def test_blog_detail_404s_drafts(self):
        post = BlogPost.objects.create(
            title='Draft field note',
            excerpt='Draft excerpt',
            body='Draft body',
            is_published=False,
        )

        response = self.client.get(reverse('blog_detail', args=[post.blog_id]))
        self.assertEqual(response.status_code, 404)


@override_settings(SECURE_SSL_REDIRECT=False)
class AdminFeedbackWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
        )
        self.client.force_login(self.user)
        self.feedback = feedback.objects.create(
            name='Amina',
            email='amina@example.com',
            message='Please review this.',
        )

    def test_feedback_status_action_persists(self):
        response = self.client.get(reverse('admin_feedback_mark_resolved', args=[self.feedback.feedback_id]))

        self.feedback.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.feedback.status, 'resolved')

    def test_feedback_response_persists_message_and_timestamp(self):
        response = self.client.post(
            reverse('admin_feedback_respond', args=[self.feedback.feedback_id]),
            {'response_message': 'Thanks for reaching out.'},
        )

        self.feedback.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.feedback.status, 'addressed')
        self.assertEqual(self.feedback.response_message, 'Thanks for reaching out.')
        self.assertIsNotNone(self.feedback.responded_at)


class PaymentServiceTests(TestCase):
    def test_complete_donation_updates_transaction(self):
        transaction = Transaction.objects.create(
            amount=Decimal('250.00'),
            payment_method='bank',
            status='pending',
        )
        gift = donation.objects.create(
            donor_email='donor@example.com',
            amount=Decimal('250.00'),
            payment_method='bank',
            transaction=transaction,
        )

        PaymentService.complete_donation(gift)

        gift.refresh_from_db()
        transaction.refresh_from_db()
        self.assertEqual(gift.status, 'completed')
        self.assertEqual(transaction.status, 'paid')
        self.assertTrue(gift.payment_reference)

    def test_volunteer_session_uses_usd_currency(self):
        selected_program = program.objects.create(
            title='Demo',
            program_description='Demo program',
            two_week_fee=Decimal('100.00'),
            four_week_fee=Decimal('180.00'),
            eight_week_fee=Decimal('320.00'),
            extra_week_fee=Decimal('40.00'),
        )
        applicant = volunteer.objects.create(
            first_name='Amina',
            last_name='Otieno',
            email='amina-usd@example.com',
            occupation='Teacher',
            phone_number='0700000000',
            id_pass_no='ABC123',
            starting_date=date(2026, 1, 1),
            end_date=date(2026, 1, 15),
            residence='Nairobi',
            emergency_contact_name='Jane',
            emergency_contact_phone='0711111111',
            program_id=selected_program,
        )
        transaction = Transaction.objects.create(
            amount=Decimal('100.00'),
            payment_method='card',
            status='pending',
        )
        payment = VolunteerPayment.objects.create(
            volunteer=applicant,
            transaction=transaction,
            amount=Decimal('100.00'),
        )

        session = PaymentService.volunteer_session(payment, 'card')

        self.assertEqual(session['currency'], 'USD')
