from django.contrib import admin
from .models import *
from django_extensions.admin import ForeignKeyAutocompleteAdmin

# Removes a default model we don't care about
from django.contrib.auth.models import Group
admin.site.unregister(Group)

# Tell admin site which fields to show and base searches on
class UserProfileAdmin(ForeignKeyAutocompleteAdmin):
    exclude = ('user_permissions',)

    list_display = ('email', 'first_name', 'last_name')

    search_fields = ('email', 'first_name', 'last_name')
admin.site.register(UserProfile, UserProfileAdmin)

class GameAdmin(ForeignKeyAutocompleteAdmin):
	list_display = ('timestamp', 'end_time', 'winner')

	search_fields = ('timestamp', 'end_time', 'winner')
admin.site.register(Game, GameAdmin)

class GameParticipationAdmin(ForeignKeyAutocompleteAdmin):
	list_display = ('user', 'game', 'role')

	search_fields = ('user__email', 'game__timestamp', 'role')
admin.site.register(GameParticipation, GameParticipationAdmin)

class RoleAdmin(ForeignKeyAutocompleteAdmin):
	list_display = ('name', 'team', 'description')

	search_fields = ('name', 'team', 'description')
admin.site.register(Role, RoleAdmin)