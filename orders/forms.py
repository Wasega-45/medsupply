from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from core.models import Medicine


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('priority', 'notes')
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Any additional information about this order...',
            }),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ('medicine', 'quantity')
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        quantity = cleaned_data.get('quantity')

        # If both empty → this is an unused row; skip validation
        if not medicine and not quantity:
            return cleaned_data

        # If one is filled but not the other → error
        if not medicine:
            raise forms.ValidationError("Please select a medicine.")
        if not quantity or quantity < 1:
            raise forms.ValidationError("Please enter a valid quantity (1 or more).")

        return cleaned_data


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
)