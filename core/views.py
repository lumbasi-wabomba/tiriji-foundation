from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import (
    program,
    volunteer,
    events as Event,
    news as News,
    resources as Resource,
    Transaction,
    VolunteerPayment,)
from .forms import ProgramForm, EventForm, NewsForm, ResourceForm , VolunteerForm , DonationForm 
import os
from django.conf import settings
from .models import resources


def user_in_group(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=['admin', 'secretary', 'director']).exists())


def group_required(view_func):
    return login_required(user_passes_test(user_in_group, login_url='login')(view_func), login_url='login')


def home(request):
    programs = program.objects.all()
    return render(request, 'core/home.html', {'programs': programs})

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def children(request):
    return render(request, 'core/children.html')

def women(request):
    return render(request, 'core/women.html')   


def programs(request):
    programs = program.objects.all()
    return render(request, 'core/programs.html', {'programs': programs})

def program_detail(request, program_id):
    program_detail = program.objects.get(program_id=program_id)
    return render(request, 'core/program_detail.html', {'program': program_detail})


def volunteer(request):
    return render(request, 'core/volunteer.html')


def volunteer_signup(request):

    if request.method == 'POST':

        form = VolunteerForm(request.POST)

        if form.is_valid():

            # =========================
            # CREATE VOLUNTEER
            # =========================
            volunteer_instance = form.save(commit=False)

            # Freeze calculated fee
            volunteer_instance.calculated_fee = (
                volunteer_instance.fee
            )

            # Initial workflow status
            volunteer_instance.status = 'payment_pending'

            volunteer_instance.save()

            # =========================
            # CREATE TRANSACTION
            # =========================
            transaction = Transaction.objects.create(
                amount=volunteer_instance.calculated_fee,
                payment_method='mpesa',
                status='pending'
            )

            # =========================
            # CREATE PAYMENT RECORD
            # =========================
            VolunteerPayment.objects.create(
                volunteer=volunteer_instance,
                transaction=transaction,
                amount=volunteer_instance.calculated_fee,
                status='pending'
            )

            # =========================
            # REDIRECT TO PAYMENT PAGE
            # =========================
            return redirect(
                'volunteer_payment_summary',
                volunteer_email=volunteer_instance.email
            )

    else:

        form = VolunteerForm()

    return render(
        request,
        'core/volunteer_signup.html',
        {
            'form': form
        }
    )

def volunteer_payment_summary(request, volunteer_email):
    volunteer_instance = get_object_or_404(volunteer, email=volunteer_email)
    payment = get_object_or_404(VolunteerPayment, volunteer=volunteer_instance)

    return render(
        request,
        'core/volunteer_payment_summary.html',
        {
            'volunteer': volunteer_instance,
            'payment': payment
        }
    )



def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = request.POST.get('amount')
            transaction = Transaction.objects.create(
                amount=amount,
                status='pending',
                payment_method=request.POST.get('payment_method', 'mpesa')
            )
            donation = form.save(commit=False)
            donation.transaction = transaction
            donation.save()

            # Simulated redirect to payment gateway step
            return redirect('donate_success')
    else:
        form = DonationForm()
        
    return render(
        request,
        'core/donate.html',
        {'form': form}
    )


# def donate(request):
#     if request.method == 'POST':
#         form = DonationForm(request.POST)

#         if form.is_valid():
#             amount = request.POST.get('amount')
#             transaction = Transaction.objects.create( amount=amount, payment_method=request.POST.get('payment_method'))
#             donation = form.save(commit=False)
#             donation.transaction = transaction
#             donation.save()
#             return redirect('donation_success')

#     else:
#         form = DonationForm()
#     return render(request, 'core/donate.html', {'form': form })

def donate_success(request):
    return render(request, 'core/donate_success.html')

def donate_cancel(request):
    return render(request, 'core/donate_cancel.html')


def events(request):
    return render(request, 'core/events.html')  

def news(request):
    return render(request, 'core/news.html')

def resources(request):
    return render(request, 'core/resources.html')

def faq(request):
    return render(request, 'core/faq.html')

def gallery(request):
    return render(request, 'core/gallery.html')

def team(request):
    return render(request, 'core/team.html')

def partners(request):
    return render(request, 'core/partners.html')

def careers(request):
    return render(request, 'core/careers.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')

def support(request):
    return render(request, 'core/support.html')

def sitemap(request):
    return render(request, 'core/sitemap.html')

def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # process message (save/email etc)

        messages.success(request, "Your message was sent successfully!")
        return redirect("feedback")

    return render(request, "core/feedback.html")


def newsletter(request):
    return render(request, 'core/newsletter.html')



def event_detail(request, event_id):
    # Placeholder for event detail view
    return render(request, 'core/event_detail.html', {'event_id': event_id})

def news_detail(request, news_id):
    # Placeholder for news detail view
    return render(request, 'core/news_detail.html', {'news_id': news_id})   

def resource_detail(request, resource_id):
    # Placeholder for resource detail view
    return render(request, 'core/resource_detail.html', {'resource_id': resource_id})

def gallery_detail(request, gallery_id):
    # Placeholder for gallery detail view
    return render(request, 'core/gallery_detail.html', {'gallery_id': gallery_id})  

def team_member_detail(request, member_id):
    # Placeholder for team member detail view
    return render(request, 'core/team_member_detail.html', {'member_id': member_id})

def partner_detail(request, partner_id):
    # Placeholder for partner detail view
    return render(request, 'core/partner_detail.html', {'partner_id': partner_id})

def career_detail(request, career_id):
    # Placeholder for career detail view
    return render(request, 'core/career_detail.html', {'career_id': career_id})

def blog(request):
    return render(request, 'core/blog.html')

def blog_detail(request, blog_id):
    # Placeholder for blog detail view
    return render(request, 'core/blog_detail.html', {'blog_id': blog_id})


@group_required
def admin_portal(request):
    context = {
        'program_count': program.objects.count(),
        'event_count': Event.objects.count(),
        'news_count': News.objects.count(),
        'resource_count': Resource.objects.count(),
    }
    return render(request, 'core/admin.html', context)


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


@group_required
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


@group_required
def admin_program_add(request):
    return admin_form_view(request, ProgramForm, section_name='Program', action_label='Add', return_url='admin_programs')


@group_required
def admin_program_edit(request, program_id):
    instance = get_object_or_404(program, program_id=program_id)
    return admin_form_view(request, ProgramForm, instance=instance, section_name='Program', action_label='Update', return_url='admin_programs')


@group_required
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


@group_required
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


@group_required
def admin_event_add(request):
    return admin_form_view(request, EventForm, section_name='Event', action_label='Add', return_url='admin_events')


@group_required
def admin_event_edit(request, event_id):
    instance = get_object_or_404(Event, event_id=event_id)
    return admin_form_view(request, EventForm, instance=instance, section_name='Event', action_label='Update', return_url='admin_events')


@group_required
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


@group_required
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


@group_required
def admin_news_add(request):
    return admin_form_view(request, NewsForm, section_name='News item', action_label='Add', return_url='admin_news')


@group_required
def admin_news_edit(request, news_id):
    instance = get_object_or_404(News, news_id=news_id)
    return admin_form_view(request, NewsForm, instance=instance, section_name='News item', action_label='Update', return_url='admin_news')


@group_required
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


@group_required
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


@group_required
def admin_resource_add(request):
    return admin_form_view(request, ResourceForm, section_name='Resource', action_label='Add', return_url='admin_resources')


@group_required
def admin_resource_edit(request, resource_id):
    instance = get_object_or_404(Resource, resource_id=resource_id)
    return admin_form_view(request, ResourceForm, instance=instance, section_name='Resource', action_label='Update', return_url='admin_resources')


@group_required
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


@group_required
def admin_volunteers(request):
    items = volunteer.objects.all().order_by('-created_at')
    return render(request, 'core/admin_list.html', {
        'section_name': 'Volunteers',
        'section_label': 'Volunteer',
        'add_url': 'admin_volunteer_add',
        'headers': ['ID', 'Full Name', 'Email', 'Phone', 'Program', 'Status', 'Created'],
        'rows': [
            {
                'cols': [item.email, f"{item.first_name} {item.last_name}", item.email, item.phone_number, 
                         item.program_id.title if item.program_id else '-', item.status, item.created_at.strftime('%Y-%m-%d')],
                'edit_url': reverse('admin_volunteer_edit', args=[item.email]),
                'delete_url': reverse('admin_volunteer_delete', args=[item.email]),
            }
            for item in items
        ],
    })


@group_required
def admin_volunteer_add(request):
    return admin_form_view(request, VolunteerForm, section_name='Volunteer', action_label='Add', return_url='admin_volunteers')


@group_required
def admin_volunteer_edit(request, volunteer_email):
    instance = get_object_or_404(volunteer, email=volunteer_email)
    return admin_form_view(request, VolunteerForm, instance=instance, section_name='Volunteer', action_label='Update', return_url='admin_volunteers')


@group_required
def admin_volunteer_delete(request, volunteer_email):
    instance = get_object_or_404(volunteer, email=volunteer_email)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Volunteer deleted successfully.')
        return redirect('admin_volunteers')
    return render(request, 'core/admin_delete_confirm.html', {
        'section_name': 'Volunteer',
        'object_name': f"{instance.first_name} {instance.last_name}",
        'return_url': 'admin_volunteers',
    })


@group_required
def admin_feedback(request):
    feedback_list = feedback.objects.all().order_by('-created_at')
    return render(request, 'core/admin_feedback_list.html', {
        'section_name': 'Feedback',
        'section_label': 'Feedback Item',
        'feedback_list': feedback_list,
    })


@group_required
def admin_feedback_delete(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
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
def admin_feedback_respond(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    if request.method == 'POST':
        # Handle response submission
        response_message = request.POST.get('response_message')
        if response_message:
            # Here you would typically save the response to a related model or add it to the feedback
            # For now, we'll just show a success message
            messages.success(request, 'Response added successfully.')
            return redirect('admin_feedback')
    
    return render(request, 'core/admin_feedback_respond.html', {
        'feedback': instance,
    })


@group_required
def admin_feedback_mark_addressed(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    # Here you would update a status field or add a tag
    # For now, we'll just show a success message
    messages.success(request, 'Feedback marked as addressed.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_unaddressed(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    # Here you would update a status field or remove a tag
    messages.success(request, 'Feedback marked as unaddressed.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_in_progress(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as in progress.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_resolved(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as resolved.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_rejected(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as rejected.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_duplicate(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as duplicate.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_wontfix(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as won\'t fix.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_needsinfo(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as needs info.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_accepted(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as accepted.')
    return redirect('admin_feedback')


@group_required
def admin_feedback_mark_reopened(request, feedback_id):
    instance = get_object_or_404(feedback, feedback_id=feedback_id)
    messages.success(request, 'Feedback marked as reopened.')
    return redirect('admin_feedback')
 