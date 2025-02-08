from django.urls import path
from .views import (
    RegisterView, LoginView,
    BookListView, BookDetailView,
    AuthorListView, AuthorDetailView,
    FavoriteBookView, csrf_token_view

)

urlpatterns = [

    path('csrf-token/', csrf_token_view, name='csrf-token'),
    # Authentication Endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # Book Endpoints
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),

    # Author Endpoints
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),

    # Favorite Books & Recommendations
    path('favorites/', FavoriteBookView.as_view(), name='favorites'),
]
