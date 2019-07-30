# -*- encoding: utf-8 -*-
from django.conf import settings
from django.db import models

from dbmail import app_installed

USE_HTML_EDITOR = getattr(settings, "DBMAIL_USE_HTML_EDITOR", False)
HTMLField = models.TextField
DataTextField = models.TextField

if USE_HTML_EDITOR and app_installed('tinymce'):
    try:
        from tinymce.models import HTMLField
    except ImportError:
        pass

if USE_HTML_EDITOR and app_installed('ckeditor'):
    try:
        from ckeditor.fields import RichTextField as HTMLField
    except ImportError:
        pass
