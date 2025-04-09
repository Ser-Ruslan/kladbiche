from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Grave, PersonalNote, EditProposal, Cemetery

class CemeteryForm(forms.ModelForm):
    """
    Форма для создания и редактирования кладбищ
    """
    class Meta:
        model = Cemetery
        fields = ['name', 'address', 'description', 'coordinates']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
        }

class GraveForm(forms.ModelForm):
    """
    Форма для создания и редактирования захоронений (для администраторов)
    """
    class Meta:
        model = Grave
        fields = ['full_name', 'birth_date', 'death_date', 'description', 'polygon_coordinates', 'photo', 'cemetery']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'death_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'polygon_coordinates': forms.HiddenInput(),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'cemetery': forms.Select(attrs={'class': 'form-control'}),
        }

class PersonalNoteForm(forms.ModelForm):
    """
    Форма для добавления/редактирования личных заметок
    """
    class Meta:
        model = PersonalNote
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите вашу личную заметку'}),
        }


class EditProposalForm(forms.ModelForm):
    """
    Форма для отправки предложений по редактированию описания захоронения
    """
    class Meta:
        model = EditProposal
        fields = ['proposed_description']
        widgets = {
            'proposed_description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Введите ваше предложение по редактированию описания'
            }),
        }


class ModerateProposalForm(forms.ModelForm):
    """
    Форма для модерации предложений администраторами
    """
    MODERATION_CHOICES = (
        ('approve', _('Одобрить')),
        ('reject', _('Отклонить')),
    )
    
    moderation_action = forms.ChoiceField(
        label=_('Действие'),
        choices=MODERATION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = EditProposal
        fields = ['rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Причина отклонения (необходима при отклонении)'
            }),
        }
