from django.contrib import admin
from .models import Category, Tag, Article, ArticleComment

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(ArticleComment)

# Register your models here.
