from django.contrib import admin

from ctfboard.models import UserProfile, CTF, CTFLevel, WriteUp

admin.site.register(UserProfile)
admin.site.register(CTF)
admin.site.register(CTFLevel)
admin.site.register(WriteUp)