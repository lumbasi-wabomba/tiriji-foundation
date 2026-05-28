from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from .models import BlogPost, program, volunteer as Volunteer, events as Event, news as News, resources as Resource, donation as Donation, Transaction, VolunteerPayment, ImpactMetric, FeaturedPerson, SuccessStory, InspirationVideo, PageMedia, employees as Employee, partners as Partner, gallery as Gallery, feedback as Feedback
from .forms import BlogPostForm, ProgramForm, EventForm, NewsForm, ResourceForm, VolunteerForm, DonationForm, FeedbackForm, AdminUserForm, SuccessStoryForm
from .admin_roles import ADMIN_GROUP_NAMES, assign_admin_role, get_admin_role_label, user_has_admin_access, user_has_any_admin_role
from .services.payment_service import PaymentService
from django.contrib.auth import logout as auth_logout
from django_ratelimit.decorators import ratelimit
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import cloudinary
import time
import cloudinary.utils


CAREER_OPENINGS = [
    {
        'id': 1,
        'title': 'Volunteer Program Coordinator',
        'location': 'Meru, Kenya',
        'description': (
            'Coordinate volunteer onboarding, placement readiness, field schedules, '
            'and communication between applicants, program leads, and community hosts.'
        ),
    },
    {
        'id': 2,
        'title': 'Events and Resources Associate',
        'location': 'Hybrid / Meru',
        'description': (
            'Support resource publishing, event logistics, field updates, partner '
            'materials, and documentation for Tiriji Foundation programs.'
        ),
    },
]


def user_in_group(user):
    return user_has_admin_access(user)


def group_required(view_func):
    return login_required(user_passes_test(user_in_group, login_url='login')(view_func), login_url='login')


def role_required(*allowed_groups):
    def decorator(view_func):
        return login_required(
            user_passes_test(
                lambda user: user_has_any_admin_role(user, allowed_groups),
                login_url='admin_portal'
            )(view_func),
            login_url='login'
        )
    return decorator


def home(request):
    programs = program.objects.all()
    return render(request, 'core/home.html', {'programs': programs})

def about(request):
    return render(request, 'core/about.html')

@ratelimit(key='ip', method='POST', rate='5/h', block=True)
def contact(request):
    return render(request, 'core/contact.html')

def impact_page_context(page):
    return {
        'impact_metrics': ImpactMetric.objects.filter(page=page, is_active=True),
        'featured_person': FeaturedPerson.objects.filter(page=page, is_featured=True).first(),
        'stories': SuccessStory.objects.filter(page=page)[:6],
        'videos': InspirationVideo.objects.filter(page=page)[:4],
        'media_items': PageMedia.objects.filter(page=page)[:8],
    }


def children(request):
    context = impact_page_context('children')
    return render(request, 'core/children.html', context)


def women(request):
    context = impact_page_context('women')
    return render(request, 'core/women.html', context)   

@require_http_methods(["GET"])
def programs(request):
    programs = program.objects.all()
    return render(request, 'core/programs.html', {'programs': programs})

@require_http_methods(["GET"])
def program_detail(request, program_id):
    program_detail = get_object_or_404(program, program_id=program_id)
    return render(request, 'core/program_detail.html', {
        'program': program_detail,
        'gallery_items': program_detail.program_gallery.all()[:6],
        'program_news': program_detail.news.all()[:3],
        'program_resources': program_detail.resources.all()[:3],
        'program_events': program_detail.events.all()[:3],
    })

@require_http_methods(["GET","POST"])
def volunteer(request):
    return render(request, 'core/volunteer.html')

@require_http_methods(["GET","POST"])
@ratelimit(key='ip', method='POST', rate='3/h', block=True)
def volunteer_signup(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            volunteer_instance = form.save(commit=False)
            volunteer_instance.calculated_fee = volunteer_instance.fee
            volunteer_instance.status = 'payment_pending'
            volunteer_instance.save()

            transaction = Transaction.objects.create(
                amount=volunteer_instance.calculated_fee,
                payment_method='mpesa',
                status='pending'
            )
            VolunteerPayment.objects.create(
                volunteer=volunteer_instance,
                transaction=transaction,
                amount=volunteer_instance.calculated_fee
            )

            return redirect(                                   
                'volunteer_payment_summary',
                volunteer_id=volunteer_instance.volunteer_id  
            )
    else:
        initial = {}
        program_id = request.GET.get('program')
        if program_id and program.objects.filter(program_id=program_id).exists():
            initial['program_id'] = program_id

        form = VolunteerForm(initial=initial)

    return render(
        request,
        'core/volunteer_signup.html',
        {'form': form}
    )

@require_http_methods(["GET","POST"])
def volunteer_payment_summary(request, volunteer_id):
    volunteer_instance = get_object_or_404(Volunteer, volunteer_id=volunteer_id)
    payment = get_object_or_404(VolunteerPayment, volunteer=volunteer_instance)
    method = request.POST.get('payment_method', payment.transaction.payment_method if payment.transaction else 'mpesa')
    payment_session = PaymentService.volunteer_session(payment, method)

    # --------------------------------------------------------------------------------------------------
    # for demo purposes
    if request.method == 'POST' and request.POST.get('action') == 'confirm_demo_payment':
        PaymentService.complete_volunteer_payment(payment)
        messages.success(request, 'Demo volunteer payment marked as paid.')
        return redirect('volunteer_payment_summary', volunteer_id=volunteer_instance.volunteer_id)
    # ---------------------------------------------------------------------------------------------------

    return render(
        request,
        'core/volunteer_payment_summary.html',
        {
            'volunteer': volunteer_instance,
            'payment': payment,
            'payment_session': payment_session,
            'payment_methods': PaymentService.METHOD_CONFIG,
        }
    )

@ratelimit(key='ip', method='POST', rate='5/h', block=True)
@require_http_methods(["GET","POST"])
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)

        if form.is_valid():
            donation = form.save(commit=False)
            transaction = Transaction.objects.create(
                amount=donation.amount,
                payment_method=donation.payment_method or 'mpesa',
                status='pending',
            )
            donation.transaction = transaction
            donation.status = 'pending'
            donation.save()
            return redirect('donation_payment', donation_id=donation.donation_id)

    else:
        form = DonationForm()
    return render(request, 'core/donate.html', {'form': form })

@require_http_methods(["GET","POST"])
@ratelimit(key='ip', method='POST', rate='10/h', block=True)
def donation_payment(request, donation_id):
    donation = get_object_or_404(Donation.objects.select_related('transaction'), donation_id=donation_id)
    payment_session = PaymentService.donation_session(donation)

    # demo purposes
    # --------------------------------------------------------------------------------------------------
    if request.method == 'POST' and request.POST.get('action') == 'confirm_demo_payment':
        PaymentService.complete_donation(donation)
        messages.success(request, 'Demo donation payment marked as complete.')
        return redirect('donate_success')
    # --------------------------------------------------------------------------------------------------

    return render(request, 'core/donation_payment.html', {
        'donation': donation,
        'payment_session': payment_session,
    })

@require_http_methods(["GET"])
def donate_success(request):
    return render(request, 'core/donate_success.html')

@require_http_methods(["GET"])
def donate_cancel(request):
    return render(request, 'core/donate_cancel.html')

@require_http_methods(["GET"])
def events(request):
    event_items = Event.objects.select_related('program_id').all().order_by('event_date')
    return render(request, 'core/events.html', {'events': event_items})

@require_http_methods(["GET"])
def news(request):
    news_items = News.objects.select_related('program_id', 'event_id').all().order_by('-created_at')
    return render(request, 'core/news.html', {'news_items': news_items})

@require_http_methods(["GET"])
def resources(request):
    resource_items = Resource.objects.select_related('program_id').all().order_by('-created_at')
    return render(request, 'core/resources.html', {'resource_items': resource_items})

@require_http_methods(["GET"])
def faq(request):
    return render(request, 'core/faq.html')

@require_http_methods(["GET"])
def gallery(request):
    gallery_items = Gallery.objects.select_related('program_id', 'event_id').all().order_by('-created_at')
    return render(request, 'core/gallery.html', {'gallery_items': gallery_items})

def team(request):
    team_members = Employee.objects.all().order_by('first_name', 'last_name')
    return render(request, 'core/team.html', {'team_members': team_members})

def partners(request):
    partner_items = Partner.objects.select_related('program_id', 'assigned_employee').all().order_by('-created_at')
    return render(request, 'core/partners.html', {'partners': partner_items})

@require_http_methods(["GET"])
def careers(request):
    return render(request, 'core/careers.html', {'careers': CAREER_OPENINGS})

@require_http_methods(["GET"])
def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

@require_http_methods(["GET"])
def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')

@require_http_methods(["GET"])
def sitemap(request):
    return render(request, 'core/sitemap.html')

@ratelimit(key='ip', method='POST', rate='5/h', block=True)
@require_http_methods(["GET","POST"])
def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message was sent successfully!")
            return redirect("feedback")
    else:
        form = FeedbackForm()

    return render(request, "core/feedback.html", {'form': form})

@require_http_methods(["GET"])
def newsletter(request):
    return render(request, 'core/newsletter.html')

@require_http_methods(["GET"])
def event_detail(request, event_id):
    event = get_object_or_404(Event.objects.select_related('program_id'), event_id=event_id)
    return render(request, 'core/event_detail.html', {'event': event})

@require_http_methods(["GET"])
def news_detail(request, news_id):
    news_item = get_object_or_404(News, news_id=news_id)
    return render(request, 'core/news_detail.html', {'news_item': news_item})   

@require_http_methods(["GET"])
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, resource_id=resource_id)
    return render(request, 'core/resource_detail.html', {'resource': resource})

@require_http_methods(["GET"])
def gallery_detail(request, gallery_id):
    gallery_item = get_object_or_404(Gallery.objects.select_related('program_id', 'event_id'), image_id=gallery_id)
    return render(request, 'core/gallery_detail.html', {'gallery_item': gallery_item})  

@require_http_methods(["GET"])
def team_member_detail(request, member_id):
    member = get_object_or_404(Employee, employee_id=member_id)
    return render(request, 'core/team_member_detail.html', {'member': member})

@require_http_methods(["GET"])
def partner_detail(request, partner_id):
    partner = get_object_or_404(Partner.objects.select_related('program_id', 'assigned_employee'), pk=partner_id)
    return render(request, 'core/partner_detail.html', {'partner': partner})

@require_http_methods(["GET"])
def career_detail(request, career_id):
    career = next((item for item in CAREER_OPENINGS if item['id'] == career_id), None)
    if career is None:
        raise Http404('Career opening not found')
    return render(request, 'core/career_detail.html', {'career': career})

def blog(request):
    blog_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'core/blog.html', {'blog_posts': blog_posts})

@require_http_methods(["GET"])
def blog_detail(request, blog_id):
    blog_post = get_object_or_404(BlogPost, blog_id=blog_id, is_published=True)
    return render(request, 'core/blog_detail.html', {'blog_post': blog_post})


@group_required
@login_required
@ratelimit(key='user', method=['POST','PATCH','DELETE'], rate='20/h', block=True)
def admin_portal(request):
    pending_statuses = ['submitted', 'payment_pending', 'paid', 'under_review']
    pending_volunteers = Volunteer.objects.select_related('program_id').filter(
        status__in=pending_statuses
    ).order_by('-created_at')[:5]

    context = {
        'program_count': program.objects.count(),
        'event_count': Event.objects.count(),
        'news_count': News.objects.count(),
        'resource_count': Resource.objects.count(),
        'blog_count': BlogPost.objects.count(),
        'story_count': SuccessStory.objects.count(),
        'donation_count': Donation.objects.count(),
        'pending_volunteers': pending_volunteers,
        'pending_volunteer_count': Volunteer.objects.filter(status__in=pending_statuses).count(),
        'current_role': get_admin_role_label(request.user),
    }
    return render(request, 'core/admin.html', context)

@group_required
@login_required
@ratelimit(key='user', method=['POST','PATCH','DELETE'], rate='20/h', block=True)
def admin_form_view(request, form_class, instance=None, section_name='', action_label='Create', return_url='admin_portal'):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{section_name} saved successfully.')
            return redirect(return_url)
    else:
        form = form_class(instance=instance)

    return render(request, 'core/admin_form.html', {
        'form': form,
        'section_name': section_name,
        'action_label': action_label,
        'return_url': return_url,
    })

# user management
# --------------------------------------------------------------------------------------------------------------------------------
@role_required('sys_admin')
@ratelimit(key='user', method=['POST','PATCH','DELETE'], rate='10/h', block=True)
@login_required
def admin_users(request):
    users = User.objects.filter(Q(is_staff=True) | Q(groups__name__in=ADMIN_GROUP_NAMES)).distinct().order_by('first_name', 'username')

    return render(request, 'core/admin_users.html', {
        'user_rows': [
            {
                'user': user,
                'role': get_admin_role_label(user),
            }
            for user in users
        ],
    })

@role_required('sys_admin')
@require_http_methods(["POST"])
@ratelimit(key='user', method=['POST'], rate='10/h', block=True)
@login_required
def admin_user_add(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            user.is_staff = True
            user.save(update_fields=['is_staff'])
            assign_admin_role(user, form.cleaned_data['role'])
            messages.success(request, 'Admin user created successfully.')
            return redirect('admin_users')
    else:
        form = AdminUserForm()

    return render(request, 'core/admin_form.html', {
        'form': form,
        'section_name': 'Admin User',
        'action_label': 'Add',
        'return_url': 'admin_users',
    })

@role_required('sys_admin')
@require_http_methods(["PATCH","PUT"])
@ratelimit(key='user', method=ratelimit.ALL, rate='10/h', block=True)
@login_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    current_role = user.groups.filter(name__in=ADMIN_GROUP_NAMES).first()
    initial = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'email': user.email,
        'role': current_role.name if current_role else 'manager',
    }

    if request.method == 'POST':
        form = AdminUserForm(request.POST, user_instance=user)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.is_staff = True
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            assign_admin_role(user, form.cleaned_data['role'])
            messages.success(request, 'Admin user updated successfully.')
            return redirect('admin_users')
    else:
        form = AdminUserForm(initial=initial, user_instance=user)

    return render(request, 'core/admin_form.html', {
        'form': form,
        'section_name': 'Admin User',
        'action_label': 'Update',
        'return_url': 'admin_users',
    })
# ---------------------------------------------------------------------------------------------------------------

# donations management 
# ---------------------------------------------------------------------------------------------------------------
@role_required('director','secretary')
@require_http_methods(["GET"])
@ratelimit(key='user', method=ratelimit.ALL, rate='30/h', block=True)
@login_required
def admin_donations(request):
    items = Donation.objects.select_related('transaction').all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Donations',
        'section_label': 'Donation',
        'add_url': None,
        'headers': ['ID', 'Donor', 'Amount', 'Type', 'Method', 'Status', 'Created'],
        'rows': [
            {
                'cols': [
                    item.donation_id or 'Missing ID',
                    item.donor_name or 'Anonymous',
                    f'${item.amount}',
                    item.get_donation_type_display(),
                    item.get_payment_method_display(),
                    item.get_status_display(),
                    item.created_at.strftime('%Y-%m-%d'),
                ],
                'review_url': reverse('admin_donation_review', args=[item.donation_id]) if item.donation_id else None,
            }
            for item in items
        ],
    })

@login_required
@role_required('director','secretary')
@ratelimit(key='user', method=ratelimit.ALL, rate='30/h', block=True)
def admin_donation_review(request, donation_id):
    instance = get_object_or_404(Donation.objects.select_related('transaction'), donation_id=donation_id)

    if request.method == 'POST':
        next_status = request.POST.get('status')
        valid_statuses = dict(Donation.STATUS_CHOICES)

        if next_status in valid_statuses:
            instance.status = next_status
            instance.save(update_fields=['status'])
            if instance.transaction:
                transaction_status = {
                    'completed': 'paid',
                    'cancelled': 'refunded',
                }.get(next_status, next_status)
                instance.transaction.status = transaction_status
                instance.transaction.save(update_fields=['status'])
            messages.success(request, f'Donation status updated to {valid_statuses[next_status]}.')
            return redirect('admin_donation_review', donation_id=instance.donation_id)

        messages.error(request, 'Invalid donation status.')

    return render(request, 'core/admin_donation_review.html', {
        'donation': instance,
        'status_choices': Donation.STATUS_CHOICES,
    })
# --------------------------------------------------------------------------------------------------------------

# program management
# --------------------------------------------------------------------------------------------------------------

@login_required
@role_required('director','secretary')
# @require_http_methods(["GET","POST","PATCH","PUT"])
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_programs(request):
    items = program.objects.all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Programs',
        'section_label': 'Program',
        'add_url': 'admin_program_add',
        'headers': ['ID', 'Title', 'Created'],
        'rows': [
            {
                'cols': [item.program_id, item.title, item.created_at.strftime('%Y-%m-%d')],
                'edit_url': reverse('admin_program_edit', args=[item.program_id]),
                'delete_url': reverse('admin_program_delete', args=[item.program_id]),
            }
            for item in items
        ],
    })


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["POST","PATCH","PUT"])
@login_required
def admin_program_add(request):
    return admin_form_view(request, ProgramForm, section_name='Program', action_label='Add', return_url='admin_programs')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["PATCH","PUT"])
@login_required
def admin_program_edit(request, program_id):
    instance = get_object_or_404(program, program_id=program_id)
    return admin_form_view(request, ProgramForm, instance=instance, section_name='Program', action_label='Update', return_url='admin_programs')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["DELETE"])
@login_required
def admin_program_delete(request, program_id):
    instance = get_object_or_404(program, program_id=program_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Program deleted successfully.')
        return redirect('admin_programs')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Program',
        'object_name': instance.title,
        'return_url': 'admin_programs',
    })
# ---------------------------------------------------------------------------------------------------------------

# event management
# ---------------------------------------------------------------------------------------------------------------

@role_required('secretary','director')
# @require_http_methods(["GET"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_events(request):
    items = Event.objects.select_related('program_id').all().order_by('-event_date')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Events',
        'section_label': 'Event',
        'add_url': 'admin_event_add',
        'headers': ['ID', 'Title', 'Program', 'Date'],
        'rows': [
            {
                'cols': [item.event_id, item.title, item.program_id.title if item.program_id else '-', item.event_date.strftime('%Y-%m-%d')],
                'edit_url': reverse('admin_event_edit', args=[item.event_id]),
                'delete_url': reverse('admin_event_delete', args=[item.event_id]),
            }
            for item in items
        ],
    })


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["POST"])
@login_required
def admin_event_add(request):
    return admin_form_view(request, EventForm, section_name='Event', action_label='Add', return_url='admin_events')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["PATCH","PUT"])
@login_required
def admin_event_edit(request, event_id):
    instance = get_object_or_404(Event, event_id=event_id)
    return admin_form_view(request, EventForm, instance=instance, section_name='Event', action_label='Update', return_url='admin_events')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["DELETE"])
@login_required
def admin_event_delete(request, event_id):
    instance = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('admin_events')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Event',
        'object_name': instance.title,
        'return_url': 'admin_events',
    })
# ----------------------------------------------------------------------------------------------------------------

# news management
# ----------------------------------------------------------------------------------------------------------------

@role_required('secretary','director')
# @require_http_methods(["GET"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_news(request):
    items = News.objects.select_related('program_id', 'event_id').all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'News',
        'section_label': 'News item',
        'add_url': 'admin_news_add',
        'headers': ['ID', 'Title', 'Program', 'Event'],
        'rows': [
            {
                'cols': [item.news_id, item.title, item.program_id.title if item.program_id else '-', item.event_id.title if item.event_id else '-'],
                'edit_url': reverse('admin_news_edit', args=[item.news_id]),
                'delete_url': reverse('admin_news_delete', args=[item.news_id]),
            }
            for item in items
        ],
    })


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["POST"])
@login_required
def admin_news_add(request):
    return admin_form_view(request, NewsForm, section_name='News item', action_label='Add', return_url='admin_news')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["PATCH","PUT"])
@login_required
def admin_news_edit(request, news_id):
    instance = get_object_or_404(News, news_id=news_id)
    return admin_form_view(request, NewsForm, instance=instance, section_name='News item', action_label='Update', return_url='admin_news')


@role_required('secretary','director')
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
# @require_http_methods(["DELETE"])
@login_required
def admin_news_delete(request, news_id):
    instance = get_object_or_404(News, news_id=news_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'News item deleted successfully.')
        return redirect('admin_news')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'News item',
        'object_name': instance.title,
        'return_url': 'admin_news',
    })
# -------------------------------------------------------------------------------------------------------------------------------

@role_required('content_manager', 'events_resources_manager')
def admin_blogs(request):
    items = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Blog',
        'section_label': 'Blog post',
        'add_url': 'admin_blog_add',
        'headers': ['ID', 'Title', 'Published', 'Updated'],
        'rows': [
            {
                'cols': [
                    item.blog_id,
                    item.title,
                    'Yes' if item.is_published else 'Draft',
                    item.updated_at.strftime('%Y-%m-%d'),
                ],
                'edit_url': reverse('admin_blog_edit', args=[item.blog_id]),
                'delete_url': reverse('admin_blog_delete', args=[item.blog_id]),
            }
            for item in items
        ],
    })


@role_required('content_manager', 'events_resources_manager')
def admin_blog_add(request):
    return admin_form_view(request, BlogPostForm, section_name='Blog post', action_label='Add', return_url='admin_blogs')


@role_required('content_manager', 'events_resources_manager')
def admin_blog_edit(request, blog_id):
    instance = get_object_or_404(BlogPost, blog_id=blog_id)
    return admin_form_view(request, BlogPostForm, instance=instance, section_name='Blog post', action_label='Update', return_url='admin_blogs')


@role_required('content_manager', 'events_resources_manager')
def admin_blog_delete(request, blog_id):
    instance = get_object_or_404(BlogPost, blog_id=blog_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Blog post deleted successfully.')
        return redirect('admin_blogs')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Blog post',
        'object_name': instance.title,
        'return_url': 'admin_blogs',
    })


@role_required('content_manager', 'events_resources_manager')
def admin_stories(request):
    items = SuccessStory.objects.all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Stories',
        'section_label': 'Story',
        'add_url': 'admin_story_add',
        'headers': ['ID', 'Title', 'Page', 'Featured'],
        'rows': [
            {
                'cols': [
                    item.id,
                    item.title,
                    item.get_page_display(),
                    'Yes' if item.is_featured else '-',
                ],
                'edit_url': reverse('admin_story_edit', args=[item.id]),
                'delete_url': reverse('admin_story_delete', args=[item.id]),
            }
            for item in items
        ],
    })


@role_required('content_manager', 'events_resources_manager')
def admin_story_add(request):
    return admin_form_view(request, SuccessStoryForm, section_name='Story', action_label='Add', return_url='admin_stories')


@role_required('content_manager', 'events_resources_manager')
def admin_story_edit(request, story_id):
    instance = get_object_or_404(SuccessStory, pk=story_id)
    return admin_form_view(request, SuccessStoryForm, instance=instance, section_name='Story', action_label='Update', return_url='admin_stories')


@role_required('content_manager', 'events_resources_manager')
def admin_story_delete(request, story_id):
    instance = get_object_or_404(SuccessStory, pk=story_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Story deleted successfully.')
        return redirect('admin_stories')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Story',
        'object_name': instance.title,
        'return_url': 'admin_stories',
    })


@role_required('secretary','director')
def admin_resources(request):
    items = Resource.objects.select_related('program_id').all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Resources',
        'section_label': 'Resource',
        'add_url': 'admin_resource_add',
        'headers': ['ID', 'Title', 'Program', 'Uploaded'],
        'rows': [
            {
                'cols': [item.resource_id, item.title, item.program_id.title if item.program_id else '-', item.created_at.strftime('%Y-%m-%d')],
                'edit_url': reverse('admin_resource_edit', args=[item.resource_id]),
                'delete_url': reverse('admin_resource_delete', args=[item.resource_id]),
            }
            for item in items
        ],
    })

@role_required('secretary','director')
# @require_http_methods(["POST"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_resource_add(request):
    return admin_form_view(request, ResourceForm, section_name='Resource', action_label='Add', return_url='admin_resources')


@role_required('secretary','director')
# @require_http_methods(["PATCH","PUT"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_resource_edit(request, resource_id):
    instance = get_object_or_404(Resource, resource_id=resource_id)
    return admin_form_view(request, ResourceForm, instance=instance, section_name='Resource', action_label='Update', return_url='admin_resources')


@role_required('secretary','director')
# @require_http_methods(["DELETE"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_resource_delete(request, resource_id):
    instance = get_object_or_404(Resource, resource_id=resource_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Resource deleted successfully.')
        return redirect('admin_resources')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Resource',
        'object_name': instance.title,
        'return_url': 'admin_resources',
    })

# volunteer management 
# ------------------------------------------------------------------------------------------------------------------------------------
@role_required('secretary','director')
# @require_http_methods(["GET"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_volunteers(request):
    items = Volunteer.objects.all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Volunteers',
        'section_label': 'Volunteer',
        'add_url': 'admin_volunteer_add',
        'headers': ['ID', 'Full Name', 'Email', 'Phone', 'Program', 'Status', 'Created'],
        'rows': [
            {
                'cols': [item.volunteer_id, f"{item.first_name} {item.last_name}", item.email, item.phone_number, 
                         item.program_id.title if item.program_id else '-', item.status, item.created_at.strftime('%Y-%m-%d')],
                'review_url': reverse('admin_volunteer_review', args=[item.volunteer_id]),
                'edit_url': reverse('admin_volunteer_edit', args=[item.volunteer_id]),
                'delete_url': reverse('admin_volunteer_delete', args=[item.volunteer_id]),
            }
            for item in items
        ],
    })


@role_required('secretary','director')
# @require_http_methods(["POST"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_volunteer_add(request):
    return admin_form_view(request, VolunteerForm, section_name='Volunteer', action_label='Add', return_url='admin_volunteers')


@role_required('secretary','director')
# @require_http_methods(["PATCH","PUT"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_volunteer_edit(request, volunteer_id):
    instance = get_object_or_404(Volunteer, volunteer_id=volunteer_id)
    return admin_form_view(request, VolunteerForm, instance=instance, section_name='Volunteer', action_label='Update', return_url='admin_volunteers')


@role_required('secretary','director')
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_volunteer_review(request, volunteer_id):
    instance = get_object_or_404(Volunteer.objects.select_related('program_id'), volunteer_id=volunteer_id)
    payment = VolunteerPayment.objects.select_related('transaction').filter(volunteer=instance).first()

    if request.method == 'POST':
        next_status = request.POST.get('status')
        valid_statuses = dict(Volunteer.APPLICATION_STATUS)

        if next_status in valid_statuses:
            instance.status = next_status
            instance.save(update_fields=['status'])
            messages.success(request, f'Application status updated to {valid_statuses[next_status]}.')
            return redirect('admin_volunteer_review', volunteer_id=instance.volunteer_id)

        messages.error(request, 'Invalid application status.')

    return render(request, 'core/admin_volunteer_review.html', {
        'volunteer': instance,
        'payment': payment,
        'status_choices': Volunteer.APPLICATION_STATUS,
    })


@role_required('secretary','director')
# @require_http_methods(["DELETE"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_volunteer_delete(request, volunteer_id):
    instance = get_object_or_404(Volunteer, volunteer_id=volunteer_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Volunteer deleted successfully.')
        return redirect('admin_volunteers')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Volunteer',
        'object_name': f"{instance.first_name} {instance.last_name}",
        'return_url': 'admin_volunteers',
    })

#  feedback management
# -------------------------------------------------------------------------------------------------------------------
@group_required
# @require_http_methods(["GET"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_feedback(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')
    return render(request, 'core/admin_feedback_list.html', {
        'section_name': 'Feedback',
        'section_label': 'Feedback Item',
        'feedback_list': feedback_list,
    })


@group_required
# @require_http_methods(["DELETE"])
@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='25/h', block=True)
def admin_feedback_delete(request, feedback_id):
    instance = get_object_or_404(Feedback, feedback_id=feedback_id)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Feedback deleted successfully.')
        return redirect('admin_feedback')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Feedback',
        'object_name': instance.name,
        'return_url': 'admin_feedback',
    })


@group_required
@login_required
def admin_feedback_respond(request, feedback_id):
    instance = get_object_or_404(Feedback, feedback_id=feedback_id)
    if request.method == 'POST':
        response_message = request.POST.get('response_message')
        if response_message:
            instance.response_message = response_message
            instance.responded_at = timezone.now()
            instance.status = 'addressed'
            instance.save(update_fields=['response_message', 'responded_at', 'status'])
            messages.success(request, 'Response saved.')
            return redirect('admin_feedback')
    return render(request, 'core/admin_feedback_respond.html', {'feedback': instance})


def _mark_feedback_status(request, feedback_id, status, message):
    instance = get_object_or_404(Feedback, feedback_id=feedback_id)
    instance.status = status
    instance.save(update_fields=['status'])
    messages.success(request, message)
    return redirect('admin_feedback')


@group_required
@login_required
def admin_feedback_mark_addressed(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'addressed', 'Feedback marked as addressed.')


@group_required
@login_required
def admin_feedback_mark_unaddressed(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'new', 'Feedback marked as new.')


@group_required
@login_required
def admin_feedback_mark_in_progress(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'in_progress', 'Feedback marked as in progress.')


@group_required
@login_required
def admin_feedback_mark_resolved(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'resolved', 'Feedback marked as resolved.')


@group_required
@login_required
def admin_feedback_mark_rejected(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'rejected', 'Feedback marked as rejected.')


@group_required
@login_required
def admin_feedback_mark_duplicate(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'duplicate', 'Feedback marked as duplicate.')


@group_required
@login_required
def admin_feedback_mark_wontfix(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'wontfix', 'Feedback marked as won\'t fix.')


@group_required
@login_required
def admin_feedback_mark_needsinfo(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'needsinfo', 'Feedback marked as needs info.')

@group_required
@login_required
def admin_feedback_mark_accepted(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'accepted', 'Feedback marked as accepted.')


@group_required
@login_required
def admin_feedback_mark_reopened(request, feedback_id):
    return _mark_feedback_status(request, feedback_id, 'reopened', 'Feedback marked as reopened.')

# @group_required
# @login_required
# def admin_logout(request):
#     auth_logout(request)
#     return redirect('home')
 
#  upload media 
# -------------------------------------------------------------------------------------------------------------------
# @group_required
# @require_http_methods(["POST"])
# @login_required                                   
# @ratelimit(key='user', method=ratelimit.ALL, rate='15/h', block=True)
# def upload_media(request):
#     media_file = request.FILES.get("file")
#     if not media_file:
#         return JsonResponse({"error": "No file provided."}, status=400)

#     try:
#         temp_path = default_storage.save(
#             f"temp/{media_file.name}",
#             ContentFile(media_file.read())
#         )
#     except Exception as e:
#         return JsonResponse({"error": f"Could not save file: {e}"}, status=500)

#     try:
#         task = process_media_task.delay(temp_path)
#     except Exception as e:
#         # Celery/Redis not reachable — clean up and return JSON error
#         default_storage.delete(temp_path)
#         return JsonResponse({
#             "error": f"Processing queue unavailable: {e}. Is Celery running?"
#         }, status=503)

#     return JsonResponse({
#         "task_id": task.id,
#         "status":  "processing",
#     })


# @group_required
# @require_http_methods(["GET"])
# def upload_media_status(request, task_id):
#     try:
#         task = AsyncResult(task_id)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

#     if task.state == "PENDING":
#         return JsonResponse({"status": "pending"})

#     elif task.state == "SUCCESS":
#         return JsonResponse({
#             "status": "done",
#             "url":    task.result["url"],
#             "type":   task.result["type"],
#         })

#     elif task.state == "FAILURE":
#         return JsonResponse({
#             "status": "failed",
#             "error":  str(task.result),
#         }, status=500)

#     else:
#         return JsonResponse({"status": task.state.lower()})
    

@login_required
@ratelimit(key='user', method=ratelimit.ALL, rate='15/h', block=True)
@group_required
def cloudinary_signature(request):
    timestamp = int(time.time())
    folder = "tiriji"
    # transformation = "q_auto,f_auto,e_auto_enhance,e_auto_color"
    
    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
        # "transformations": transformation,
    }

    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        cloudinary.config().api_secret
    )                                            

    return JsonResponse({
        "signature":  signature,
        "timestamp":  timestamp,
        "folder":     folder,
        # "transformations": transformation,
        "cloud_name": cloudinary.config().cloud_name,
        "api_key":    cloudinary.config().api_key,
    })                                              