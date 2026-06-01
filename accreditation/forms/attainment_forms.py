from django import forms

from ..models import CourseAttainmentRecord


class CourseAttainmentRecordForm(forms.ModelForm):
    class Meta:
        model = CourseAttainmentRecord
        fields = ['academic_year', 'term', 'target_value', 'actual_value', 'conclusion', 'remark']
        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'conclusion': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }