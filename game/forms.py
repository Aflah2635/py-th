from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters, '
            'including uppercase, lowercase, numbers, and special characters.'
        )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as error:
            raise ValidationError(error)

        # Additional custom password validation
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number.')
        if not any(char in '!@#$%^&*()' for char in password):
            raise ValidationError('Password must contain at least one special character (!@#$%^&*())')

        return password

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')

class AnswerForm(forms.Form):
    answer = forms.CharField(max_length=100)

    def clean_answer(self):
        answer = self.cleaned_data.get('answer')
        if not answer:
            raise forms.ValidationError('Answer cannot be empty')
            
        # Remove leading/trailing whitespace and convert to lowercase
        answer = answer.strip().lower()
        
        # Allow alphanumeric characters, spaces, hyphens, and basic punctuation
        answer = re.sub(r'[^\w\s\-.,!?]', '', answer)
        
        # Replace multiple spaces with single space
        answer = re.sub(r'\s+', ' ', answer)
        
        # Ensure the answer is not just whitespace after cleaning
        if not answer.strip():
            raise forms.ValidationError('Answer cannot be empty after cleaning')
            
        return answer