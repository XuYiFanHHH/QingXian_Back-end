# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(["POST"])
def user_login(request):
    response = {}
    try:
        code = request.POST["code"]
        response['msg'] = "login success"
        response['error_num'] = 0
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
        response = JsonResponse(response)
    finally:
        return response