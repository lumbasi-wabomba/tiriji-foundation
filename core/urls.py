# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('children/', views.children, name='children'),
    path('women/', views.women, name='women'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('programs/', views.programs, name='programs'),
    path('programs/<uuid:program_id>/', views.program_detail, name='program_detail'),        
    path('volunteer/signup/', views.volunteer_signup, name='volunteer_signup'),
    path('volunteer/payment/<uuid:volunteer_id>/volunteer_payment_summary/', views.volunteer_payment_summary, name='volunteer_payment_summary'),
    path('donate/', views.donate, name='donate'),
    path('donate/payment/<uuid:donation_id>/', views.donation_payment, name='donation_payment'),
    path('events/', views.events, name='events'),
    path('events/<uuid:event_id>/', views.event_detail, name='event_detail'),                
    path('news/', views.news, name='news'),
    path('news/<uuid:news_id>/', views.news_detail, name='news_detail'),                    
    path('resources/', views.resources, name='resources'),
    path('resources/<uuid:resource_id>/', views.resource_detail, name='resource_detail'),    
    path('faq/', views.faq, name='faq'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<int:gallery_id>/', views.gallery_detail, name='gallery_detail'),          
    path('team/', views.team, name='team'),
    path('team/<uuid:member_id>/', views.team_member_detail, name='team_member_detail'),
    path('partners/', views.partners, name='partners'),
    path('partners/<int:partner_id>/', views.partner_detail, name='partner_detail'),       
    path('blog/', views.blog, name='blog'),
    path('blog/<uuid:blog_id>/', views.blog_detail, name='blog_detail'),
    path('donate/success/', views.donate_success, name='donate_success'),
    path('donate/cancel/', views.donate_cancel, name='donate_cancel'),
    path('feedback/', views.feedback, name='feedback'),

    # auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    

    # admin
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('admin-portal/users/', views.admin_users, name='admin_users'),
    path('admin-portal/users/add/', views.admin_user_add, name='admin_user_add'),
    path('admin-portal/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),         
    path('admin-portal/donations/', views.admin_donations, name='admin_donations'),
    path('admin-portal/donations/<uuid:donation_id>/review/', views.admin_donation_review, name='admin_donation_review'),

    path('admin-portal/programs/', views.admin_programs, name='admin_programs'),
    path('admin-portal/programs/add/', views.admin_program_add, name='admin_program_add'),
    path('admin-portal/programs/<uuid:program_id>/edit/', views.admin_program_edit, name='admin_program_edit'),      
    path('admin-portal/programs/<uuid:program_id>/delete/', views.admin_program_delete, name='admin_program_delete'),

    path('admin-portal/events/', views.admin_events, name='admin_events'),
    path('admin-portal/events/add/', views.admin_event_add, name='admin_event_add'),
    path('admin-portal/events/<uuid:event_id>/edit/', views.admin_event_edit, name='admin_event_edit'),      
    path('admin-portal/events/<uuid:event_id>/delete/', views.admin_event_delete, name='admin_event_delete'),

    path('admin-portal/news/', views.admin_news, name='admin_news'),
    path('admin-portal/news/add/', views.admin_news_add, name='admin_news_add'),
    path('admin-portal/news/<uuid:news_id>/edit/', views.admin_news_edit, name='admin_news_edit'),          
    path('admin-portal/news/<uuid:news_id>/delete/', views.admin_news_delete, name='admin_news_delete'),    

    path('admin-portal/blog/', views.admin_blogs, name='admin_blogs'),
    path('admin-portal/blog/add/', views.admin_blog_add, name='admin_blog_add'),
    path('admin-portal/blog/<int:blog_id>/edit/', views.admin_blog_edit, name='admin_blog_edit'),
    path('admin-portal/blog/<int:blog_id>/delete/', views.admin_blog_delete, name='admin_blog_delete'),

    path('admin-portal/stories/', views.admin_stories, name='admin_stories'),
    path('admin-portal/stories/add/', views.admin_story_add, name='admin_story_add'),
    path('admin-portal/stories/<int:story_id>/edit/', views.admin_story_edit, name='admin_story_edit'),
    path('admin-portal/stories/<int:story_id>/delete/', views.admin_story_delete, name='admin_story_delete'),

    path('admin-portal/resources/', views.admin_resources, name='admin_resources'),
    path('admin-portal/resources/add/', views.admin_resource_add, name='admin_resource_add'),
    path('admin-portal/resources/<uuid:resource_id>/edit/', views.admin_resource_edit, name='admin_resource_edit'),      
    path('admin-portal/resources/<uuid:resource_id>/delete/', views.admin_resource_delete, name='admin_resource_delete'),

    path('admin-portal/volunteers/<uuid:volunteer_id>/payment-summary/', views.volunteer_payment_summary, name='admin_volunteer_payment_summary'),
    path('admin-portal/volunteers/', views.admin_volunteers, name='admin_volunteers'),
    path('admin-portal/volunteers/add/', views.admin_volunteer_add, name='admin_volunteer_add'),
    path('admin-portal/volunteers/<uuid:volunteer_id>/review/', views.admin_volunteer_review, name='admin_volunteer_review'),
    path('admin-portal/volunteers/<uuid:volunteer_id>/edit/', views.admin_volunteer_edit, name='admin_volunteer_edit'),
    path('admin-portal/volunteers/<uuid:volunteer_id>/delete/', views.admin_volunteer_delete, name='admin_volunteer_delete'),

    path('admin-portal/feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin-portal/feedback/<int:feedback_id>/delete/', views.admin_feedback_delete, name='admin_feedback_delete'),
    path('admin-portal/feedback/<int:feedback_id>/respond/', views.admin_feedback_respond, name='admin_feedback_respond'),
    path('admin-portal/feedback/<int:feedback_id>/mark-addressed/', views.admin_feedback_mark_addressed, name='admin_feedback_mark_addressed'),
    path('admin-portal/feedback/<int:feedback_id>/mark-unaddressed/', views.admin_feedback_mark_unaddressed, name='admin_feedback_mark_unaddressed'),
    path('admin-portal/feedback/<int:feedback_id>/mark-in-progress/', views.admin_feedback_mark_in_progress, name='admin_feedback_mark_in_progress'),
    path('admin-portal/feedback/<int:feedback_id>/mark-resolved/', views.admin_feedback_mark_resolved, name='admin_feedback_mark_resolved'),
    path('admin-portal/feedback/<int:feedback_id>/mark-rejected/', views.admin_feedback_mark_rejected, name='admin_feedback_mark_rejected'),
    path('admin-portal/feedback/<int:feedback_id>/mark-duplicate/', views.admin_feedback_mark_duplicate, name='admin_feedback_mark_duplicate'),
    path('admin-portal/feedback/<int:feedback_id>/mark-wontfix/', views.admin_feedback_mark_wontfix, name='admin_feedback_mark_wontfix'),
    path('admin-portal/feedback/<int:feedback_id>/mark-needsinfo/', views.admin_feedback_mark_needsinfo, name='admin_feedback_mark_needsinfo'),
    path('admin-portal/feedback/<int:feedback_id>/mark-accepted/', views.admin_feedback_mark_accepted, name='admin_feedback_mark_accepted'),
    path('admin-portal/feedback/<int:feedback_id>/mark-reopened/', views.admin_feedback_mark_reopened, name='admin_feedback_mark_reopened'),

    path('admin-portal/cloudinary-signature/', views.cloudinary_signature, name='cloudinary_signature')
]