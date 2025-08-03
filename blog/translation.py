from modeltranslation.translator import register, TranslationOptions
from .models import Category, Tag

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

