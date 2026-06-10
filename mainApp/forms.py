from django import forms
from .models import Patient, Appointment, Payment, ContactMessage

class PatienttForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['full_name', 'phone', 'birth_date', 'gender', 'address']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['department', 'doctor', 'patient_name', 'patient_phone', 'service', 'lab_test', 'is_consultation', 'date', 'time_slot', 'status']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['appointment', 'online_appointment', 'payment_type', 'is_paid']


from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['full_name', 'phone', 'birth_date', 'gender', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'F.I.Sh kiriting'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomAdminLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=True)

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # Agar checkbox belgilangan bo'lsa, uzoq muddat saqlaydi, aks holda brauzer yopilganda o'chadi
        if not self.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(None)