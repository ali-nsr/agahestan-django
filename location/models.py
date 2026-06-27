from django.db import models
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('نام'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('آدرس URL'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'provinces'
        verbose_name = _('استان')
        verbose_name_plural = _('استان ها')
        ordering = ('name',)
        indexes = [models.Index(fields=['slug'])]  # unique خودش ایندکس می‌سازد؛ این صرفاً صریح‌ترش می‌کند




class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name=_('استان'))
    name = models.CharField(max_length=50, verbose_name=_('نام'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('آدرس URL'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cities'
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
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('آدرس URL'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'neighborhoods'
        verbose_name = _('محله')
        verbose_name_plural = _('محله ها')
        ordering = ('name',)
        indexes = [models.Index(fields=['city'])]
        constraints = [
            models.UniqueConstraint(fields=['city', 'name'], name='uniq_neighborhood_name_per_city')
        ]


"""
python manage.py loaddata ad/fixtures/ad.json
python manage.py loaddata ad/fixtures/category.json && python manage.py loaddata ad/fixtures/category_field.json && python manage.py loaddata location/fixtures/provinces.json && python manage.py loaddata location/fixtures/cities.json && python manage.py loaddata location/fixtures/neighborhoods.json
"""
