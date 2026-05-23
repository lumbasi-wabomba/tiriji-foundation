from django.db import models
import math
import uuid
from django.db.models.signals import post_save
from datetime import timedelta
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import (
    EncryptedEmailField,
    EncryptedCharField,
)

class program(models.Model):
    program_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    program_description = models.TextField()
    program_location = models.CharField(max_length=100)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    week_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title


class volunteer(models.Model):
    volunteer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = EncryptedEmailField(unique=True)
    occupation = models.CharField(max_length=100)
    phone_number = EncryptedCharField(max_length=20)
    id_pass_no = EncryptedCharField(max_length=50, verbose_name="ID/Passport No")
    starting_date = models.DateField()
    end_date = models.DateField()
    residence = models.CharField(max_length=100)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = EncryptedCharField(max_length=20)
    program_id = models.ForeignKey( program, on_delete=models.CASCADE, null=True, blank=True, related_name='volunteers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    APPLICATION_STATUS = [
        ('submitted', 'Submitted'),
        ('payment_pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS,
        default='submitted'
    )
    calculated_fee = models.DecimalField( max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def duration_weeks(self):
        total_days = (self.end_date - self.starting_date).days
        return math.ceil(total_days / 7)
    
    @property
    def fee(self):
        if not self.program_id:
            return 0

        if self.duration_weeks <= 2:
            return self.program_id.week_fee * self.duration_weeks
        elif self.duration_weeks <= 4:
            return self.program_id.week_fee * self.duration_weeks
        elif self.duration_weeks <= 8:
            return self.program_id.week_fee * self.duration_weeks
        else:
            extra_weeks = self.duration_weeks - 8
            extra_fee = extra_weeks * self.program_id.week_fee 
            return self.program_id.eight_week_fee + extra_fee
        

    def __str__(self):
        program_title = self.program_id.title if self.program_id else "No Program"
        return (
            f"{self.first_name} {self.last_name} "
            f"registered for {program_title} "
            f"program from {self.starting_date} "
            f"to {self.end_date}"
        )
    

class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank', 'Bank Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    amount = models.DecimalField( max_digits=10, decimal_places=2)
    payment_method = models.CharField( max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_reference = models.CharField( max_length=100, blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.payment_method} "
            f"- {self.amount} "
            f"- {self.status}"
        )


class donation(models.Model):
    DONATION_TYPES = [
        ('general', 'General Fund'),
        ('children', 'Children Program'),
        ('women', 'Women Empowerment'),
        ('community', 'Regenerative Communities'),
        ('volunteer', 'Volunteer Sponsorship'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank', 'Bank Transfer'),
    ]
    # IDENTIFIERS
    donation_id = models.UUIDField( primary_key=True, default=uuid.uuid4, editable=False)
    merchant_reference_id = models.CharField( max_length=100, unique=True )
    pesapal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # DONOR INFORMATION
    donor_name = models.CharField( max_length=100, blank=True, null=True)
    donor_email = EncryptedEmailField( blank=True, null=True )
    donor_phone_number = EncryptedCharField( max_length=20, blank=True, null=True)
    
    # DONATION DETAILS
    donation_type = models.CharField( max_length=20, choices=DONATION_TYPES, default='general' )
    donation_reason = models.CharField( max_length=255, blank=True, null=True)
    amount = models.DecimalField( max_digits=10, decimal_places=2)
    currency = models.CharField( max_length=10, default='USD')
    is_monthly = models.BooleanField( default=False)
    payment_method = models.CharField( max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default ='pending')
    
    # PAYMENT DETAILS
    transaction = models.OneToOneField( Transaction, on_delete=models.CASCADE, related_name='donation', null=True, blank=True)
    authorization_code = models.CharField( max_length=100, blank=True, null=True)
    payment_reference = models.CharField( max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField( blank=True, null=True) 
    amount_paid = models.DecimalField( max_digits=10, decimal_places=2, blank=True, null=True)
    payer_phone_number = EncryptedCharField( max_length=20, blank=True, null=True)
    payer_email = EncryptedEmailField( blank=True, null=True)
    payer_name = EncryptedCharField( max_length=100, blank=True, null=True)

    # TIMESTAMPS
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        donor = ( self.donor_name if self.donor_name else "Anonymous")
        return (
            f"{donor} donated "
            f"{self.amount} "
            f"{self.currency}"
        )

    def save(self, *args, **kwargs):
        if not self.donation_id:
            self.donation_id = self._generate_identifier("DON")

        if not self.merchant_reference_id:
            self.merchant_reference_id = self._generate_identifier("TIR")

        super().save(*args, **kwargs)

    @classmethod
    def _generate_identifier(cls, prefix):
        while True:
            value = f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(donation_id=value).exists() and not cls.objects.filter(merchant_reference_id=value).exists():
                return value

class VolunteerPayment(models.Model):
    payment_ref = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    volunteer = models.OneToOneField( volunteer, on_delete=models.CASCADE, related_name='payment')
    transaction = models.OneToOneField( Transaction, on_delete=models.CASCADE, related_name='volunteer_payment')
    amount = models.DecimalField( max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_reference = models.CharField( max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.volunteer.first_name} {self.volunteer.last_name} - ${self.amount}"
        )


class events(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=False, blank=False)
    events_description = models.TextField()
    image_url = models.URLField(max_length=250, null=True, blank=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    event_location = models.CharField(max_length=100)
    event_date = models.DateField()

    def __str__(self):
        program_title = self.program_id.title if self.program_id else "No Program"
        return f"{self.title} event scheduled for {self.event_date} at {self.event_location} under {program_title} program"


class event_registration(models.Model):
    registration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.ForeignKey(events, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100, null=False, blank=False)
    email = EncryptedEmailField(null=True, blank=True)
    phone_number = EncryptedCharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} registered for {self.event_id.title} event"


class event_payment(models.Model):
    PAYMENT_STATUS = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
    ]

    status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default='pending')
    registration = models.OneToOneField( event_registration, on_delete=models.CASCADE)
    amount = models.DecimalField( max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_reference = models.CharField( max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registration} - ${self.amount}"


class news(models.Model):
    news_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=False, blank=False)
    news_description = models.TextField()
    image_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='news')
    event_id = models.ForeignKey(events, on_delete=models.CASCADE, null=True, blank=True, related_name='news')

    def __str__(self):
        if self.program_id and self.event_id:
            return f"{self.title} news related to {self.program_id.title} program and {self.event_id.title} event"
        elif self.program_id:
            return f"{self.title} news related to {self.program_id.title} program"
        elif self.event_id:
            return f"{self.title} news related to {self.event_id.title} event"
        else:
            return self.title
class BlogPost(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    excerpt = models.TextField()
    body = models.TextField()
    image = models.ImageField(upload_to='temp/', blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    source_url = models.URLField(max_length=500, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
class resources(models.Model):
    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=False, blank=False)
    resources_description = models.TextField()
    image_url = models.URLField(max_length=250, null=True, blank=True)
    file_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='resources')

    def __str__(self):
        program_title = self.program_id.title if self.program_id else "No Program"
        return f"{self.title} resource related to {program_title} program"


class employees(models.Model):
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = EncryptedEmailField(unique=True, primary_key=True)
    role = models.CharField(max_length=100)
    phone_number = EncryptedCharField(max_length=20)
    id_pass_no = EncryptedCharField(max_length=50, verbose_name="ID/Passport No")
    starting_date = models.DateField()
    residence = models.CharField(max_length=100)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = EncryptedCharField(max_length=20)
    bio = models.TextField()
    profile_image_url = models.URLField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"


class partners(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    partners_description = models.TextField()
    profile_logo_url = models.URLField(max_length=250, null=True, blank=True)
    website_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_employee = models.ForeignKey(employees, on_delete=models.SET_NULL, null=True, blank=True, related_name='partners')  
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='partners')

    def __str__(self):
        program_title = self.program_id.title if self.program_id else "No Program"
        if self.assigned_employee:
            return f"{self.name} partner related to {program_title} program and assigned to {self.assigned_employee.first_name} {self.assigned_employee.last_name}" 
        else:
            return f"{self.name} partner related to {program_title} program"


class gallery(models.Model):
    image_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    image_description = models.TextField()
    image_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='program_gallery')
    event_id = models.ForeignKey(events, on_delete=models.CASCADE, null=True, blank=True, related_name='event_gallery')

    def __str__(self):
        if self.program_id and self.event_id:
            return f"{self.title} image related to {self.program_id.title} program and {self.event_id.title} event"
        elif self.program_id:
            return f"{self.title} image related to {self.program_id.title} program"
        elif self.event_id:
            return f"{self.title} image related to {self.event_id.title} event"
        else:
            return self.title            


# IMPACT / PROGRAM STORYTELLING
class ImpactPageChoices(models.TextChoices):
    CHILDREN = 'children', 'Children Program'
    WOMEN = 'women', 'Women Empowerment'
    COMMUNITY = 'community', 'Regenerative Communities'

class ImpactMetric(models.Model):
    page = models.CharField(max_length=20, choices=ImpactPageChoices.choices)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'label']

    def __str__(self):
        return f"{self.value} {self.label} ({self.get_page_display()})"


class FeaturedPerson(models.Model):
    FEATURE_TYPES = [
        ('scholar', 'Scholar of the Week'),
        ('entrepreneur', 'Entrepreneur of the Month'),
        ('mentor', 'Mentor Spotlight'),
    ]

    page = models.CharField(max_length=20, choices=ImpactPageChoices.choices)
    feature_type = models.CharField(max_length=30, choices=FEATURE_TYPES)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(blank=True, null=True)
    headline = models.CharField(max_length=150)
    short_bio = models.TextField()
    achievement = models.CharField(max_length=255, blank=True, null=True)
    dream_or_goal = models.CharField(max_length=255, blank=True, null=True)
    quote = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_feature_type_display()}"


class SuccessStory(models.Model):
    page = models.CharField(max_length=20, choices=ImpactPageChoices.choices)
    title = models.CharField(max_length=150)
    person_name = models.CharField(max_length=100, blank=True, null=True)
    challenge = models.TextField()
    intervention = models.TextField()
    outcome = models.TextField()
    quote = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = 'Success stories'

    def __str__(self):
        return self.title


class InspirationVideo(models.Model):
    page = models.CharField(max_length=20, choices=ImpactPageChoices.choices)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=500, help_text='YouTube, Vimeo, Cloudinary, or direct video URL')
    thumbnail_url = models.URLField(max_length=250, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title


class PageMedia(models.Model):
    MEDIA_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]

    page = models.CharField(max_length=20, choices=ImpactPageChoices.choices)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='photo')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name_plural = 'Page media'

    def __str__(self):
        return f"{self.title} ({self.get_page_display()})"


class feedback(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('addressed', 'Addressed'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('duplicate', 'Duplicate'),
        ('wontfix', "Won't Fix"),
        ('needsinfo', 'Needs Info'),
        ('accepted', 'Accepted'),
        ('reopened', 'Reopened'),
    ]

    feedback_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    email = EncryptedEmailField(null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    response_message = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} ({self.email}): {self.message[:50]}..."

# @receiver(post_save, sender=program)
# def upload_program_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url'])


# @receiver(post_save, sender=events)
# def upload_event_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url'])


# @receiver(post_save, sender=news)
# def upload_news_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url', 'image'])


# @receiver(post_save, sender=resources)
# def upload_resource_files(sender, instance, **kwargs):
#     updated_fields = []
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 updated_fields.extend(['image_url', 'image'])
    
#     if instance.file and not instance.file_url:
#         if os.path.isfile(instance.file.path):
#             # For files, just upload without compression
#             result = cloudinary.uploader.upload(instance.file.path)
#             instance.file_url = result['secure_url']
#             os.remove(instance.file.path)
#             instance.file = None
#             updated_fields.append('file_url')
#             updated_fields.append('file')
    
#     if updated_fields:
#         instance.save(update_fields=updated_fields)


# @receiver(post_save, sender=employees)
# def upload_employee_image(sender, instance, **kwargs):
#     if instance.profile_image and not instance.profile_image_url:
#         if os.path.isfile(instance.profile_image.path):
#             compressed_path = compress_image(instance.profile_image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.profile_image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.profile_image.path)
#                 instance.profile_image = None
#                 instance.save(update_fields=['profile_image_url', 'profile_image'])


# @receiver(post_save, sender=partners)
# def upload_partner_logo(sender, instance, **kwargs):
#     if instance.profile_logo and not instance.profile_logo_url:
#         if os.path.isfile(instance.profile_logo.path):
#             compressed_path = compress_image(instance.profile_logo.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.profile_logo_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.profile_logo.path)
#                 instance.profile_logo = None
#                 instance.save(update_fields=['profile_logo_url', 'profile_logo'])


# @receiver(post_save, sender=gallery)
# def upload_gallery_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url', 'image'])

#     class Meta:
#         ordering = ['display_order', '-created_at']
#         verbose_name_plural = 'Page media'

#     def __str__(self):
#         return f"{self.title} ({self.get_page_display()})"

# @receiver(post_save, sender=FeaturedPerson)
# def upload_featured_person_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url', 'image'])


# @receiver(post_save, sender=SuccessStory)
# def upload_success_story_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url', 'image'])


# @receiver(post_save, sender=InspirationVideo)
# def upload_inspiration_video_thumbnail(sender, instance, **kwargs):
#     if instance.thumbnail and not instance.thumbnail_url:
#         if os.path.isfile(instance.thumbnail.path):
#             compressed_path = compress_image(instance.thumbnail.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.thumbnail_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.thumbnail.path)
#                 instance.thumbnail = None
#                 instance.save(update_fields=['thumbnail_url', 'thumbnail'])


# @receiver(post_save, sender=PageMedia)
# def upload_page_media_image(sender, instance, **kwargs):
#     if instance.image and not instance.image_url:
#         if os.path.isfile(instance.image.path):
#             compressed_path = compress_image(instance.image.path)
#             if compressed_path:
#                 result = cloudinary.uploader.upload(compressed_path)
#                 instance.image_url = result['secure_url']
#                 os.remove(compressed_path)
#                 os.remove(instance.image.path)
#                 instance.image = None
#                 instance.save(update_fields=['image_url', 'image'])
