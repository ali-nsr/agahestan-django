from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import json

from location.models import City, Neighborhood
from .models import Ad, AdAttribute, Category, CategoryField


MAX_IMAGES = 10
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image(image):
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(f'حجم «{image.name}» بیشتر از ۵ مگابایت است.')
    ct = getattr(image, 'content_type', '')
    if ct and not ct.startswith('image/'):
        raise ValidationError(f'«{image.name}» فایل تصویری نیست.')


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            'title', 'description',
            'price', 'is_negotiable',
            'province', 'city', 'neighborhood', 'address',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً: آپارتمان ۱۲۰ متری نوساز',
                'maxlength': 100,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'جزئیات ملک را کامل بنویسید...',
            }),
            # ⚠️ اینجا TextInput به جای NumberInput — مشکل اصلی قیمت
            'price': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً ۲۵۰۰۰۰۰۰۰۰',
                'id': 'id_price',
                'inputmode': 'numeric',
                'autocomplete': 'off',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'خیابان، کوچه، پلاک',
            }),
            'province': forms.Select(attrs={'class': 'form-select', 'id': 'id_province'}),
            'city': forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
            'neighborhood': forms.Select(attrs={'class': 'form-select', 'id': 'id_neighborhood'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.fixed_category = kwargs.pop('fixed_category', None)
        super().__init__(*args, **kwargs)

        self.fields['province'].required = True
        self.fields['city'].required = True
        self.fields['neighborhood'].required = False
        self.fields['address'].required = True

        # ═══ تعیین province_id و city_id از POST یا instance ═══
        province_id = None
        city_id = None

        if self.is_bound:
            # فرم POST شده → از داده‌های ارسالی
            province_id = self.data.get('province') or None
            city_id = self.data.get('city') or None
        elif self.instance and self.instance.pk:
            # ویرایش → از instance
            province_id = self.instance.province_id
            city_id = self.instance.city_id

        # ═══ پر کردن queryset بر اساس انتخاب فعلی ═══
        if province_id:
            self.fields['city'].queryset = City.objects.filter(province_id=province_id)
        else:
            self.fields['city'].queryset = City.objects.none()

        if city_id:
            self.fields['neighborhood'].queryset = Neighborhood.objects.filter(city_id=city_id)
        else:
            self.fields['neighborhood'].queryset = Neighborhood.objects.none()


    def clean_price(self):
        """حذف کاما از قیمت قبل از اعتبارسنجی."""
        price = self.cleaned_data.get('price')
        if price in (None, ''):
            return None
        # اگر رشته است، کاما و فاصله رو حذف کن
        if isinstance(price, str):
            price = price.replace(',', '').replace('،', '').strip()
            if not price:
                return None
            try:
                price = int(price)
            except ValueError:
                raise ValidationError('قیمت باید عدد باشد.')
        if price is not None and price < 0:
            raise ValidationError('قیمت نمی‌تواند منفی باشد.')
        return price

    def clean(self):
        cd = super().clean()
        if cd.get('price') is None and not cd.get('is_negotiable'):
            raise ValidationError('قیمت (یا ودیعه) را وارد کنید یا «توافقی» را انتخاب کنید.')
        return cd

    @transaction.atomic
    def save(self, commit=True):
        ad = super().save(commit=False)
        if self.user and not ad.user_id:
            ad.user = self.user
        if self.fixed_category and not ad.category_id:
            ad.category = self.fixed_category
        if not ad.pk:
            ad.status = Ad.Status.REVIEW
            ad.expires_at = timezone.now() + timedelta(days=30)
        if commit:
            ad.save()
        return ad


# ─── فرم داینامیک ───
def _make_field_from_cf(cf):
    data = cf.data or {}
    required = cf.is_required

    # ═══ فیلد وابسته (مدل) ═══
    if data.get('depends_on'):
        return forms.ChoiceField(
            label=cf.label,
            required=required,
            choices=[('', 'انتخاب کنید...')],
            widget=forms.Select(attrs={
                'class': 'form-select cascading-target',
                'data-depends-on': data['depends_on'],
                'data-field-key': cf.key,
            }),
        )

    # ═══ Choice (برند یا ساده) ═══
    if cf.type == cf.FieldType.CHOICE:
        options = [(o, o) for o in (data.get('options') or [])]
        attrs = {'class': 'form-select', 'data-field-key': cf.key}
        if data.get('models'):
            attrs['class'] = 'form-select cascading-source'
            attrs['data-models'] = json.dumps(data['models'], ensure_ascii=False)
        return forms.ChoiceField(
            label=cf.label,
            required=required,
            choices=[('', 'انتخاب کنید...')] + options,
            widget=forms.Select(attrs=attrs),
        )

    # بقیه انواع بدون تغییر...
    if cf.type == cf.FieldType.INTEGER:
        return forms.IntegerField(
            label=cf.label, required=required,
            min_value=data.get('min'), max_value=data.get('max'),
            widget=forms.NumberInput(attrs={'class': 'form-control', 'data-field-key': cf.key}),
        )
    if cf.type == cf.FieldType.DECIMAL:
        return forms.DecimalField(
            label=cf.label, required=required,
            min_value=data.get('min'), max_value=data.get('max'),
            widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'data-field-key': cf.key}),
        )
    if cf.type == cf.FieldType.BOOLEAN:
        return forms.BooleanField(
            label=cf.label, required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-field-key': cf.key}),
        )
    if cf.type == cf.FieldType.STRING:
        return forms.CharField(
            label=cf.label, required=required, max_length=255,
            widget=forms.TextInput(attrs={'class': 'form-control', 'data-field-key': cf.key}),
        )
    if cf.type == cf.FieldType.TEXT:
        return forms.CharField(
            label=cf.label, required=required,
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'data-field-key': cf.key}),
        )
    if cf.type == cf.FieldType.MULTI_CHOICE:
        options = [(o, o) for o in (data.get('options') or [])]
        return forms.MultipleChoiceField(
            label=cf.label, required=required, choices=options,
            widget=forms.SelectMultiple(attrs={
                'class': 'form-select select2-multi',
                'data-field-key': cf.key,
            }),
        )

    return forms.CharField(
        label=cf.label, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'data-field-key': cf.key}),
    )


def build_category_form(category, data=None, initial=None):
    fields = {}
    for cf in category.get_category_fields():
        fields[f'cf_{cf.pk}'] = _make_field_from_cf(cf)
    FormClass = type('DynamicCategoryForm', (forms.Form,), fields)
    return FormClass(data=data, initial=initial)


def save_category_attributes(ad, cleaned_data, category):
    seen_cf_pks = set()
    for cf in category.get_category_fields():
        seen_cf_pks.add(cf.pk)
        key = f'cf_{cf.pk}'
        if key not in cleaned_data:
            continue
        value = cleaned_data[key]
        if value in (None, '', [], False):
            AdAttribute.objects.filter(ad=ad, category_field=cf).delete()
            continue
        if isinstance(value, list):
            value = ','.join(str(v) for v in value)
        else:
            value = str(value)
        AdAttribute.objects.update_or_create(
            ad=ad, category_field=cf,
            defaults={'value': value[:500]},
        )
    AdAttribute.objects.filter(ad=ad).exclude(
        category_field_id__in=seen_cf_pks
    ).delete()