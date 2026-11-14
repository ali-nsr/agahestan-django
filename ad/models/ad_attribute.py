from django.db import models
from django.utils.translation import gettext_lazy as _



class AdAttribute(models.Model):
    category_field = models.ForeignKey('ad.CategoryField', on_delete=models.CASCADE, verbose_name=_('فیلد دسته بندی'))
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, related_name='ad_attributes', verbose_name=_('آگهی'))
    value = models.CharField(max_length=500, verbose_name=_('مقدار'))

    class Meta:
        verbose_name = _('اتریبیوت آگهی')
        verbose_name_plural = _('اتریبیوت های آگهی')

        indexes = [
            models.Index(fields=['ad', 'category_field']),
        ]
        unique_together = ('ad', 'category_field')  # هر فیلد در هر آگهی فقط یک مقدار

    def __str__(self):
        return f"{self.category_field} - {self.value}"
