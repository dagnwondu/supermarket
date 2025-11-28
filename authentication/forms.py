from django import forms
from .models import CustomUser


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'middle_name', 'last_name',
                  'email', 'password', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'middle_name', 'last_name',
                  'email', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'middle_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
            'user_type': forms.Select(attrs={'class': 'form-control', 'id': 'user_type'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If the user being edited is a superuser, disable all editable fields
        if self.instance.is_superuser:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'  # Disable all fields

            # Explicitly mark password as not editable for superuser
            self.fields['password'].widget.attrs['disabled'] = 'disabled'
            self.fields['password'].required = False

        # Exclude 'admin' from user_type choices if necessary
        if 'user_type' in self.fields:
            self.fields['user_type'].choices = [
                (key, label) for key, label in self.fields['user_type'].choices if key != 'admin'
            ]

    def clean(self):
        # Prevent editing of superuser details
        if self.instance.is_superuser:
            raise forms.ValidationError("Superuser accounts cannot be edited.")

        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Prevent saving any changes to superuser
        if self.instance.is_superuser:
            return user  # Don't save any changes for superusers

        if commit:
            user.save()

        # Save related staff info if it exists and the user is not a superuser
        if hasattr(self.instance, 'staff') and self.instance.staff:
            staff = self.instance.staff
            staff.middle_name = self.cleaned_data.get('middle_name', staff.middle_name)
            staff.contact_number = self.cleaned_data.get('contact_number', staff.contact_number)
            staff.address = self.cleaned_data.get('address', staff.address)
            staff.save()

        return user