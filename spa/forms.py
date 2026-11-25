from django import forms
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Solicitud, UsuarioAutorizado

class TurnoForm(forms.Form):

    TRATAMIENTOS = [
        ('', 'Seleccioná un tratamiento'),
        ('Masaje relajante', 'Masaje relajante'),
        ('Tratamiento corporal', 'Tratamiento corporal'),
        ('Tratamiento facial', 'Tratamiento facial'),
    ]

    nombre = forms.CharField(
        label='Nombre y apellido',
        max_length=100,
        error_messages={
            'required': 'Ingresá tu nombre y apellido.'
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre y apellido'
        })
    )

    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'placeholder': 'Escribí tu consulta',
            'rows': 4
        }),
        required=True
    )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']

        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError(
                'El nombre y apellido deben contener solamente letras.'
            )

        return nombre

    email = forms.EmailField(
        label='Email',
        error_messages={
            'required': 'Ingresá tu email.',
            'invalid': 'Ingresá un email válido.'
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'tuemail@ejemplo.com'
        })
    )

    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        error_messages={
            'required': 'Ingresá tu teléfono.'
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu teléfono',
            'type': 'tel',
            'inputmode': 'numeric',
            'pattern': '[0-9]+'
        })
    )

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']

        if not telefono.isdigit():
            raise forms.ValidationError(
                'El teléfono debe contener solamente números.'
            )

        return telefono

    tratamiento = forms.ChoiceField(
        label='Tratamiento',
        choices=TRATAMIENTOS,
        error_messages={
            'required': 'Seleccioná un tratamiento.',
            'invalid_choice': 'Seleccioná un tratamiento válido.'
        }
    )

    fecha = forms.DateField(
        label='Fecha preferida',
        error_messages={
            'required': 'Seleccioná una fecha.',
            'invalid': 'Ingresá una fecha válida.'
        },
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': date.today().isoformat()
        })
    )

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < date.today():
            raise forms.ValidationError(
                'La fecha seleccionada no puede ser anterior a hoy.'
            )

        return fecha


class SolicitudForm(forms.ModelForm):
    tratamiento = forms.ChoiceField(
        label='Tratamiento',
        choices=TurnoForm.TRATAMIENTOS
    )

    class Meta:
        model = Solicitud

        fields = [
            'nombre',
            'email',
            'telefono',
            'tratamiento',
            'fecha',
            'mensaje',
        ]

        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'date', 'min': date.today().isoformat()}
            ),
            'mensaje': forms.Textarea(attrs={
                'rows': 4
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']

        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError(
                'El nombre y apellido deben contener solamente letras.'
            )

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']

        if not telefono.isdigit():
            raise forms.ValidationError(
                'El teléfono debe contener solamente números.'
            )

        return telefono

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < date.today():
            raise forms.ValidationError(
                'No se pueden seleccionar fechas anteriores a hoy.'
            )

        return fecha


class RegistroForm(UserCreationForm):

    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        label='Correo electrónico',
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if not UsuarioAutorizado.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                'Acceso restringido. No está autorizado '
                'a utilizar este sistema.'
            )

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo electrónico.'
            )

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.username = self.cleaned_data['email']
        usuario.email = self.cleaned_data['email']
        usuario.is_active = False

        if commit:
            usuario.save()

        return usuario


class LoginForm(AuthenticationForm):

    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingresá tu correo electrónico'
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingresá tu contraseña'
        })
    )

    error_messages = {
        'invalid_login': 'El correo electrónico o la contraseña son incorrectos.',
        'inactive': 'La cuenta todavía no fue validada.'
    }
