"""Formalar uchun umumiy yordamchilar."""

from django import forms


class BootstrapMixin:
    """Barcha maydonlarga Bootstrap CSS klasslarini qo'shadi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for maydon in self.fields.values():
            widget = maydon.widget
            if isinstance(widget, forms.RadioSelect):
                continue
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                klass = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                klass = 'form-check-input'
            else:
                klass = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {klass}".strip()
