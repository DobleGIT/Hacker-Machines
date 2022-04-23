import django_filters

from .models import *

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['username']

