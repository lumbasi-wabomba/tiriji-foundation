from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase
from django.urls import reverse

from .models import program, volunteer


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
