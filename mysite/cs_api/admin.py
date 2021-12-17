from django.contrib import admin
from .models import Category, CloudstackEventServer, CloudstackEventLog, Command, Parameter, APIRequest, APIRequestParameterValue

admin.site.register(Category)
admin.site.register(Command)
admin.site.register(Parameter)
admin.site.register(APIRequest)
admin.site.register(APIRequestParameterValue)
admin.site.register(CloudstackEventServer)
admin.site.register(CloudstackEventLog)
