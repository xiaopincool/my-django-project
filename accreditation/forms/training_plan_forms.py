from django import forms

from ..models import TrainingPlan


class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ['college_name', 'major_name', 'plan_year', 'plan_file', 'remark', 'is_active']
        widgets = {
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'major_name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(),
        }
