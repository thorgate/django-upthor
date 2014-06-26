from upthor.models import TemporaryFileWrapper, show_in_admin

if show_in_admin():
    from django.contrib import admin

    admin.site.register(TemporaryFileWrapper)
