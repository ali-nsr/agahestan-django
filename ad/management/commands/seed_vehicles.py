import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from ad.models import Category, CategoryField


class Command(BaseCommand):
    help = 'بارگذاری امن دسته‌بندی و فیلدهای وسایل نقلیه'

    def add_arguments(self, parser):
        parser.add_argument('--dir', default='fixtures')

    @transaction.atomic
    def handle(self, *args, **opts):
        fixtures_dir = Path(opts['dir'])
        cat_files = [
            fixtures_dir / 'vehicle_categories.json',
            fixtures_dir / 'vehicle_categories_extra.json',
        ]
        field_files = [
            fixtures_dir / 'vehicle_fields.json',
            fixtures_dir / 'vehicle_fields_extra.json',
        ]

        # جمع‌آوری از همه فایل‌ها
        all_cats = {}
        for f in cat_files:
            if f.exists():
                for c in json.loads(f.read_text(encoding='utf-8')):
                    all_cats[c['pk']] = c

        all_fields = {}
        for f in field_files:
            if f.exists():
                for c in json.loads(f.read_text(encoding='utf-8')):
                    all_fields[c['pk']] = c

        # ─── topological sort والدها ───
        remaining = dict(all_cats)
        created_count = 0
        while remaining:
            progress = False
            for pk, data in list(remaining.items()):
                parent_pk = data['fields']['parent']
                if parent_pk is None or Category.objects.filter(pk=parent_pk).exists():
                    fields = dict(data['fields'])
                    fields.pop('parent', None)
                    parent = Category.objects.filter(pk=parent_pk).first() if parent_pk else None
                    Category.objects.update_or_create(
                        pk=pk, defaults={**fields, 'parent': parent}
                    )
                    del remaining[pk]
                    created_count += 1
                    progress = True
            if not progress:
                orphans = list(remaining.keys())
                raise Exception(f'والدهای گم‌شده برای: {orphans}')

        # ─── فیلدها ───
        field_count = 0
        for pk, data in all_fields.items():
            f = data['fields']
            CategoryField.objects.update_or_create(
                pk=pk,
                defaults={
                    'category_id': f['category'],
                    'key': f['key'],
                    'label': f['label'],
                    'type': f['type'],
                    'is_required': f['is_required'],
                    'data': f['data'],
                },
            )
            field_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'✓ {created_count} category, {field_count} field'
        ))