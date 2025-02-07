from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    """Model for storing author details"""
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    fans_count = models.IntegerField(default=0)
    works_count = models.IntegerField(default=0)
    goodreads_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    """Model for storing book details"""
    title = models.CharField(max_length=500)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    book_id = models.CharField(max_length=50, unique=True)
    work_id = models.CharField(max_length=50)
    publication_year = models.IntegerField(null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    ratings_count = models.IntegerField(default=0)
    text_reviews_count = models.IntegerField(default=0)
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    favorite_by = models.ManyToManyField(User, related_name="favorite_books", blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """Extending Django's User Model to store favorite books"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_books = models.ManyToManyField(Book, related_name="favorited_by", blank=True)

    def __str__(self):
        return self.user.username
