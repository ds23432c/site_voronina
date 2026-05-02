from datetime import datetime

from django.conf import settings


def site_meta(request):
    """Expose shared branding values to templates."""
    return {
        "site_name": getattr(settings, "SITE_NAME", "БухПомощник"),
        "current_year": datetime.now().year,
    }