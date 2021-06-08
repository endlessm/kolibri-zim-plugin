from kolibri.dist.django.conf.urls import url

from .views import ZimArticleView
from .views import ZimIndexView

urlpatterns = [
    url(
        r"^zim/content/(?P<zim_filename>[^/]+.zim)$",
        ZimIndexView.as_view(),
        name="zim_index",
    ),
    url(
        r"^zim/content/(?P<zim_filename>[^/]+.zim)/(?P<zim_article_path>.+)$",
        ZimArticleView.as_view(),
        name="zim_article",
    ),
]
