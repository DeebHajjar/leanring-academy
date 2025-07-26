from django.utils import translation

class PreferredLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_code = request.session.get('django_language')
        user = request.user
        if lang_code:
            translation.activate(lang_code)
            request.LANGUAGE_CODE = lang_code
        elif user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile and profile.preferred_language:
                translation.activate(profile.preferred_language)
                request.LANGUAGE_CODE = profile.preferred_language
        response = self.get_response(request)
        return response
