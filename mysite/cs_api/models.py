import base64
import hashlib
import hmac
import json
import pika
import requests
import threading
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

    def make_api_request(self, command_id, parameter_list):
        # TODO add date, ip, ...
        # TODO also save url?
        api_request = APIRequest(cloudstack_user_id=self, command_id=Command.objects.get(pk=int(command_id)))
        api_request.save()
        for parameter in parameter_list:
            if parameter['value'] == '':
                continue
            api_request_parameter_value = APIRequestParameterValue(request_id=api_request, parameter_id=Parameter.objects.get(pk=int(parameter['id'])), value=parameter['value'])
            api_request_parameter_value.save()
        try:
            res = api_request.make_api_request()
        except Exception as e:
            res = {'error': str(e)}
        api_request.result = res
        api_request.save()
        return res


class CloudstackEventServer(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cloudstack_event_server_ids')
    host = models.CharField(max_length=300)
    exchange = models.CharField(max_length=300, default='cloudstack-events')

    def listen(self):

        def on_message_callback(ch, method, properties, body):
            event_log = CloudstackEventLog.objects.create(cloudstack_event_server_id=self, routing_key=method.routing_key, body=body.decode("utf-8"))
            print(f'message: {event_log}')

        def start():
            print(f"Starting to listen for events on {self}")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
            channel = connection.channel()
            cs_exchange = 'cloudstack-events'
            channel.exchange_declare(exchange=cs_exchange, exchange_type='topic', durable=True)

            result = channel.queue_declare(f'listener{self.id}', durable=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange=cs_exchange, queue=queue_name, routing_key='#')

            channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=True)

            channel.start_consuming()

        t = threading.Thread(target=start)
        t.start()

    def __str__(self):
        return f'{self.id} / {self.host} / {self.exchange}'


class CloudstackEventLog(models.Model):
    cloudstack_event_server_id = models.ForeignKey('CloudstackEventServer', on_delete=models.CASCADE, related_name='cloudstack_event_log_ids')
    routing_key = models.CharField(max_length=300)
    body = models.TextField()

    def __str__(self):
        return f'{self.cloudstack_event_server_id} : {self.id} / {self.routing_key} / {self.body}'


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
        self.save()
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
            parameter.save()


class Parameter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    required = models.BooleanField()
    command_id = models.ForeignKey('Command', on_delete=models.RESTRICT, related_name='parameter_ids')

    def __str__(self):
        return self.name


class APIRequest(models.Model):
    cloudstack_user_id = models.ForeignKey('CloudstackUser', on_delete=models.CASCADE, related_name='api_request_ids')
    created_at = models.DateTimeField(auto_now_add=True)
    command_id = models.ForeignKey('Command', on_delete=models.RESTRICT)
    result = models.TextField()

    def __str__(self):
        return f"{self.command_id.name}?{'&'.join([str(v) for v in self.value_ids.all()])}"

    def make_api_request(self):
        url_parts = urllib.parse.urlparse(self.cloudstack_user_id.url)
        baseurl = f'{url_parts.scheme}://{url_parts.netloc}{url_parts.path}?'
        my_request = {
            api_request_parameter_value.parameter_id.name: api_request_parameter_value.value
            for api_request_parameter_value in self.value_ids.all()
        }
        my_request['command'] = self.command_id.name
        my_request['response'] = 'json'
        my_request['apikey'] = self.cloudstack_user_id.api_key
        my_request_str = '&'.join(['='.join([k, urllib.parse.quote(my_request[k])]) for k in my_request.keys()])
        sig_str = '&'.join(['='.join([k.lower(), urllib.parse.quote(my_request[k].lower().replace('+', '%20'))])for k in sorted(my_request.keys())])
        req_str = baseurl + my_request_str + '&signature=' + self.sign_request(sig_str, self.cloudstack_user_id.secret_key)
        req = urllib.request.Request(req_str)
        try:
            res = urllib.request.urlopen(req)
        except Exception as e:
            return json.loads(e.read())
        else:
            return json.loads(res.read())

    def sign_request(self, sig_str, secret_key):
        digest = hmac.new(secret_key.encode(), sig_str.encode(), hashlib.sha1).digest()
        sig = urllib.parse.quote(base64.encodebytes(digest).strip().decode())
        return sig


class APIRequestParameterValue(models.Model):
    request_id = models.ForeignKey('APIRequest', on_delete=models.RESTRICT, related_name='value_ids')
    parameter_id = models.ForeignKey('Parameter', on_delete=models.RESTRICT)
    value = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.parameter_id.name}={self.value}"
