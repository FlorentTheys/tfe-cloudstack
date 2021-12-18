import json
import requests

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from lxml import etree

from .models import APIRequest, Category, CloudstackEventLog, CloudstackEventServer, CloudstackEventTrigger, CloudstackEventTriggerCondition, CloudstackEventTriggerActionParameter, CloudstackUser, Command, Parameter


def index(request):
    return render(request, 'home.html')


def api(request):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'api_request.html')


def api_history(request, offset=0, limit=10):
    if not request.user.is_authenticated:
        raise Http404
    csu_ids = [csu.id for csu in request.user.cloudstack_user_ids.all()]
    base_query = APIRequest.objects.filter(cloudstack_user_id__in=csu_ids)
    next_offset = offset + limit
    api_request_list = base_query.order_by('-created_at')[offset:next_offset]
    total = base_query.count()
    return render(request, 'api_history.html', {
        'api_request_list': api_request_list,
        'offset': offset,
        'limit': limit,
        'first': min(offset + 1, total),
        'last': min(next_offset, total),
        'prev_offset': max(0, offset - limit) if offset > 0 else False,
        'next_offset': next_offset if next_offset < total else False,
        'total': total,
    })


def cs_event_history(request, offset=0, limit=10):
    if not request.user.is_authenticated:
        raise Http404
    cs_event_server_ids = [csu.id for csu in request.user.cloudstack_event_server_ids.all()]
    base_query = CloudstackEventLog.objects.filter(cloudstack_event_server_id__in=cs_event_server_ids)
    next_offset = offset + limit
    event_log_list = base_query.order_by('-id')[offset:next_offset]
    total = base_query.count()
    return render(request, 'cs_event_history.html', {
        'event_log_list': event_log_list,
        'offset': offset,
        'limit': limit,
        'first': min(offset + 1, total),
        'last': min(next_offset, total),
        'prev_offset': max(0, offset - limit) if offset > 0 else False,
        'next_offset': next_offset if next_offset < total else False,
        'total': total,
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


def cs_event_server(request):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'cs_event_server.html')


def cs_event_server_add(request):
    if not request.user.is_authenticated:
        raise Http404
    host = request.POST.get('host', '')
    exchange = request.POST.get('exchange', '')
    if host and exchange:
        CloudstackEventServer.objects.create(user_id=request.user, host=host, exchange=exchange)
        return redirect('/cs_event_server')
    return render(request, 'cs_event_server_add.html', {
        'host': host or 'localhost',
        'exchange': exchange or 'cloudstack-events',
    })


def cs_event_server_delete(request, cs_event_server_id):
    if not request.user.is_authenticated:
        raise Http404
    cs_event_server = CloudstackEventServer.objects.get(user_id=request.user, id=cs_event_server_id)
    cs_event_server.delete()
    return redirect('/cs_event_server')


def fetch_category_list_view(request):
    if not request.user.is_authenticated:
        raise Http404
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
    cs_user_id = form_data['cs_user_id']
    command_id = form_data['command_id']
    parameter_list = form_data['parameter_list']
    cs_user = CloudstackUser.objects.get(user_id=request.user, id=cs_user_id)
    return JsonResponse(cs_user.make_api_request(command_id=command_id, parameter_list=parameter_list))


# event triggers
def cs_event_trigger_list(request, offset=0, limit=10):
    if not request.user.is_authenticated:
        raise Http404
    csu_ids = [csu.id for csu in request.user.cloudstack_user_ids.all()]
    cs_event_server_ids = [csu.id for csu in request.user.cloudstack_event_server_ids.all()]
    base_query = CloudstackEventTrigger.objects.filter(cloudstack_event_server_id__in=cs_event_server_ids, cloudstack_user_id__in=csu_ids)
    next_offset = offset + limit
    event_trigger_list = base_query.order_by('-id')[offset:next_offset]
    total = base_query.count()
    return render(request, 'cs_event_trigger_list.html', {
        'event_trigger_list': event_trigger_list,
        'offset': offset,
        'limit': limit,
        'first': min(offset + 1, total),
        'last': min(next_offset, total),
        'prev_offset': max(0, offset - limit) if offset > 0 else False,
        'next_offset': next_offset if next_offset < total else False,
        'total': total,
    })


def cs_event_trigger_add(request, event_trigger_id=0):
    if not request.user.is_authenticated:
        raise Http404
    return render(request, 'cs_event_trigger_add.html', {
        'event_trigger_id': event_trigger_id,
    })


def cs_event_trigger_delete(request, cs_event_trigger_id):
    if not request.user.is_authenticated:
        raise Http404
    cs_event_trigger = CloudstackEventTrigger.objects.get(pk=cs_event_trigger_id)
    cs_event_trigger.delete()
    return redirect('/cs_event_trigger_list')


def get_data_for_trigger(request, cs_event_trigger_id=0):
    res = {}
    res['event_servers'] = [
        {
            'id': event_server.id,
            'name': str(event_server),
        }
        for event_server in request.user.cloudstack_event_server_ids.all()
    ]
    res['cs_users'] = [
        {
            'id': event_server.id,
            'name': str(event_server),
        }
        for event_server in request.user.cloudstack_user_ids.all()
    ]
    res['categoryList'] = [
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
                            'command': '',
                            'value': '',
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
    ]
    if cs_event_trigger_id:
        cs_event_trigger = CloudstackEventTrigger.objects.get(pk=cs_event_trigger_id)
        res['formData'] = {
            'cloudstack_user_id': cs_event_trigger.cloudstack_user_id.id,
            'command_id': cs_event_trigger.command_id.id,
            'conditions': [
                {
                    'data_key': condition.data_key,
                    'operator': condition.operator,
                    'value': condition.value,
                }
                for condition in cs_event_trigger.cloudstack_event_trigger_condition_ids.all()
            ],
            'parameterList': [
                {
                    'id': parameter.parameter_id.id,
                    'operator': parameter.operator,
                    'value': parameter.value,
                }
                for parameter in cs_event_trigger.cloudstack_event_trigger_action_parameter_ids.all()
            ],
            'event_server_id': cs_event_trigger.cloudstack_event_server_id.id,
        }
    return JsonResponse(res)


def trigger_create(request):
    body = json.loads(request.body)
    form_data = body['form_data']
    event_trigger_id = form_data.get('event_trigger_id')
    event_server_id = form_data['event_server_id']
    cloudstack_user_id = form_data['cloudstack_user_id']
    conditions = form_data['conditions']
    parameter_list = form_data['parameter_list']
    command_id = form_data['command_id']
    if event_trigger_id:
        event_trigger = CloudstackEventTrigger.objects.get(pk=event_trigger_id)
        event_trigger.cloudstack_event_server_id = CloudstackEventServer.objects.get(pk=event_server_id)
        event_trigger.cloudstack_user_id = CloudstackUser.objects.get(pk=cloudstack_user_id)
        event_trigger.cloudstack_event_trigger_condition_ids.all().delete()
        event_trigger.cloudstack_event_trigger_action_parameter_ids.all().delete()
        event_trigger.save()
    else:
        event_trigger = CloudstackEventTrigger.objects.create(
            cloudstack_event_server_id=CloudstackEventServer.objects.get(pk=event_server_id),
            cloudstack_user_id=CloudstackUser.objects.get(pk=cloudstack_user_id),
            command_id=Command.objects.get(pk=command_id),
        )
    for condition in conditions:
        data_key = condition.get('data_key')
        operator = condition.get('operator')
        value = condition.get('value')
        if data_key and operator:
            CloudstackEventTriggerCondition.objects.create(
                cs_event_trigger_id=event_trigger,
                data_key=data_key,
                operator=operator,
                value=value,
            )
    for parameter in parameter_list:
        parameter_id = parameter.get('parameter_id')
        operator = parameter.get('operator')
        value = parameter.get('value')
        if parameter_id and operator:
            CloudstackEventTriggerActionParameter.objects.create(
                cs_event_trigger_id=event_trigger,
                parameter_id=Parameter.objects.get(pk=parameter_id),
                operator=operator,
                value=value,
            )
    return JsonResponse({
        'id': event_trigger.id,
    })
