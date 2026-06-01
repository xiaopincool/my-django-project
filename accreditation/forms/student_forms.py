from django import forms

from ..models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'student_no',
            'college_name',
            'major_name',
            'grade_name',
            'class_name',
            'gender',
            'mobile',
            'status',
            'remark',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_no': forms.TextInput(attrs={'class': 'form-control'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'major_name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
