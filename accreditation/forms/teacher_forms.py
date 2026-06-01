from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class TeacherForm(forms.ModelForm):
    status_flag = forms.ChoiceField(
        choices=(
            ('1', '启用'),
            ('0', '停用'),
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='账号状态'
    )
    login_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '留空则沿用当前密码'}),
        label='登录密码'
    )

    class Meta:
        model = User
        fields = [
            'username',
            'realname',
            'mobile',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'realname': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '工号 / 登录账号'
        self.fields['realname'].label = '姓名'
        self.fields['mobile'].label = '手机号'
        self.fields['status_flag'].initial = '1' if self.instance and self.instance.is_active else '0'
        if not self.instance.pk:
            self.fields['login_password'].widget.attrs['placeholder'] = '留空默认 123456'

    def clean_username(self):
        value = (self.cleaned_data.get('username') or '').strip()
        if not value:
            raise forms.ValidationError('请填写工号。')
        return value

    def clean_realname(self):
        value = (self.cleaned_data.get('realname') or '').strip()
        if not value:
            raise forms.ValidationError('请填写姓名。')
        return value

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.role = 'teacher'
        obj.is_active = self.cleaned_data.get('status_flag') == '1'

        password = (self.cleaned_data.get('login_password') or '').strip()
        if obj.pk:
            if password:
                obj.set_password(password)
        else:
            obj.set_password(password or '123456')

        if commit:
            obj.save()
        return obj
