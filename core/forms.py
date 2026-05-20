from django import forms
from .models import program, events, news, resources ,volunteer , donation 

class ProgramForm(forms.ModelForm):
    class Meta:
        model = program
        fields = [ 'title', 'program_description', 'image', 'two_week_fee', 'four_week_fee', 'eight_week_fee', 'extra_week_fee',]
        
        widgets = {
            'program_description': forms.Textarea(attrs={'rows': 4}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = events
        fields = ['event_id', 'title', 'events_description', 'image', 'program_id', 'event_location', 'event_date']
        widgets = {
            'events_description': forms.Textarea(attrs={'rows': 4}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = news
        fields = ['news_id', 'title', 'news_description', 'image', 'program_id', 'event_id']
        widgets = {
            'news_description': forms.Textarea(attrs={'rows': 4}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = resources
        fields = ['resource_id', 'title', 'resources_description', 'image', 'file', 'program_id']
        widgets = {
            'resources_description': forms.Textarea(attrs={'rows': 4}),
        }

class VolunteerForm(forms.ModelForm):

    class Meta:

        model = volunteer

        fields = ['first_name', 'last_name', 'email', 'occupation', 'phone_number', 'id_pass_no', 'residence', 'starting_date', 'end_date', 'emergency_contact_name', 'emergency_contact_phone', 'program_id', ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'occupation': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'id_pass_no': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'residence': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'starting_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'program': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('starting_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:

            if end_date <= start_date:

                raise forms.ValidationError(
                    "End date must be after start date."
                )

        return cleaned_data

class DonationForm(forms.ModelForm):

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:

        model = donation

        fields = [
            'donor_name',
            'donor_email',
            'donor_phone_number',
            'donation_type',
            'donation_reason',
            'amount',
            'payment_method',
            'is_monthly',
        ]

        widgets = {

            'donor_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'donor_email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'donation_type': forms.Select(attrs={
                'class': 'form-control'
            }),

            'message': forms.Textarea(attrs={
                'class': 'form-control'
            }),
        }