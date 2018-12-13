from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import os


def get_file(fpath):
    if os.path.isfile(fpath):
        return open(fpath, 'rb').read()
    else:
        return None


# 显示图片
@require_http_methods(["GET"])
def show_image(request):
    pic_addr = str(request.path).replace("/showimage/", "/")
    content = get_file(pic_addr)
    if content is not None:
        return HttpResponse(content, content_type="image/png")