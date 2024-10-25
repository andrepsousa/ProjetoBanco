from django.contrib import admin
from .models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

    class Meta:
        model = User


admin.site.register(User)
