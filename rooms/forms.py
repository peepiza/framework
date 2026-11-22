from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Room


def validate_room_image(image):
    if image.size > 5 * 1024 * 1024:
        raise forms.ValidationError("Размер изображения должен быть не больше 5 МБ.")
    if image.image.format not in {"JPEG", "PNG", "WEBP"}:
        raise forms.ValidationError("Допустимы изображения JPEG, PNG и WebP.")


class RoomImageForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("image",)
        widgets = {"image": forms.ClearableFileInput(attrs={"class": "form-control"})}
        help_texts = {"image": "JPEG, PNG или WebP, до 5 МБ."}

    def clean_image(self):
        image = self.cleaned_data["image"]
        if isinstance(image, UploadedFile):
            validate_room_image(image)
        return image
