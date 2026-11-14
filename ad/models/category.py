from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _




class CategoryManager(models.Manager):
    def get_all_categories(self):
        # فقط یک کوئری
        rows = list(
            self.all()
            .values('id', 'title', 'slug', 'parent_id', 'icon')
            .order_by('id')
        )

        # ساخت درخت بدون O(n^2)
        nodes = {}
        roots = []
        for r in rows:
            r['children'] = []
            nodes[r['id']] = r

        for r in rows:
            pid = r['parent_id']
            if pid:
                # ممکنه parent قبل یا بعد دیده شود، ولی چون nodes کامل است، مشکلی نیست
                nodes[pid]['children'].append(r)
            else:
                roots.append(r)

        # مرتب‌سازی ایمن برای هر سطح (در صورت نیاز)
        for n in nodes.values():
            n['children'].sort(key=lambda x: (x['id']))
        roots.sort(key=lambda x: (x['id']))

        return roots


class Category(models.Model):
    parent = models.ForeignKey('self', default=None, null=True, blank=True, on_delete=models.CASCADE,
                               related_name='children', verbose_name=_('والد'))
    title = models.CharField(max_length=50, verbose_name=_('عنوان'))
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, verbose_name=_('اسلاگ'))
    icon = models.ImageField(upload_to='category/icon/', null=True, blank=True, verbose_name='آیکون')
    is_payable = models.BooleanField(default=False, verbose_name=_('پولی'))
    is_special = models.BooleanField(default=False, verbose_name=_('ویژه'))
    price = models.PositiveBigIntegerField(default=0, verbose_name=_('قیمت'))

    objects = CategoryManager()

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')
        ordering = ['id']

    # def get_category_fields(self):
    #     from . import CategoryField
    #
    #     res = CategoryField.objects.filter(category=self)
    #
    #     return res

    def get_category_fields(self):
        from . import CategoryField
        cats = [self]
        p = self.parent
        while p:
            cats.append(p)
            p = p.parent
        return CategoryField.objects.filter(category__in=cats).order_by('id')

    # def get_absolute_url(self):
    #     # آدرس کامل با احتساب والدها (مثلاً 'vehicles/car')
    #     path = self.slug
    #     parent = self.parent
    #     while parent:
    #         path = f"{parent.slug}/{path}"
    #         parent = parent.parent
    #     return reverse('ad:hierarchical-landing', kwargs={'path': f"{path}"})
