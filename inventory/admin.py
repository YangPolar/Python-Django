from django.contrib import admin
from .models import InventoryItem, Category

# Register your models here. So we can edit from web page 127.0.0.1:8000/admin
admin.site.register(InventoryItem)
admin.site.register(Category)
