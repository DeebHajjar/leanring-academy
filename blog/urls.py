from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Article URLs
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('article/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('my-articles/', views.MyArticlesView.as_view(), name='my_articles'),
    
    # Comment URLs
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
    # Category and Tag URLs
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('tag/<slug:slug>/', views.tag_articles, name='tag_articles'),
    
    # Search URL
    path('search/', views.search_articles, name='search_articles'),
]