from django import forms
from .models import Review

class AddReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['place', 'rating', 'comment']
        widgets = {
            'place': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ReviewFormForDetailPage(forms.ModelForm):
    class Meta:
        model = Review
        # Exclude the 'place' field as it will be set automatically
        # It will be written under the place detail so the place selection is not required
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your experience...'}),
        }