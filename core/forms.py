from django import forms
from .models import program, events, news, resources, volunteer, donation, feedback, ImpactMetric, FeaturedPerson, SuccessStory, InspirationVideo, PageMedia
from .admin_roles import ADMIN_ROLE_CHOICES

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
        fields = ['title', 'events_description', 'image', 'program_id', 'event_location', 'event_date']
        widgets = {
            'events_description': forms.Textarea(attrs={'rows': 4}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = news
        fields = ['title', 'news_description', 'image', 'program_id', 'event_id']
        widgets = {
            'news_description': forms.Textarea(attrs={'rows': 4}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = resources
        fields = ['title', 'resources_description', 'image', 'file', 'program_id']
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

            'program_id': forms.Select(attrs={
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

            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_monthly': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'donor_phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'donation_reason': forms.Textarea(attrs={
                'class': 'form-control'
            }), 
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class AdminUserForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=ADMIN_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        help_text='Required for new users. Leave blank when editing unless you want to reset it.',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, user_instance=None, **kwargs):
        self.user_instance = user_instance
        super().__init__(*args, **kwargs)
        if not user_instance:
            self.fields['password'].required = True

    def clean_username(self):
        from django.contrib.auth.models import User

        username = self.cleaned_data['username']
        query = User.objects.filter(username=username)
        if self.user_instance:
            query = query.exclude(pk=self.user_instance.pk)
        if query.exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def clean_email(self):
        from django.contrib.auth.models import User

        email = self.cleaned_data['email']
        query = User.objects.filter(email=email)
        if self.user_instance:
            query = query.exclude(pk=self.user_instance.pk)
        if query.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

class ImpactMetricForm(forms.ModelForm):
    class Meta:
        model = ImpactMetric
        fields = ['page', 'label', 'value', 'description', 'display_order', 'is_active']
        widgets = {
            'page': forms.Select(attrs={'class': 'form-control'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class FeaturedPersonForm(forms.ModelForm):
    class Meta:
        model = FeaturedPerson
        fields = ['page', 'feature_type', 'name', 'age', 'headline', 'short_bio', 'achievement', 'dream_or_goal', 'quote', 'image', 'is_featured']
        widgets = {
            'page': forms.Select(attrs={'class': 'form-control'}),
            'feature_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'short_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'achievement': forms.TextInput(attrs={'class': 'form-control'}),
            'dream_or_goal': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ['page', 'title', 'person_name', 'challenge', 'intervention', 'outcome', 'quote', 'image', 'is_featured']
        widgets = {
            'page': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'challenge': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'intervention': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InspirationVideoForm(forms.ModelForm):
    class Meta:
        model = InspirationVideo
        fields = ['page', 'title', 'description', 'video_url', 'thumbnail', 'is_featured']
        widgets = {
            'page': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class PageMediaForm(forms.ModelForm):
    class Meta:
        model = PageMedia
        fields = ['page', 'media_type', 'title', 'description', 'image', 'video_url', 'display_order']
        widgets = {
            'page': forms.Select(attrs={'class': 'form-control'}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
