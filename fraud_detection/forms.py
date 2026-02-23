from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TrainedModel, CustomUser

class ModelTrainingForm(forms.Form):
    dataset = forms.FileField(help_text='Upload the CSV file for training')
    algorithm_choices = [
        ('logistic', 'Logistic Regression'),
        ('random_forest', 'Random Forest'),
        ('xgboost', 'XGBoost')
        # ('neural_network', 'Neural Network')
    ]
    algorithms = forms.MultipleChoiceField(
        choices=algorithm_choices,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select algorithms to train and evaluate'
    )

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class PredictionForm(forms.Form):
    model = forms.ModelChoiceField(
        queryset=TrainedModel.objects.filter(is_active=True),
        empty_label=None,
        help_text='Select a trained model for prediction'
    )
    amount = forms.FloatField(
        help_text='Transaction amount (e.g., 123.45)',
        widget=forms.NumberInput(attrs={'placeholder': '123.45'})
    )
    ip_address = forms.GenericIPAddressField(
        help_text='IP address (e.g., 192.168.1.1)',
        widget=forms.TextInput(attrs={'placeholder': '192.168.1.1'})
    )
    timestamp = forms.DateTimeField(
        help_text='Transaction timestamp (YYYY-MM-DD HH:MM:SS)',
        widget=forms.DateTimeInput(attrs={'placeholder': '2024-01-01 12:00:00'})
    )
    CITY_CHOICES = [
        ('New York', 'New York'),
        ('London', 'London'),
        ('Tokyo', 'Tokyo'),
        ('Berlin', 'Berlin'),
        ('Mumbai', 'Mumbai'),
        ('Sydney', 'Sydney'),
        ('other', 'Other')
    ]
    location = forms.ChoiceField(
        choices=CITY_CHOICES,
        help_text='Select city',
        widget=forms.Select(attrs={'class': 'select2'})
    )
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other')
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        help_text='Select payment method',
        widget=forms.Select(attrs={'class': 'select2'})
    )
    DEVICE_INFO_CHOICES = [
        ('iphone', 'iPhone'),
        ('android', 'Android'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
        ('other', 'Other')
    ]
    device_info = forms.ChoiceField(
        choices=DEVICE_INFO_CHOICES,
        help_text='Select device type',
        widget=forms.Select(attrs={'class': 'select2'})
    )