from django import forms

from ..models import (
    Course,
    CourseGoal,
    CourseIndicatorRelation,
    GoalIndicatorRelation,
)


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'credit', 'course_type', 'term', 'teacher', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }


class CourseGoalForm(forms.ModelForm):
    class Meta:
        model = CourseGoal
        fields = ['code', 'content', 'sort']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sort': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CourseIndicatorRelationForm(forms.ModelForm):
    class Meta:
        model = CourseIndicatorRelation
        fields = ['indicator', 'support_level', 'weight']
        widgets = {
            'indicator': forms.Select(attrs={'class': 'form-control'}),
            'support_level': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GoalIndicatorRelationForm(forms.ModelForm):
    class Meta:
        model = GoalIndicatorRelation
        fields = ['indicator', 'weight']
        widgets = {
            'indicator': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }