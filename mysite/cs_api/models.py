import base64
import hashlib
import hmac
import json
import requests
import urllib
import urllib.parse
import urllib.request

from lxml import etree
from django.db import models

# Create your models here.

from django.contrib.auth.models import User


class CloudstackUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloudstack_user_ids')
    url = models.CharField(max_length=300)
    api_key = models.CharField(max_length=86)
    secret_key = models.CharField(max_length=86)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Command(models.Model):
    doc_url = models.CharField(max_length=300)
    name = models.CharField(max_length=100)
    category_id = models.ForeignKey('Category', on_delete=models.RESTRICT, related_name='command_ids')

    def __str__(self):
        return self.name

    def update_from_doc(self):
        url = "https://cloudstack.apache.org/api/apidocs-4.11/"
        req_get = requests.get(f'{url}{self.doc_url}')
        root_node = etree.HTML(req_get.text)
        name_node = root_node.xpath('.//h1')[0]
        self.name = name_node.text
        parameters_node = root_node.xpath('.//table[@class="apitable"]')[0]
        for parameter_node in parameters_node.xpath('.//tr[not(contains(@class, "hed"))]'):
            parameter_item_node = parameter_node.xpath('.//td')
            name = ''.join(parameter_item_node[0].itertext())
            description = ''.join(parameter_item_node[1].itertext())
            required = ''.join(parameter_item_node[2].itertext()) == 'true'
            parameter, was_created = Parameter.objects.get_or_create(
                name=name,
                command_id=self,
                defaults={
                    'description': description,
                    'required': required,
                },
            )
            parameter.description = description
            parameter.required = required


class Parameter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    required = models.BooleanField()
    command_id = models.ForeignKey('Command', on_delete=models.RESTRICT, related_name='parameter_ids')

    def __str__(self):
        return self.name


class APIRequest(models.Model):
    command_id = models.ForeignKey('Command', on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.command_id.name}?{'&'.join([str(v) for v in self.value_ids.all()])}"

    def make_api_request(self, url, api_key, secret_key):

        print('url', url)

        url_parts = urllib.parse.urlparse(url)

        print('url_parts', url_parts)

        baseurl = f'{url_parts.scheme}://{url_parts.netloc}{url_parts.path}?'
        print('------------', [
            {
                'name': api_request_parameter_value.parameter_id.name,
                'value': api_request_parameter_value.value,
            }
            for api_request_parameter_value in self.value_ids.all()
        ])
        my_request = {
            api_request_parameter_value.parameter_id.name: api_request_parameter_value.value
            for api_request_parameter_value in self.value_ids.all()
        }

        my_request['command'] = self.command_id.name
        my_request['response'] = 'json'

        my_request['apikey'] = api_key

        my_request_str = '&'.join(['='.join([k, urllib.parse.quote(my_request[k])]) for k in my_request.keys()])
        print('my_request_str         ', my_request_str)

        sig_str = '&'.join(['='.join([k.lower(), urllib.parse.quote(my_request[k].lower().replace('+', '%20'))])for k in sorted(my_request.keys())])
        print('sig_str         ', sig_str)
        sig = hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1)
        print('sig         ', sig)
        sig = hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1).digest()
        print('sig         ', sig)
        sig = base64.encodebytes(hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1).digest())
        print('sig         ', sig)
        sig = base64.encodebytes(hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1).digest()).strip()
        print('sig         ', sig)
        diget = hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1).digest()
        # sig = base64.encodebytes(diget).strip()
        sig = urllib.parse.quote(base64.encodebytes(diget).strip().decode())
        print('sig         ', sig)

        req_str = baseurl + my_request_str + '&signature=' + sig
        print('req_str         ', req_str)

        my_request['signature'] = sig

        # data = urllib.urlencode(my_request).encode()

        # print('my_request', my_request)
        # req =  urllib.request.Request(baseurl, data=bytes(json.dumps(my_request), encoding="utf-8")) # this will make the method "POST"
        req = urllib.request.Request(req_str)
        try:
            res = urllib.request.urlopen(req)
        except Exception as e:
            error_message = e.read().decode("utf-8")
            print('error: ', error_message)
            return {'error': error_message}
        else:
            # TODO save result?
            res_json = json.loads(res.read())
            print('res: ', res_json)
            return res_json
        # res=urllib.request.urlopen(req_str)


class APIRequestParameterValue(models.Model):
    request_id = models.ForeignKey('APIRequest', on_delete=models.RESTRICT, related_name='value_ids')
    parameter_id = models.ForeignKey('Parameter', on_delete=models.RESTRICT)
    value = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.parameter_id.name}={self.value}"
