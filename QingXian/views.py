# -*- coding: utf-8 -*-
#
from django.views.generic import View
from QingXian.settings import *

from django.http import HttpResponse, Http404
import mimetypes
import os


__author__ = "Epsirom"


class StaticFileView(View):

    def get_file(self, fpath):
        if os.path.isfile(fpath):
            return open(fpath, 'rb').read()
        else:
            return None

    def do_dispatch(self, *args, **kwargs):
        print("into dispatch", self.request.path)
        rpath = self.request.path.replace('..', '.').strip('/')
        if '__' in rpath:
            raise Http404('Could not access private static file: ' + self.request.path)
        content = self.get_file(rpath)
        if content is not None:
            return HttpResponse(content, content_type=mimetypes.guess_type(rpath)[0])
