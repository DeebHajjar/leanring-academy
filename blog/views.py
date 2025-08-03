from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from .models import Article, Category, Tag , ArticleComment  
from .forms import ArticleForm, CommentForm, GuestCommentForm, ArticleSearchForm


class CanPublishMixin(UserPassesTestMixin):
    """Mixin to check if user can publish articles (instructors and admins only)"""
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or 
            user.is_staff or 
            user.user_type == 'instructor'
        )


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Article.objects.published()
        
        # Search
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by tag
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET)
        context['featured_articles'] = Article.objects.featured()[:3]
        context['categories'] = Category.objects.filter(is_active=True)
        context['popular_tags'] = Tag.objects.all()[:10]
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        # Allow authors to view their own unpublished articles
        if self.request.user.is_authenticated:
            return Article.objects.filter(
                Q(status='published') | Q(author=self.request.user)
            )
        return Article.objects.published()
    
    def get_object(self):
        article = super().get_object()
        # Increment views count
        article.increment_views()
        return article
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Comments
        comments = article.comments.filter(is_approved=True, parent=None)
        context['comments'] = comments
        context['comments_count'] = article.comments.filter(is_approved=True).count()
        
        # Comment forms
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        else:
            context['comment_form'] = GuestCommentForm()
        
        # Related articles
        context['related_articles'] = Article.objects.published().filter(
            category=article.category
        ).exclude(id=article.id)[:4]
        
        return context


class ArticleCreateView(CanPublishMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Article created successfully!'))
        return response
    
    def get_success_url(self):
        if self.object.status == 'published':
            return self.object.get_absolute_url()
        else:
            return reverse('blog:my_articles')


class ArticleUpdateView(CanPublishMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def get_queryset(self):
        # Authors can only edit their own articles, superusers can edit all
        if self.request.user.is_superuser:
            return Article.objects.all()
        return Article.objects.filter(author=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Article updated successfully!'))
        return response
    
    def get_success_url(self):
        if self.object.status == 'published':
            return self.object.get_absolute_url()
        else:
            return reverse('blog:my_articles')


class ArticleDeleteView(CanPublishMixin, DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('blog:article_list')
    
    def get_queryset(self):
        # Authors can only delete their own articles, superusers can delete all
        if self.request.user.is_superuser:
            return Article.objects.all()
        return Article.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Article deleted successfully!'))
        return super().delete(request, *args, **kwargs)


class MyArticlesView(LoginRequiredMixin, ListView):
    """Display user's articles"""
    model = Article
    template_name = 'blog/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user).order_by('-created_at')
    
    def dispatch(self, request, *args, **kwargs):
        # Only allow instructors and admins
        if not (request.user.is_superuser or request.user.is_staff or 
                request.user.user_type == 'instructor'):
            messages.error(request, _('You do not have permission to access this page.'))
            return redirect('blog:article_list')
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, slug):
    """إضافة تعليق على المقال"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent_comment = None
        
        if parent_id:
            try:
                parent_comment = ArticleComment.objects.get(id=parent_id, article=article)
            except ArticleComment.DoesNotExist:
                parent_comment = None
        
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.article = article
                comment.author = request.user
                comment.parent = parent_comment
                comment.save()
                
                if parent_comment:
                    messages.success(request, _('Your reply has been added successfully!'))
                else:
                    messages.success(request, _('Your comment has been added successfully!'))
        else:
            form = GuestCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.article = article
                comment.parent = parent_comment
                comment.is_approved = False  # Require approval for guest comments
                comment.save()
                
                if parent_comment:
                    messages.success(request, _('Your reply has been submitted and is awaiting approval.'))
                else:
                    messages.success(request, _('Your comment has been submitted and is awaiting approval.'))
    
    return redirect('blog:article_detail', slug=slug)


def category_articles(request, slug):
    """Display articles in a specific category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    articles = Article.objects.published().filter(category=category)
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'articles': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category_articles.html', context)


def tag_articles(request, slug):
    """Display articles with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.published().filter(tags=tag)
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'articles': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'blog/tag_articles.html', context)


def search_articles(request):
    """Search articles"""
    form = ArticleSearchForm(request.GET)
    articles = Article.objects.published()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        
        if query:
            articles = articles.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        
        if category:
            articles = articles.filter(category=category)
        
        if tag:
            articles = articles.filter(tags=tag)
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'articles': page_obj,
        'page_obj': page_obj,
        'query': request.GET.get('query', ''),
    }
    return render(request, 'blog/search_results.html', context)
