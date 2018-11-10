# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(["POST"])
def user_login(request):
    response = {}
    try:
        code = request.POST["code"]
        response['msg'] = "username or password error"
        response['error_num'] = 1
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
        response = JsonResponse(response)
    return response