from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryField(models.Model):
    class FieldType(models.TextChoices):
        INTEGER = 'int', _('Integer')
        DECIMAL = 'decimal', _('Decimal')
        BOOLEAN = 'bool', _('Boolean')
        STRING = 'str', _('String')
        TEXT = 'text', _('Text')
        CHOICE = 'choice', _('Choice')
        MULTI_CHOICE = 'multi_choice', _('Multi Choice')

    category = models.ForeignKey('ad.Category', on_delete=models.CASCADE, related_name='fields', verbose_name=_('دسته بندی'))
    key = models.SlugField(max_length=100, unique=True, verbose_name=_('کلید'))
    label = models.CharField(max_length=100, verbose_name=_('لیبل'))
    type = models.CharField(max_length=20, choices=FieldType.choices, verbose_name=_('نوع'))
    is_required = models.BooleanField(default=True, verbose_name=_('اجباری'))
    data = models.JSONField(null=True, blank=True, verbose_name=_('دیتا'))

    # پیشنهاد: {"options":[...], "unit":"m2", "min":0, "max":1000, "widget":"range"}

    class Meta:
        verbose_name = _('فیلد دسته بندی')
        verbose_name_plural = _('فیلد های دسته بندی')
        indexes = [
            models.Index(fields=['category'])
        ]

    def __str__(self):
        return f"{self.category} - {self.label}"
