from django.contrib import admin
from .models import Category, Command, Parameter, APIRequest, APIRequestParameterValue

admin.site.register(Category)
admin.site.register(Command)
admin.site.register(Parameter)
admin.site.register(APIRequest)
admin.site.register(APIRequestParameterValue)
