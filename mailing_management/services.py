from django.core.cache import cache

from config.settings import CACHE_ENABLED
from mailing_management.models import Mailing


def get_mailings_from_cache():
    """Получает список продуктов из кеша, при его отсутствии получает из БД."""
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailings_list"
    mailings = cache.get(key)
    if mailings is not None:
        return mailings
    mailings = Mailing.objects.all()
    cache.set(key, mailings, 60 * 15)
    return mailings
