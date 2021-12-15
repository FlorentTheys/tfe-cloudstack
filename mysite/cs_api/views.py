import json

from django.http import JsonResponse
from django.shortcuts import render
from .models import APIRequest, APIRequestParameterValue, Category, Command, Parameter


def index(request):
    return render(request, 'home.html', {
    })


def api(request):
    return render(request, 'api_request.html', {
    })


def get_category_map(request):
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
