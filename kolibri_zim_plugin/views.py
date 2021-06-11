from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import time

import libzim.reader
from kolibri.core.content.utils.paths import get_content_storage_file_path
from kolibri.dist.django.core.urlresolvers import get_resolver
from kolibri.dist.django.http import HttpResponse
from kolibri.dist.django.http import HttpResponseBadRequest
from kolibri.dist.django.http import HttpResponseNotFound
from kolibri.dist.django.http import HttpResponseNotModified
from kolibri.dist.django.http import HttpResponsePermanentRedirect
from kolibri.dist.django.http import HttpResponseServerError
from kolibri.dist.django.http import JsonResponse
from kolibri.dist.django.utils.cache import patch_response_headers
from kolibri.dist.django.utils.http import http_date
from kolibri.dist.django.views import View


# This provides an API similar to the zipfile view in Kolibri core's zip_wsgi.
# In the future, we should replace this with a change adding Zim file support
# in the same place: <https://github.com/endlessm/kolibri/pull/3>.
#
# We are avoiding Django REST Framework here in case this code needs to be
# moved to the alternative zip_wsgi server.


YEAR_IN_SECONDS = 60 * 60 * 24 * 365


class ZimFileNotFoundError(Exception):
    pass


class ZimFileReadError(Exception):
    pass


class _ZimFileViewMixin(View):
    def dispatch(self, request, *args, **kwargs):
        zim_filename = kwargs["zim_filename"]

        try:
            self.zim_file = self.__get_zim_file(zim_filename)
        except ZimFileNotFoundError:
            return HttpResponseNotFound("Zim file does not exist")
        except ZimFileReadError:
            return HttpResponseServerError("Error reading Zim file")

        return super().dispatch(request, *args, **kwargs)

    def __get_zim_file(self, zim_filename):
        zim_file_path = get_content_storage_file_path(zim_filename)

        if not os.path.exists(zim_file_path):
            raise ZimFileNotFoundError()

        # Raises RuntimeError
        try:
            zim_file = libzim.reader.File(zim_file_path)
        except RuntimeError as error:
            raise ZimFileReadError(str(error))

        return zim_file


class _ImmutableViewMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.method != "GET":
            return super().dispatch(request, *args, **kwargs)
        elif request.META.get("HTTP_IF_MODIFIED_SINCE"):
            return HttpResponseNotModified()
        else:
            response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 200:
            patch_response_headers(response, cache_timeout=YEAR_IN_SECONDS)
        return response


class ZimIndexView(_ImmutableViewMixin, _ZimFileViewMixin, View):
    http_method_names = (
        "get",
        "options",
    )

    def get(self, request, zim_filename):
        if request.META.get("HTTP_IF_MODIFIED_SINCE"):
            return HttpResponseNotModified()

        return _zim_redirect_response(
            request, zim_filename, self.zim_file.main_page_url
        )


class ZimArticleView(_ImmutableViewMixin, _ZimFileViewMixin, View):
    http_method_names = (
        "get",
        "options",
    )

    def get(self, request, zim_filename, zim_article_path):
        try:
            zim_article = self.zim_file.get_article(zim_article_path)
        except KeyError:
            return HttpResponseNotFound("Article does not exist")

        if zim_article.is_redirect:
            redirect_article = zim_article.get_redirect_article()
            return _zim_redirect_response(
                request, zim_filename, redirect_article.longurl
            )

        # TODO: It would be better to use StreamingHttpResponse or FileResponse
        #       here. We are copying the entire file for now for simplicity since
        #       we may use a different Zim implementation in the near future.

        response = HttpResponse()
        response["Content-Length"] = zim_article.content.nbytes
        # ensure the browser knows not to try byte-range requests, as we don't support them here
        response["Accept-Ranges"] = "none"
        response["Last-Modified"] = http_date(time.time())
        response["Content-Type"] = zim_article.mimetype
        response.write(zim_article.content.tobytes())
        return response


class ZimSearchView(_ZimFileViewMixin, View):
    MAX_RESULTS_MAXIMUM = 100

    def get(self, request, zim_filename):
        query = request.GET.get("query")
        suggest = "suggest" in request.GET
        start = request.GET.get("start", 0)
        max_results = request.GET.get("max_results", 30)

        if not query:
            return HttpResponseBadRequest('Missing "query"')

        try:
            start = int(start)
        except ValueError:
            return HttpResponseBadRequest('Invalid "start"')

        try:
            max_results = int(max_results)
        except ValueError:
            return HttpResponseBadRequest('Invalid "max_results"')

        if max_results < 0 or max_results > self.MAX_RESULTS_MAXIMUM:
            return HttpResponseBadRequest('Invalid "max_results"')

        if suggest:
            count = self.zim_file.get_suggestions_results_count(query)
            search = self.zim_file.suggest(query, start=start, end=start + max_results)
        else:
            count = self.zim_file.get_search_results_count(query)
            search = self.zim_file.search(query, start=start, end=start + max_results)

        articles = list(self.__article_metadata(path) for path in search)

        return JsonResponse({"articles": articles, "count": count})

    def __article_metadata(self, zim_article_path):
        zim_article = self.zim_file.get_article(zim_article_path)
        return {"title": zim_article.title, "path": zim_article.longurl}


def _zim_redirect_response(request, zim_filename, zim_article_path):
    # FIXME: I don't know why I need to torment the resolver like this instead
    #        instead of using django.urls.reverse, but something is trying to
    #        add a language prefix incorrectly and causing an error.
    resolver = get_resolver(None)
    redirect_url = resolver.reverse(
        "zim_article", zim_filename=zim_filename, zim_article_path=zim_article_path
    )
    return HttpResponsePermanentRedirect(request.build_absolute_uri("/" + redirect_url))
