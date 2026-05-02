from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include(("apps.core.urls", "core"), namespace="core")),
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("calculator/", include(("apps.calculator.urls", "calculator"), namespace="calculator")),
    path("documents/", include(("apps.documents.urls", "documents"), namespace="documents")),
    path("calendar/", include(("apps.calendar_tax.urls", "calendar_tax"), namespace="calendar_tax")),
    path("chat/", include(("apps.chat.urls", "chat"), namespace="chat")),
    path("forum/", include(("apps.forum.urls", "forum"), namespace="forum")),
    path("knowledge/", include(("apps.knowledge.urls", "knowledge"), namespace="knowledge")),
    path("admin-custom/", include(("apps.admin_panel.urls", "admin_panel"), namespace="admin_panel")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
