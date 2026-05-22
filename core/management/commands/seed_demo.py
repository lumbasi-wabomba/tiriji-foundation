from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    FeaturedPerson,
    ImpactMetric,
    InspirationVideo,
    PageMedia,
    SuccessStory,
    employees,
    events,
    gallery,
    partners,
    program,
    resources,
)


class Command(BaseCommand):
    help = 'Create or update demo content for the Tiriji Foundation site.'

    def handle(self, *args, **options):
        today = timezone.localdate()

        children_program, _ = program.objects.update_or_create(
            title='Children Education & Mentorship',
            defaults={
                'program_description': 'Scholarship support, mentorship circles, school visits, and confidence-building pathways for children and youth.',
                'image_url': '/static/images/hero-children.jpg',
                'two_week_fee': Decimal('12000.00'),
                'four_week_fee': Decimal('22000.00'),
                'eight_week_fee': Decimal('40000.00'),
                'extra_week_fee': Decimal('4500.00'),
            },
        )
        women_program, _ = program.objects.update_or_create(
            title='Women Enterprise & Leadership',
            defaults={
                'program_description': 'Training, peer mentorship, economic empowerment, and leadership support for women shaping their communities.',
                'image_url': '/static/images/hero-women.jpg',
                'two_week_fee': Decimal('14000.00'),
                'four_week_fee': Decimal('26000.00'),
                'eight_week_fee': Decimal('48000.00'),
                'extra_week_fee': Decimal('5200.00'),
            },
        )
        community_program, _ = program.objects.update_or_create(
            title='Regenerative Community Action',
            defaults={
                'program_description': 'Grassroots sustainability, tree planting, community education, and volunteer-led regenerative action.',
                'image_url': '/static/images/program-kenger.jpg',
                'two_week_fee': Decimal('10000.00'),
                'four_week_fee': Decimal('19000.00'),
                'eight_week_fee': Decimal('35000.00'),
                'extra_week_fee': Decimal('4000.00'),
            },
        )

        event_data = [
            ('Mentorship Field Day', children_program, today + timedelta(days=14), 'Meru County'),
            ('Women Enterprise Workshop', women_program, today + timedelta(days=28), 'Meru Town'),
            ('Community Regeneration Weekend', community_program, today + timedelta(days=42), 'Tiriji Field Site'),
        ]
        for title, linked_program, event_date, location in event_data:
            events.objects.update_or_create(
                title=title,
                defaults={
                    'events_description': f'{title} brings volunteers, coordinators, and community members together for practical learning and field action.',
                    'image_url': linked_program.image_url,
                    'program_id': linked_program,
                    'event_location': location,
                    'event_date': event_date,
                },
            )

        resource_data = [
            ('Program Impact Brief', children_program, '/static/resources/tiriji-program-brief.txt'),
            ('Volunteer Orientation Notes', community_program, '/static/resources/volunteer-orientation.txt'),
        ]
        for title, linked_program, file_url in resource_data:
            resources.objects.update_or_create(
                title=title,
                defaults={
                    'resources_description': f'{title} for demo users reviewing Tiriji Foundation programs and volunteer pathways.',
                    'image_url': linked_program.image_url,
                    'file_url': file_url,
                    'program_id': linked_program,
                },
            )

        for title, linked_program in [
            ('Scholar mentorship moment', children_program),
            ('Women leadership circle', women_program),
            ('Community planting day', community_program),
        ]:
            gallery.objects.update_or_create(
                title=title,
                defaults={
                    'image_description': f'Demo gallery item for {linked_program.title}.',
                    'image_url': linked_program.image_url,
                    'program_id': linked_program,
                },
            )

        employee, _ = employees.objects.update_or_create(
            email='coordination@tirijifoundation.com',
            defaults={
                'first_name': 'Tiriji',
                'last_name': 'Coordinator',
                'role': 'Program Coordinator',
                'phone_number': '+254795444556',
                'id_pass_no': 'DEMO-001',
                'starting_date': today,
                'residence': 'Meru',
                'emergency_contact_name': 'Operations Desk',
                'emergency_contact_phone': '+254795444556',
                'bio': 'Coordinates program operations, partners, volunteers, and community reporting for demo workflows.',
                'profile_image_url': '/static/images/team-placeholder-1.jpg',
            },
        )

        partner_data = [
            ('International Peace Initiatives', 'https://ipeacei.org/', '/static/images/partners/partner-ipi.png'),
            ('Nile Journeys', 'https://www.nilejourneys.org/', '/static/images/partners/partner-nile.png'),
            ('Impact Direct', 'https://impactdirect.eu/', '/static/images/partners/partner-id.png'),
            ('Gender Equity and Reconciliation International', 'https://www.genderreconciliationinternational.org/', '/static/images/partners/partner-geri.png'),
            ('Synergy Youth Kenya', 'https://www.synergykenya.org/', '/static/images/partners/partner-syk.png'),
            ('Naledi Initiative', 'https://nalediinitiative.org/', '/static/images/partners/partner-naledi.jpg'),
        ]
        for name, website_url, logo_url in partner_data:
            partners.objects.update_or_create(
                name=name,
                defaults={
                    'partners_description': f'{name} is part of Tiriji Foundation demo partner network.',
                    'profile_logo_url': logo_url,
                    'website_url': website_url,
                    'assigned_employee': employee,
                    'program_id': community_program,
                },
            )

        ImpactMetric.objects.update_or_create(
            page='children',
            label='Scholar mentorship touchpoints',
            defaults={'value': '120+', 'description': 'Demo metric for education support.', 'display_order': 1, 'is_active': True},
        )
        ImpactMetric.objects.update_or_create(
            page='women',
            label='Women trained through workshops',
            defaults={'value': '80+', 'description': 'Demo metric for enterprise support.', 'display_order': 1, 'is_active': True},
        )
        FeaturedPerson.objects.update_or_create(
            page='children',
            feature_type='scholar',
            name='Amina',
            defaults={
                'age': 13,
                'headline': 'Scholar of the Week',
                'short_bio': 'Amina represents the children mentorship pathway in this demo dataset.',
                'achievement': 'Improved school attendance and confidence.',
                'dream_or_goal': 'To become a teacher.',
                'quote': 'Mentorship helps me believe I can lead.',
                'image_url': '/static/images/hero-children.jpg',
                'is_featured': True,
            },
        )
        SuccessStory.objects.update_or_create(
            page='women',
            title='From workshop to local enterprise',
            defaults={
                'person_name': 'Grace',
                'challenge': 'Limited access to business mentorship.',
                'intervention': 'Enterprise training and peer support.',
                'outcome': 'Launched a small community business.',
                'quote': 'The workshop gave me practical confidence.',
                'image_url': '/static/images/hero-women.jpg',
                'is_featured': True,
            },
        )
        InspirationVideo.objects.update_or_create(
            page='children',
            title='Mentorship in action',
            defaults={
                'description': 'Demo video placeholder for inspirational storytelling.',
                'video_url': 'https://www.youtube.com/',
                'thumbnail_url': '/static/images/hero-children.jpg',
                'is_featured': True,
            },
        )
        PageMedia.objects.update_or_create(
            page='women',
            title='Women workshop demo media',
            defaults={
                'media_type': 'photo',
                'description': 'Demo media item for the women empowerment page.',
                'image_url': '/static/images/hero-women.jpg',
                'display_order': 1,
            },
        )

        self.stdout.write(self.style.SUCCESS('Demo content seeded successfully.'))
