import json
import requests

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from lxml import etree

from .models import APIRequest, APIRequestParameterValue, Category, CloudstackUser, Command, Parameter


def index(request):
    return render(request, 'home.html')


def api(request):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'api_request.html')


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


def cs_user(request):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'cs_user.html')


def cs_user_add(request):
    if not request.user.is_authenticated:
        raise Http404
    url = request.POST.get('url', '')
    api_key = request.POST.get('api_key', '')
    secret_key = request.POST.get('secret_key', '')
    if url and api_key and secret_key:
        CloudstackUser.objects.create(user_id=request.user, url=url, api_key=api_key, secret_key=secret_key)
        return redirect('/cs_user')
    return render(request, 'cs_user_add.html', {
        'url': url,
        'api_key': api_key,
        'secret_key': secret_key,
    })


def cs_user_delete(request, cs_user_id):
    if not request.user.is_authenticated:
        raise Http404
    cs_user = CloudstackUser.objects.get(user_id=request.user, id=cs_user_id)
    cs_user.delete()
    return redirect('/cs_user')


def fetch_category_list_view(request):
    url = "https://cloudstack.apache.org/api/apidocs-4.11/"
    req_get = requests.get(url)
    root_node = etree.HTML(req_get.text)
    for category_node in root_node.xpath('.//div[@class="apismallbullet_box"]'):
        category_title_node = category_node.xpath('.//h5')[0]
        category, was_category_created = Category.objects.get_or_create(name=category_title_node.text)
        for command_node in category_node.xpath('.//li/a'):
            command, was_command_created = Command.objects.get_or_create(
                doc_url=command_node.get('href'),
                defaults={
                    'name': command_node.text,
                    'category_id': category,
                },
            )
            command.update_from_doc()
    return redirect('/api')


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
        'cloudstackUsers': [
            {
                'id': cs_user.id,
                'url': cs_user.url,
                'apiKey': cs_user.api_key,
                'secretKey': cs_user.secret_key,
            }
            for cs_user in request.user.cloudstack_user_ids.all()
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
