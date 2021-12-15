import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from .models import APIRequest, APIRequestParameterValue, Category, Command, Parameter


def index(request):
    return render(request, 'home.html', {
    })


def api(request):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'api_request.html', {
    })


def signup_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    is_already_taken = False
    if username and password:
        users = User.objects.filter(username=username)
        if users.count() > 0:
            is_already_taken = True
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('/')
    return render(request, 'signup.html', {
        'is_already_taken': is_already_taken,
        'username': username,
        'password': password,
    })


def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
    return render(request, 'login.html', {
        'username': username,
        'password': password,
    })


def logout_view(request):
    logout(request)
    return redirect('/')


def get_category_map(request):
    if not request.user.is_authenticated:
        raise Http404
    return JsonResponse({
        'categoryList': [
            {
                'commandList': [
                    {
                        'id': command.id,
                        'name': command.name,
                        'parameterList': [
                            {
                                'description': parameter.description,
                                'id': parameter.id,
                                'name': parameter.name,
                                'required': parameter.required,
                            }
                            for parameter in command.parameter_ids.all()
                        ],
                    }
                    for command in category.command_ids.all()
                ],
                'id': category.id,
                'name': category.name,
            }
            for category in Category.objects.all()
        ],
    })


def receive_api_request(request):
    if not request.user.is_authenticated:
        raise Http404
    body = json.loads(request.body)
    form_data = body['form_data']
    api_key = form_data['api_key']
    command_id = form_data['command_id']
    parameter_list = form_data['parameter_list']
    secret_key = form_data['secret_key']
    url = form_data['url']
    print(command_id, parameter_list, url, api_key, secret_key)

    # TODO add date, ip, ...
    # TODO also save url?
    api_request = APIRequest(command_id=Command.objects.get(pk=int(command_id)))
    api_request.save()
    for parameter in parameter_list:
        if parameter['value'] == '':
            continue
        api_request_parameter_value = APIRequestParameterValue(request_id=api_request, parameter_id=Parameter.objects.get(pk=int(parameter['id'])), value=parameter['value'])
        api_request_parameter_value.save()

    res = api_request.make_api_request(url=url, api_key=api_key, secret_key=secret_key)
    return JsonResponse(res)
