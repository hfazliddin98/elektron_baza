from django import forms

from config.forms import BootstrapMixin

from .models import Bolim, Qurilma, Xodim


class QurilmaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Qurilma
        fields = [
            'inventar_raqami', 'turi', 'modeli', 'seriya_raqami',
            'bolim', 'xodim', 'holati', 'olingan_sana',
        ]
        widgets = {
            'olingan_sana': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_inventar_raqami(self):
        return self.cleaned_data['inventar_raqami'].strip()


class BolimForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Bolim
        fields = ['nomi', 'bino', 'xona']


class XodimForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Xodim
        fields = ['fio', 'bolim', 'lavozimi', 'telefon', 'user', 'telegram_id']


class ImportForm(BootstrapMixin, forms.Form):
    fayl = forms.FileField(
        label='Excel fayl (.xlsx)',
        widget=forms.FileInput(attrs={'accept': '.xlsx'}),
    )
    yangilash = forms.BooleanField(
        label='Mavjud yozuvlarni yangilash',
        required=False,
        help_text="Belgilanmasa, bazada bor yozuvlar o'zgarishsiz qoldiriladi.",
    )

    def clean_fayl(self):
        fayl = self.cleaned_data['fayl']
        if not fayl.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Faqat .xlsx formatidagi fayl qabul qilinadi.')
        return fayl
