from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import time

import libzim.reader
from kolibri.core.content.utils.paths import get_content_storage_file_path
from kolibri.dist.django.core.urlresolvers import get_resolver
from kolibri.dist.django.http import Http404
from kolibri.dist.django.http import HttpResponse
from kolibri.dist.django.http import HttpResponseNotModified
from kolibri.dist.django.http import HttpResponsePermanentRedirect
from kolibri.dist.django.http import HttpResponseServerError
from kolibri.dist.django.utils.cache import patch_response_headers
from kolibri.dist.django.utils.http import http_date


# This provides an API similar to the zipfile view in Kolibri core's zip_wsgi.
# In the future, we should replace this with a change adding Zim file support
# in the same place: <https://github.com/endlessm/kolibri/pull/3>.


YEAR_IN_SECONDS = 60 * 60 * 24 * 365


def zim_index(request, zim_filename):
    if request.META.get("HTTP_IF_MODIFIED_SINCE"):
        return HttpResponseNotModified()

    try:
        zim_file = _get_zim_file(zim_filename)
    except RuntimeError:
        return HttpResponseServerError("Error reading Zim file")

    return _zim_redirect_response(request, zim_filename, zim_file.main_page_url)


def zim_article(request, zim_filename, zim_article_path):
    if request.META.get("HTTP_IF_MODIFIED_SINCE"):
        return HttpResponseNotModified()

    try:
        zim_file = _get_zim_file(zim_filename)
    except RuntimeError:
        raise HttpResponseServerError("Error reading Zim file")

    try:
        zim_article = zim_file.get_article(zim_article_path)
    except KeyError:
        raise Http404("Article does not exist")

    if zim_article.is_redirect:
        redirect_article = zim_article.get_redirect_article()
        return _zim_redirect_response(request, zim_filename, redirect_article.longurl)

    return _zim_article_response(zim_article)


def _get_zim_file(zim_filename):
    zim_file_path = get_content_storage_file_path(zim_filename)

    if not os.path.exists(zim_file_path):
        raise Http404("Zim file does not exist")

    # Raises RuntimeError
    zim_file = libzim.reader.File(zim_file_path)

    return zim_file


def _zim_redirect_response(request, zim_filename, zim_article_path):
    # FIXME: I don't know why I need to torment the resolver like this instead
    #        instead of using django.urls.reverse, but something is trying to
    #        add a language prefix incorrectly and causing an error.
    resolver = get_resolver(None)
    redirect_url = resolver.reverse(
        "zim_article", zim_filename=zim_filename, zim_article_path=zim_article_path
    )
    return HttpResponsePermanentRedirect(request.build_absolute_uri("/" + redirect_url))


def _zim_article_response(zim_article):
    # TODO: It would be better to use StreamingHttpResponse or FileResponse
    #       here. We are copying the entire file for now for simplicity since
    #       we may use a different Zim implementation in the near future.

    response = HttpResponse()
    response.write(zim_article.content.tobytes())
    response["Content-Length"] = zim_article.content.nbytes
    # ensure the browser knows not to try byte-range requests, as we don't support them here
    response["Accept-Ranges"] = "none"
    response["Last-Modified"] = http_date(time.time())
    patch_response_headers(response, cache_timeout=YEAR_IN_SECONDS)

    return response
