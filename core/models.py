from django.db import models
import cloudinary
import cloudinary.uploader
import os
from .media_compress import compress_image, compress_video 

class program(models.Model):
    program_id = models.IntegerField(primary_key=True, db_index=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    program_description = models.TextField()
    image = models.ImageField(upload_to='temp/', blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            compressed_path = compress_image(self.image.path)
            if compressed_path:
                result = cloudinary.uploader.upload(compressed_path)
                self.image_url = result['secure_url']
                os.remove(compressed_path)
                os.remove(self.image.path)
                self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class volunteer(models.Model):
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(primary_key=True)
    occupation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    id_pass_no = models.CharField(max_length=50, verbose_name="ID/Passport No")
    starting_date = models.DateField()
    end_date = models.DateField()
    residence = models.CharField(max_length=100)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='volunteers')


    def __str__(self):
        return f"{self.first_name} {self.last_name} registered for {self.program_id.title} program that starts on {self.start_date} and ends on {self.end_date}"


class events(models.Model):
    event_id = models.IntegerField(primary_key=True, db_index=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    events_description = models.TextField()
    image = models.ImageField(upload_to='temp/', blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    event_location = models.CharField(max_length=100)
    event_date = models.DateField()

    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            compressed_path = compress_image(self.image.path)
            if compressed_path:
                result = cloudinary.uploader.upload(compressed_path)
                self.image_url = result['secure_url']
                os.remove(compressed_path)
                os.remove(self.image.path)
                self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} event scheduled for {self.event_date} at {self.location} under {self.program_id.title} program"


class news(models.Model):
    news_id = models.IntegerField(primary_key=True, db_index=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    news_description = models.TextField()
    image = models.ImageField(upload_to='temp/', blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='news')
    event_id = models.ForeignKey(events, on_delete=models.CASCADE, null=True, blank=True, related_name='news')

    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            compressed_path = compress_image(self.image.path)
            if compressed_path:
                result = cloudinary.uploader.upload(compressed_path)
                self.image_url = result['secure_url']
                os.remove(compressed_path)
                os.remove(self.image.path)
                self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.program_id and self.event_id:
            return f"{self.title} news related to {self.program_id.title} program and {self.event_id.title} event"
        elif self.program_id:
            return f"{self.title} news related to {self.program_id.title} program"
        elif self.event_id:
            return f"{self.title} news related to {self.event_id.title} event"
        else:
            return self.title

class resources(models.Model):
    resource_id = models.IntegerField(primary_key=True, db_index=True)
    title = models.CharField(max_length=50, null=False, blank=False)
    resources_description = models.TextField()
    image = models.ImageField(upload_to='temp/', blank=True, null=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    file = models.FileField(upload_to='temp/', blank=True, null=True)
    file_url = models.URLField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='resources')

    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            compressed_path = compress_image(self.image.path)
            if compressed_path:
                result = cloudinary.uploader.upload(compressed_path)
                self.image_url = result['secure_url']
                os.remove(compressed_path)
                os.remove(self.image.path)
                self.image = None
        if self.file and not self.file_url:
            # check if video
            if self.file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                compressed_path = compress_video(self.file.path)
                if compressed_path:
                    result = cloudinary.uploader.upload(compressed_path, resource_type='video')
                    self.file_url = result['secure_url']
                    os.remove(compressed_path)
                    os.remove(self.file.path)
                    self.file = None
            else:
                # for other files, upload directly
                result = cloudinary.uploader.upload(self.file.path)
                self.file_url = result['secure_url']
                os.remove(self.file.path)
                self.file = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} resource related to {self.program_id.title} program"


#class employees(models.Model):
#    first_name = models.CharField(max_length=50, null=False, blank=False)
#    last_name = models.CharField(max_length=50, null=False, blank=False)
#    email = models.EmailField(unique=True, primary_key=True)
#    role = models.CharField(max_length=100)
#    phone_number = models.CharField(max_length=20)
#    id_pass_no = models.CharField(max_length=50, verbose_name="ID/Passport No")
#    starting_date = models.DateField(auto_now_add=True)
#    residence = models.CharField(max_length=100)
#    emergency_contact_name = models.CharField(max_length=100)
#    emergency_contact_phone = models.CharField(max_length=20)
#    bio = models.TextField()
#    profile_image_url = models.URLField(max_length=250, null=True, blank=True)
#
#    def __str__(self):
#        return f"{self.first_name} {self.last_name} - {self.role}"


#class patners(models.Model):
#    name = models.CharField(max_length=100, null=False, blank=False)
#    patners_description = models.TextField()
#    profile_logo_url = models.URLField(max_length=250, null=True, blank=True)
#    website_url = models.URLField(max_length=250, null=True, blank=True)
#    created_at = models.DateTimeField(auto_now_add=True)
#    assigned_employee = models.ForeignKey(employees, on_delete=models.SET_NULL, null=True, blank=True, related_name='patners')  
#    program_id = models.ForeignKey(program, on_delete=models.CASCADE, null=True, blank=True, related_name='patners')
#
#    def __str__(self):
#        if self.assigned_employee:
#            return f"{self.name} patner related to {self.program_id.title} program and assigned to {self.assigned_employee.first_name} {self.assigned_employee.last_name}" 
#        else:
#            return f"{self.name} patner related to {self.program_id.title} program"


class gallery(models.Model):
    image_id = models.IntegerField(primary_key=True, db_index=True)
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


class donations(models.Model):
    donations_id  = models.CharField(max_length=50, primary_key=True)
    merchant_reference_id = models.CharField(max_length=100, null=False, blank=False)
    pesapal_transaction_id = models.CharField(max_length=100, null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    donation_reason = models.CharField(max_length=255, null=True, blank=True)
    donor_email = models.EmailField(null=True, blank=True)
    donor_phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Donation {self.donations_id} of {self.amount} {self.currency} via {self.payment_method} with status {self.status}"


class feedback(models.Model):
    feedback_id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} ({self.email}): {self.message[:50]}..."