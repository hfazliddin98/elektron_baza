from django import forms

from .models import Bolim, Qurilma, Xodim


class BootstrapMixin:
    """Barcha maydonlarga Bootstrap CSS klasslarini qo'shadi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for maydon in self.fields.values():
            widget = maydon.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                klass = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                klass = 'form-check-input'
            else:
                klass = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {klass}".strip()


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
