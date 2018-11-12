# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from codex.baseError import *

@require_http_methods(["POST"])
def admin_login(request):
    response = {}
    try:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            raise ValidateError("Login failed!")
        response['msg'] = "Login success!"
        response['error'] = 0
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    return response

@require_http_methods(["POST"])
def admin_logout(request):
    response = {}
    try:
        if not request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            logout(request)
            response['msg'] = "Logout success!"
            response['error'] = 0
            response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    return response