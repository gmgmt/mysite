from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False



class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    # 重写展示列表
    list_display = ('username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser')


    def nickname(self, obj):
        return obj.profile.nickname
    # 展示列表显示中文
    nickname.short_description = '昵称'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')