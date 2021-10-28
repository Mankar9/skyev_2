from django import forms
from app.models import Caso

from app.utils import naturalsize

class CrearCasoForm(forms.ModelForm):

    class Meta:
        model = Caso
        fields = ['titulo', 'descripcion']

# https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/3.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other

class CargarEvidenciaForm(forms.Form):

    max_upload_limit = 200 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    evidencia_file = forms.FileField(required = True, label = 'Evidencia <= '+ max_upload_limit_text, widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def clean(self):
        cleaned_data = super(CargarEvidenciaForm, self).clean()

        for ev in self.files.getlist('evidencia_file'):
            if len(ev) > self.max_upload_limit:
                self.add_error('evidencia_file', "Los archivos deben tener un tamaño menor a " + self.max_upload_limit_text)
                break

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ('email', 'empresa')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ('email', 'empresa')
