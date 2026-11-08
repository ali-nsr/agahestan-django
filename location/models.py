from django.db import models
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('نام'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('اسلاگ'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('استان')
        verbose_name_plural = _('استان ها')
        ordering = ('name',)
        indexes = [models.Index(fields=['slug'])]  # unique خودش ایندکس می‌سازد؛ این صرفاً صریح‌ترش می‌کند


class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name=_('استان'))
    name = models.CharField(max_length=50, verbose_name=_('نام'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('اسلاگ'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('شهر')
        verbose_name_plural = _('شهر ها')
        ordering = ('name',)
        indexes = [models.Index(fields=['province'])]
        constraints = [
            models.UniqueConstraint(fields=['province', 'name'], name='uniq_city_name_per_province')
        ]


class Neighborhood(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='neighborhoods', verbose_name=_('شهر'))
    name = models.CharField(max_length=50, verbose_name=_('نام'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('اسلاگ'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('محله')
        verbose_name_plural = _('محله ها')
        ordering = ('name',)
        indexes = [models.Index(fields=['city'])]
        constraints = [
            models.UniqueConstraint(fields=['city', 'name'], name='uniq_neighborhood_name_per_city')
        ]


load_fixtures = """

python manage.py loaddata categories.json & python manage.py loaddata real_estate_fields.json

python manage.py loaddata provinces.json & python manage.py loaddata cities.json & python manage.py loaddata neighborhoods.json


"""
