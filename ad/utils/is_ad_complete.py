from ..models import Ad

def is_ad_complete(ad: Ad):
    has_main_fields = bool(ad.title and ad.description and ad.price)
    has_attributes = ad.ad_attributes.exists()
    has_images = ad.gallery.exists()
    return has_main_fields and has_attributes and has_images