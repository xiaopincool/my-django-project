from django import forms

from ..models import ContinuousImprovement


# 持续改进表单
class ContinuousImprovementForm(forms.ModelForm):
    class Meta:
        model = ContinuousImprovement
        exclude = ['creator', 'create_time', 'update_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入问题标题'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'problem_description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入问题描述'}
            ),
            'improvement_measure': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入整改措施'}
            ),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'planned_finish_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'progress': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '100'}
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'effect_evaluation': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入效果评价'}
            ),
            'remark': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入备注'}
            ),
        }

    def clean_progress(self):
        progress = self.cleaned_data.get('progress') or 0
        if progress < 0 or progress > 100:
            raise forms.ValidationError('进度只能在 0 到 100 之间')
        return progress