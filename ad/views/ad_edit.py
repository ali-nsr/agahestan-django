from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..models import Ad, Category, Gallery
from ..forms import (
    AdForm, build_category_form, save_category_attributes,
    validate_image, MAX_IMAGES,
)
from ..views import generate_thumbnail  # یا از همون فایل import کن

@login_required
def ad_edit(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid, user=request.user)

    # if ad.status not in (Ad.Status.DRAFT, Ad.Status.REJECTED):
    #     messages.error(request, 'این آگهی قابل ویرایش نیست.')
    #     return redirect('accounts:dashboard')

    category = ad.category
    existing_images = list(ad.gallery.order_by('-is_main', 'id'))

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad,
                      user=request.user, fixed_category=category)
        cat_form = build_category_form(category, data=request.POST)

        new_images = request.FILES.getlist('images')
        removed_ids = [int(x) for x in request.POST.getlist('removed_images') if x.isdigit()]
        main_ref = request.POST.get('main_image_ref', '')

        image_errors = []
        for img in new_images:
            try:
                validate_image(img)
            except ValidationError as e:
                image_errors.extend(e.messages)

        remaining = len([i for i in existing_images if i.id not in removed_ids])
        total = remaining + len(new_images)

        if total == 0:
            image_errors.append('حداقل یک تصویر باید داشته باشید.')

        if form.is_valid() and cat_form.is_valid() and not image_errors:
            with transaction.atomic():
                ad = form.save()
                save_category_attributes(ad, cat_form.cleaned_data, category)

                if removed_ids:
                    Gallery.objects.filter(ad=ad, id__in=removed_ids).delete()

                created_new = []
                for img in new_images:
                    created_new.append(Gallery.objects.create(ad=ad, image=img, is_main=False))

                ad.gallery.update(is_main=False)
                main_gallery = None

                if main_ref.startswith('existing:'):
                    try:
                        gid = int(main_ref.split(':', 1)[1])
                        main_gallery = ad.gallery.filter(id=gid).first()
                    except (ValueError, IndexError):
                        pass
                elif main_ref.startswith('new:'):
                    try:
                        idx = int(main_ref.split(':', 1)[1])
                        if 0 <= idx < len(created_new):
                            main_gallery = created_new[idx]
                    except (ValueError, IndexError):
                        pass

                if not main_gallery:
                    main_gallery = ad.gallery.first()

                if main_gallery:
                    main_gallery.is_main = True
                    main_gallery.save(update_fields=['is_main'])
                    if ad.thumbnail:
                        ad.thumbnail.delete(save=False)
                    generate_thumbnail(ad, main_gallery.image)

                ad.status = Ad.Status.REVIEW
                ad.save(update_fields=['status'])

            messages.success(request, 'آگهی با موفقیت ویرایش شد.')
            return redirect('accounts:dashboard')

        for err in image_errors:
            messages.error(request, err)

    else:
        form = AdForm(instance=ad, user=request.user, fixed_category=category)
        initial = _get_category_initial(ad, category)
        cat_form = build_category_form(category, initial=initial)

    return render(request, 'ad/ad_edit.html', {
        'ad': ad,
        'form': form,
        'cat_form': cat_form,
        'category': category,
        'existing_images': existing_images,
    })


def _get_category_initial(ad, category):
    """مقدارهای اولیه از AdAttribute."""
    initial = {}
    attrs = {a.category_field_id: a.value for a in ad.ad_attributes.all()}
    for cf in category.get_category_fields():
        if cf.pk not in attrs:
            continue
        raw = attrs[cf.pk]
        field_name = f'cf_{cf.pk}'
        if cf.type == cf.FieldType.MULTI_CHOICE:
            initial[field_name] = raw.split(',') if raw else []
        elif cf.type == cf.FieldType.BOOLEAN:
            initial[field_name] = raw in ('True', 'true', '1', 'yes')
        else:
            initial[field_name] = raw
    return initial

@login_required
@require_POST
def ad_delete(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid, user=request.user)
    ad.delete()
    return JsonResponse({'ok': True})