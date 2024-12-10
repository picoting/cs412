"""
Ting Liu
tinglliu@bu.edu
register models to admin
"""


from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(Review)