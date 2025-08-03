from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Article, ArticleComment, Category, Tag


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles"""
    
    class Meta:
        model = Article
        fields = [
            'title', 'category', 'tags', 'excerpt', 'content', 
            'featured_image', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter article title...')
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Brief description of the article...')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': _('Write your article content here...')
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only superusers can mark articles as featured
        if user and not user.is_superuser:
            self.fields['is_featured'].widget = forms.HiddenInput()
            self.fields['is_featured'].initial = False
        
        # Filter active categories only
        self.fields['category'].queryset = Category.objects.filter(is_active=True)


class CommentForm(forms.ModelForm):
    """Form for adding comments to articles"""
    
    class Meta:
        model = ArticleComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Write your comment here...')
            })
        }


class GuestCommentForm(forms.ModelForm):
    """Form for guest users to add comments"""
    
    class Meta:
        model = ArticleComment
        fields = ['name', 'email', 'website', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your email')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your website (optional)')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Write your comment here...')
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Add any email validation logic here if needed
            pass
        return email


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Category name')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Category description (optional)')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class TagForm(forms.ModelForm):
    """Form for creating and editing tags"""
    
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tag name')
            })
        }


class ArticleSearchForm(forms.Form):
    """Form for searching articles"""
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles...'),
            'aria-label': _('Search articles')
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_('All categories'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label=_('All tags'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
