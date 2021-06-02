from kolibri.dist.django.conf.urls import url

from .views import zim_article
from .views import zim_index

urlpatterns = [
    url(r"^zimcontent/(?P<zim_filename>[^/]+.zim)$", zim_index, name="zim_index"),
    url(
        r"^zimcontent/(?P<zim_filename>[^/]+.zim)/(?P<zim_article_path>.+)$",
        zim_article,
        name="zim_article",
    ),
]
