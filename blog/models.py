from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User


class Category(models.Model):
    """Categories for articles"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            if not base_slug:  # If slugify returns empty (e.g., for Arabic text)
                base_slug = f"category-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # Ensure unique slug
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tags for articles"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            if not base_slug:  # If slugify returns empty (e.g., for Arabic text)
                base_slug = f"category-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # Ensure unique slug
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ArticleManager(models.Manager):
    """Custom manager for Article model"""
    
    def published(self):
        return self.filter(status='published', published_at__lte=timezone.now())
    
    def featured(self):
        return self.published().filter(is_featured=True)


class Article(models.Model):
    """Articles for blog"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    excerpt = models.CharField(max_length=300, help_text=_('Brief description of the article'))
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    objects = ArticleManager()
    
    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            if not base_slug:  # If slugify returns empty (e.g., for Arabic text)
                base_slug = f"article-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # Ensure unique slug
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != 'published':
            self.published_at = None
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at and self.published_at <= timezone.now()
    
    def increment_views(self):
        """Increment article views count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ArticleComment(models.Model):
    """Comments for articles"""
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # For non-registered users
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    is_approved = models.BooleanField(default=True)  # Auto-approve for registered users
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        author_name = self.author.get_full_name() if self.author else self.name
        return f"Comment by {author_name} on {self.article.title}"
    
    def save(self, *args, **kwargs):
        # Auto-approve comments from registered users
        if self.author and not self.pk:
            self.is_approved = True
        super().save(*args, **kwargs)
    
    @property
    def author_name(self):
        return self.author.get_full_name() if self.author else self.name
