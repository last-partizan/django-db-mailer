# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url
from django.shortcuts import redirect

from django.contrib import admin

from dbmail.models import (
    MailCategory, MailTemplate, MailLog,
    MailLogEmail, MailGroup, MailGroupEmail)
from dbmail import send_db_mail
from dbmail import defaults


class MailCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'updated', 'id',)
    list_filter = ('created', 'updated',)
    search_fields = ('name',)


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'subject', 'slug', 'is_admin', 'is_html',
        'num_of_retries', 'priority', 'created', 'updated', 'id',
    )
    list_filter = (
        'category', 'is_admin', 'is_html', 'priority', 'created', 'updated',)
    search_fields = (
        'name', 'subject', 'slug', 'message',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-id',)
    list_editable = ('category', 'priority',)
    list_display_links = ('name',)
    date_hierarchy = 'created'
    list_per_page = 20

    class Media:
        js = (
            '/static/dbmail/admin/js/dbmail.js',
        )

    def send_mail_view(self, request, pk):
        slug = MailTemplate.objects.get(pk=pk).slug
        send_db_mail(slug, request.user.email, request.user)
        return redirect(
            reverse(
                'admin:dbmail_mailtemplate_change', args=(pk,),
                current_app=self.admin_site.name
            )
        )

    def get_urls(self):
        urls = super(MailTemplateAdmin, self).get_urls()
        admin_urls = patterns(
            '',
            url(
                r'^(\d+)/sendmail/$',
                self.admin_site.admin_view(self.send_mail_view),
                name='send_mail_view'
            ),
        )
        return admin_urls + urls

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and defaults.READ_ONLY_ENABLED:
            return ['slug', 'context_note']
        return self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        if obj is not None:
            return {}
        return self.prepopulated_fields


class MailLogEmailInline(admin.TabularInline):
    readonly_fields = [field.name for field in MailLogEmail._meta.fields]
    model = MailLogEmail
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method != 'POST'


class MailLogAdmin(admin.ModelAdmin):
    list_display = (
        'template', 'created', 'is_sent', 'num_of_retries', 'user', 'id',)
    list_filter = ('is_sent', 'created',)
    date_hierarchy = 'created'
    inlines = [MailLogEmailInline]

    def __init__(self, model, admin_site):
        super(MailLogAdmin, self).__init__(model, admin_site)

        self.readonly_fields = [field.name for field in model._meta.fields]
        self.readonly_model = model

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method != 'POST'


class MailGroupEmailInline(admin.TabularInline):
    model = MailGroupEmail
    extra = 1


class MailGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created', 'updated', 'id',)
    list_filter = ('updated', 'created',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MailGroupEmailInline]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and defaults.READ_ONLY_ENABLED:
            return ['slug']
        return self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        if obj is not None:
            return {}
        return self.prepopulated_fields


admin.site.register(MailCategory, MailCategoryAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)
admin.site.register(MailLog, MailLogAdmin)
admin.site.register(MailGroup, MailGroupAdmin)
