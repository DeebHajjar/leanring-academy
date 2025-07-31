from modeltranslation.translator import register, TranslationOptions
from .models import Instructor, Course, Lesson

@register(Instructor)
class InstructorTranslationOptions(TranslationOptions):
    fields = ('expertise', )

@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'short_description', 'requirements', 'what_you_learn')
    
@register(Lesson)
class LessonTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
