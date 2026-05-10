from django import forms
from .models import program, events, news, resources

class ProgramForm(forms.ModelForm):
    class Meta:
        model = program
        fields = ['program_id', 'title', 'program_description', 'image']
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
