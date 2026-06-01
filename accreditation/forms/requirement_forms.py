from django import forms

from ..models import GraduationRequirement, RequirementIndicator


class GraduationRequirementForm(forms.ModelForm):
    class Meta:
        model = GraduationRequirement
        fields = ['code', 'name', 'content', 'version', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }


class RequirementIndicatorForm(forms.ModelForm):
    class Meta:
        model = RequirementIndicator
        fields = ['code', 'content', 'sort', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sort': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }