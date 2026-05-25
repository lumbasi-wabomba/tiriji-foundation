from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    BlogPost,
    FeaturedPerson,
    ImpactMetric,
    InspirationVideo,
    PageMedia,
    SuccessStory,
    employees,
    events,
    gallery,
    news as News,
    partners,
    program,
    resources,
)


class Command(BaseCommand):
    help = 'Create or update demo content for the Tiriji Foundation site.'

    def handle(self, *args, **options):
        today = timezone.localdate()

        children_program, _ = program.objects.update_or_create(
            title="Kithoka Amani Children's Home",
            defaults={
                'program_description': (
                    "Kithoka Amani Children's Home creates a nurturing pathway where children can grow, learn, heal, and flourish. "
                    "The program combines daily care, education support, emotional wellbeing, mentorship, and family/community reintegration where appropriate."
                ),
                'image_url': '/static/images/IMG-20260522-WA0018.jpg',
                'two_week_fee': Decimal('240.00'),
                'four_week_fee': Decimal('440.00'),
                'eight_week_fee': Decimal('800.00'),
                'extra_week_fee': Decimal('90.00'),
            },
        )
        women_program, _ = program.objects.update_or_create(
            title='Women Empowerment Program',
            defaults={
                'program_description': (
                    "Tiriji invests in regenerative social enterprises that strengthen the lives of women and girls. "
                    "The program supports women groups, seed funding, weaving skills, local enterprise, and economic independence."
                ),
                'image_url': '/static/images/hero-women-2.jpg',
                'two_week_fee': Decimal('280.00'),
                'four_week_fee': Decimal('520.00'),
                'eight_week_fee': Decimal('960.00'),
                'extra_week_fee': Decimal('105.00'),
            },
        )
        community_program, _ = program.objects.update_or_create(
            title='Regenculture & Community Action',
            defaults={
                'program_description': (
                    "Community action at Tiriji links people, resources, and tools into regenerative, sustainable, resilient, and flourishing local systems. "
                    "Field work includes food systems, ecology, community learning, and practical service."
                ),
                'image_url': '/static/images/IMG-20260522-WA0016.jpg',
                'two_week_fee': Decimal('200.00'),
                'four_week_fee': Decimal('380.00'),
                'eight_week_fee': Decimal('700.00'),
                'extra_week_fee': Decimal('80.00'),
            },
        )
        ngl_program, _ = program.objects.update_or_create(
            title='Now Generation Leaders & EDE',
            defaults={
                'program_description': (
                    "The Now Generation Leaders and Ecovillage Design Education pathways help young people practice leadership, ecological design, "
                    "cross-cultural learning, and community project implementation rooted in local wisdom."
                ),
                'image_url': '/static/images/IMG-20260522-WA0037.jpg',
                'two_week_fee': Decimal('300.00'),
                'four_week_fee': Decimal('580.00'),
                'eight_week_fee': Decimal('1080.00'),
                'extra_week_fee': Decimal('120.00'),
            },
        )
        vocational_program, _ = program.objects.update_or_create(
            title='Vocational Skills Training Centre',
            defaults={
                'program_description': (
                    "The vocational centre prepares learners for practical livelihoods through certificate-level training such as hairdressing and beauty therapy, "
                    "catering and hospitality, and fashion and design."
                ),
                'image_url': '/static/images/program-kenger.jpg',
                'two_week_fee': Decimal('260.00'),
                'four_week_fee': Decimal('500.00'),
                'eight_week_fee': Decimal('920.00'),
                'extra_week_fee': Decimal('100.00'),
            },
        )
        wellness_program, _ = program.objects.update_or_create(
            title='Wellness Services',
            defaults={
                'program_description': (
                    "Tiriji treats wellness as a community foundation. The wellness pathway includes health-conscious services, yoga sessions, herbal knowledge, "
                    "and restorative practices that help people and communities thrive."
                ),
                'image_url': '/static/images/hero-women.jpg',
                'two_week_fee': Decimal('220.00'),
                'four_week_fee': Decimal('420.00'),
                'eight_week_fee': Decimal('780.00'),
                'extra_week_fee': Decimal('85.00'),
            },
        )
        guest_program, _ = program.objects.update_or_create(
            title='Guest Services & Eco-Center Hospitality',
            defaults={
                'program_description': (
                    "Guest Services welcomes visitors into the Tiriji Eco-Center, an organic food forest and learning space where guests can rest, serve, "
                    "meet community members, and contribute to the wider mission."
                ),
                'image_url': '/static/images/IMG-20260522-WA0016.jpg',
                'two_week_fee': Decimal('360.00'),
                'four_week_fee': Decimal('680.00'),
                'eight_week_fee': Decimal('1260.00'),
                'extra_week_fee': Decimal('140.00'),
            },
        )

        event_data = [
            ('Mentorship Field Day', children_program, today + timedelta(days=14), 'Meru County'),
            ('Women Enterprise Workshop', women_program, today + timedelta(days=28), 'Meru Town'),
            ('Community Regeneration Weekend', community_program, today + timedelta(days=42), 'Tiriji Field Site'),
            ('Youth Leadership Lab', ngl_program, today + timedelta(days=49), 'Tiriji Amani Community Hub'),
            ('Vocational Open Studio', vocational_program, today + timedelta(days=56), 'Vocational Training Centre'),
            ('Wellness Practice Morning', wellness_program, today + timedelta(days=63), 'Tiriji Eco-Center'),
        ]
        for title, linked_program, event_date, location in event_data:
            event_image_url = linked_program.image_url
            if linked_program == children_program:
                event_image_url = '/static/images/IMG-20260522-WA0037.jpg'
            events.objects.update_or_create(
                title=title,
                defaults={
                    'events_description': f'{title} brings volunteers, coordinators, and community members together for practical learning and field action.',
                    'image_url': event_image_url,
                    'program_id': linked_program,
                    'event_location': location,
                    'event_date': event_date,
                },
            )

        resource_data = [
            ('KACH Impact Brief', children_program, '/static/resources/tiriji-program-brief.txt'),
            ('Volunteer Orientation Notes', community_program, '/static/resources/volunteer-orientation.txt'),
            ('Women Enterprise Notes', women_program, '/static/resources/tiriji-program-brief.txt'),
            ('Youth Leadership Brief', ngl_program, '/static/resources/volunteer-orientation.txt'),
            ('Vocational Intake Guide', vocational_program, '/static/resources/tiriji-program-brief.txt'),
            ('Guest Services Brief', guest_program, '/static/resources/volunteer-orientation.txt'),
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

        for title, linked_program, image_url in [
            ('Scholar mentorship moment', children_program, '/static/images/IMG-20260522-WA0037.jpg'),
            ('Women leadership circle', women_program, '/static/images/hero-women.jpg'),
            ('Community planting day', community_program, '/static/images/IMG-20260522-WA0016.jpg'),
            ('Youth leadership session', ngl_program, '/static/images/IMG-20260522-WA0018.jpg'),
            ('Vocational training practice', vocational_program, '/static/images/program-kenger.jpg'),
            ('Wellness circle', wellness_program, '/static/images/hero-women-2.jpg'),
            ('Eco-center guest pathway', guest_program, '/static/images/IMG-20260522-WA0016.jpg'),
        ]:
            gallery.objects.update_or_create(
                title=title,
                defaults={
                    'image_description': f'Demo gallery item for {linked_program.title}.',
                    'image_url': image_url,
                    'program_id': linked_program,
                },
            )

        news_data = [
            (
                'KACH Care Pathway',
                children_program,
                "Kithoka Amani Children's Home is now represented in the demo site as a care, education, emotional wellbeing, and development pathway for vulnerable children.",
                '/static/images/IMG-20260522-WA0037.jpg',
            ),
            (
                'Women Enterprise Update',
                women_program,
                'The women empowerment section now highlights seed support, weaving skills, social enterprise, and economic independence for women groups.',
                '/static/images/hero-women.jpg',
            ),
            (
                'Youth Leadership Pathways',
                ngl_program,
                'The platform now includes Now Generation Leaders and Ecovillage Design Education as youth leadership and regenerative learning pathways.',
                '/static/images/IMG-20260522-WA0018.jpg',
            ),
            (
                'Vocational Intake Focus',
                vocational_program,
                'Vocational training content now reflects certificate-level tracks in hospitality, beauty, and fashion design.',
                '/static/images/program-kenger.jpg',
            ),
            (
                'Wellness Program Update',
                wellness_program,
                'Wellness Services are included as part of Tiriji Foundation\'s belief that health is essential for thriving communities.',
                '/static/images/hero-women-2.jpg',
            ),
            (
                'Guest Services Live',
                guest_program,
                'Guest Services now explain how visitors can stay, learn, serve, and experience Tiriji Eco-Center.',
                '/static/images/IMG-20260522-WA0016.jpg',
            ),
        ]
        for title, linked_program, description, image_url in news_data:
            News.objects.update_or_create(
                title=title,
                defaults={
                    'news_description': description,
                    'image_url': image_url,
                    'program_id': linked_program,
                    'event_id': None,
                },
            )

        blog_data = [
            (
                'What Regeneration Means at Tiriji',
                'Tiriji connects people, resources, and tools into resilient community systems.',
                (
                    'Tiriji Foundation frames community transformation as regeneration: people, nature, culture, and practical systems working together.\n\n'
                    'That is why the platform now presents the organization as an operating ecosystem rather than a flat charity site. Programs, partners, volunteers, resources, and updates connect back to one shared purpose: communities that are sustainable, peaceful, resilient, and flourishing.'
                ),
                community_program,
                'https://www.tirijifoundation.com/',
                '/static/images/IMG-20260522-WA0016.jpg',
            ),
            (
                "KACH: Care, Learning, and Flourishing",
                "Kithoka Amani Children's Home is represented as a holistic child development pathway.",
                (
                    "KACH is more than a shelter entry in the demo. It is modeled as a child-centered pathway for care, emotional wellbeing, education, mentorship, and future preparation.\n\n"
                    "The official Tiriji site describes KACH as a nurturing environment where children grow, learn, thrive, and flourish. This seed story turns that into site content that can be extended with real child protection stories, alumni profiles, and field photos."
                ),
                children_program,
                'https://www.tirijifoundation.com/children',
                '/static/images/IMG-20260522-WA0037.jpg',
            ),
            (
                'Women Building Regenerative Enterprise',
                'Women empowerment content now centers social enterprise and economic independence.',
                (
                    "The women empowerment story now focuses on practical economic pathways: women groups, seed support, weaving, tea harvesting, and local enterprise.\n\n"
                    "This gives the demo a stronger documentary feel and creates a base for future blogs about cohorts, business transformation, mentorship, and financial resilience."
                ),
                women_program,
                'https://www.tirijifoundation.com/women',
                '/static/images/hero-women.jpg',
            ),
            (
                'Leadership and Ecovillage Learning',
                'NGL and EDE connect youth leadership with regenerative design practice.',
                (
                    "Now Generation Leaders is presented as a leadership pathway, while Ecovillage Design Education brings ecological, economic, social, cultural, and spiritual dimensions into practical community learning.\n\n"
                    "Together they make the site feel more like a living learning network, with clear openings for youth cohorts, international learners, mentors, and field projects."
                ),
                ngl_program,
                'https://www.tirijifoundation.com/programs/ede',
                '/static/images/IMG-20260522-WA0018.jpg',
            ),
            (
                'Wellness as Community Infrastructure',
                'The wellness program positions health as necessary for a thriving community.',
                (
                    "The wellness content is now connected to Tiriji's wider operating model. Healthy communities need spaces for restoration, learning, movement, and practical care.\n\n"
                    "The demo uses Wellness Services as an entry point for future content on yoga sessions, Tiriji herbs, emotional wellbeing, and community health practices."
                ),
                wellness_program,
                'https://www.tirijifoundation.com/wellness',
                '/static/images/hero-women-2.jpg',
            ),
        ]
        for title, excerpt, body, linked_program, source_url, image_url in blog_data:
            BlogPost.objects.update_or_create(
                title=title,
                defaults={
                    'excerpt': excerpt,
                    'body': body,
                    'image_url': image_url,
                    'source_url': source_url,
                    'is_published': True,
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
            page='children',
            title='A nurturing home for growth',
            defaults={
                'person_name': 'KACH Children',
                'challenge': 'Children need safe environments that support basic care, learning, emotional wellbeing, and long-term development.',
                'intervention': "Kithoka Amani Children's Home brings care, education support, mentorship, and partner-backed community support into one pathway.",
                'outcome': 'The story now appears across the site as a child-centered impact pathway that can be expanded with real alumni and family reintegration stories.',
                'quote': 'A nurturing environment helps children see a future worth growing toward.',
                'image_url': '/static/images/IMG-20260522-WA0037.jpg',
                'is_featured': True,
            },
        )
        SuccessStory.objects.update_or_create(
            page='women',
            title='From workshop to local enterprise',
            defaults={
                'person_name': 'Grace',
                'challenge': 'Women groups need practical support, skills, and seed capital to grow social enterprises.',
                'intervention': 'Enterprise training, weaving practice, peer support, and seed support through the Tiriji women empowerment pathway.',
                'outcome': 'The story now frames women empowerment around economic independence and regenerative local enterprise.',
                'quote': 'The workshop gave me practical confidence.',
                'image_url': '/static/images/hero-women.jpg',
                'is_featured': True,
            },
        )
        SuccessStory.objects.update_or_create(
            page='women',
            title='Skills that travel into households',
            defaults={
                'person_name': 'Women Empowerment Cohort',
                'challenge': 'Many women and girls carry responsibility for households while lacking access to resilient income pathways.',
                'intervention': 'Hands-on learning in craft, enterprise, community leadership, and peer mentoring.',
                'outcome': 'Women empowerment content now has a second featured story for program pages and public storytelling sections.',
                'quote': 'When a woman gains a skill, the whole household gains options.',
                'image_url': '/static/images/hero-women-2.jpg',
                'is_featured': False,
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
