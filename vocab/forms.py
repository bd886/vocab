from django import forms
from .models import Category, Vocabulary

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Kategorie eingeben'}),
        }


class VocabularyForm(forms.ModelForm):
    class Meta:
        model = Vocabulary
        fields = ['german', 'english', 'category']
        widgets = {
            'german': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Deutsches Wort'}),
            'english': forms.TextInput(attrs={'class': 'input mb-3', 'placeholder': 'Englisches Wort'}),
            'category': forms.Select(attrs={'class': 'select'}),
        }