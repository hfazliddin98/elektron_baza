from django import forms

from accounts.models import Usta
from config.forms import BootstrapMixin
from devices.models import Qurilma, Xodim

from .models import TamirYozuvi


def _faol_ustalar():
    return Usta.objects.filter(faol=True)


class MurojaatForm(BootstrapMixin, forms.ModelForm):
    """Xodim saytdan yuboradigan murojaat."""

    class Meta:
        model = TamirYozuvi
        fields = ['qurilma', 'muhimlik', 'muammo_tavsifi', 'rasm', 'tanlangan_usta']
        widgets = {
            'muammo_tavsifi': forms.Textarea(attrs={'rows': 4,
                                                    'placeholder': 'Qurilmada nima muammo bor?'}),
        }
        labels = {'tanlangan_usta': 'Usta (ixtiyoriy)'}
        help_texts = {
            'tanlangan_usta': 'Tanlamasangiz ish umumiy navbatga tushadi va bo\'sh usta oladi.',
            'muhimlik': 'Shoshilinch — dars yoki ish jarayoni to\'xtab qolgan hollarda.',
        }

    def __init__(self, *args, xodim=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tanlangan_usta'].queryset = _faol_ustalar()
        self.fields['tanlangan_usta'].empty_label = '— Farqi yo\'q —'
        if xodim is not None:
            self.fields['qurilma'].queryset = Qurilma.objects.filter(
                bolim=xodim.bolim,
            ).exclude(holati=Qurilma.Holat.YAROQSIZ)


class OperatorMurojaatForm(BootstrapMixin, forms.ModelForm):
    """Operator xodim nomidan ochadigan murojaat (qurilma olib kelinganda)."""

    class Meta:
        model = TamirYozuvi
        fields = ['xodim', 'qurilma', 'muhimlik', 'muammo_tavsifi', 'rasm']
        widgets = {'muammo_tavsifi': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qurilma'].queryset = Qurilma.objects.exclude(
            holati=Qurilma.Holat.YAROQSIZ,
        ).select_related('bolim')
        self.fields['xodim'].queryset = Xodim.objects.select_related('bolim')


class OziTamirForm(BootstrapMixin, forms.ModelForm):
    """Xodim o'zi ta'mirlagani haqidagi hisobot (admin tasdiqlaydi)."""

    class Meta:
        model = TamirYozuvi
        fields = ['qurilma', 'muammo_tavsifi', 'bajarilgan_ishlar',
                  'ehtiyot_qismlar', 'xarajat', 'rasm']
        widgets = {
            'muammo_tavsifi': forms.Textarea(attrs={'rows': 3,
                                                    'placeholder': 'Nima buzilgan edi?'}),
            'bajarilgan_ishlar': forms.Textarea(attrs={'rows': 3,
                                                       'placeholder': 'Nima qildingiz?'}),
            'ehtiyot_qismlar': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {'muammo_tavsifi': 'Qanday nosozlik bor edi'}

    def __init__(self, *args, xodim=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bajarilgan_ishlar'].required = True
        if xodim is not None:
            self.fields['qurilma'].queryset = Qurilma.objects.filter(bolim=xodim.bolim)


class RadForm(BootstrapMixin, forms.Form):
    sabab = forms.CharField(
        label='Rad etish sababi', widget=forms.Textarea(attrs={'rows': 3}),
    )


class BiriktirishForm(BootstrapMixin, forms.Form):
    usta = forms.ModelChoiceField(label='Usta', queryset=Usta.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usta'].queryset = _faol_ustalar()


class YakunlashForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = TamirYozuvi
        fields = ['bajarilgan_ishlar', 'ehtiyot_qismlar', 'xarajat']
        widgets = {
            'bajarilgan_ishlar': forms.Textarea(attrs={'rows': 3}),
            'ehtiyot_qismlar': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bajarilgan_ishlar'].required = True


class BahoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = TamirYozuvi
        fields = ['baho', 'baho_izoh']
        widgets = {
            'baho': forms.RadioSelect,
            'baho_izoh': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Izoh (ixtiyoriy)'}),
        }
        labels = {'baho': 'Xizmatni baholang', 'baho_izoh': 'Izoh'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['baho'].required = True
        self.fields['baho'].choices = [(i, f'{i} ' + '★' * i) for i in range(1, 6)]


class TasdiqForm(BootstrapMixin, forms.Form):
    QARORLAR = [
        (TamirYozuvi.Tasdiq.TASDIQLANDI, 'Tasdiqlash'),
        (TamirYozuvi.Tasdiq.RAD, 'Rad etish'),
    ]
    qaror = forms.ChoiceField(label='Qaror', choices=QARORLAR, widget=forms.RadioSelect)
    izoh = forms.CharField(
        label='Izoh', required=False, widget=forms.Textarea(attrs={'rows': 2}),
        help_text='Rad etilsa sabab yozilishi shart.',
    )

    def clean(self):
        malumot = super().clean()
        if malumot.get('qaror') == TamirYozuvi.Tasdiq.RAD and not malumot.get('izoh', '').strip():
            self.add_error('izoh', 'Rad etish sababini yozing.')
        return malumot
