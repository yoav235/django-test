import json
import random
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
import jwt
import datetime
from django.conf import settings


# JWT Helpers
def generate_jwt(user):
    payload = {
        "id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        token = auth_header.split(" ")[1]
        decoded = decode_jwt(token)
        if not decoded:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)
        request.user_id = decoded["id"]
        return func(request, *args, **kwargs)

    return wrapper


# Authentication Views
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return JsonResponse({"error": "Missing fields"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return JsonResponse({"message": "User registered successfully", "user_id": user.id})


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        user = User.objects.filter(username=username).first()

        if not user or not user.check_password(password):
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        token = generate_jwt(user)
        return JsonResponse({"token": token})


# Book Views
class BookListView(View):
    def get(self, request):
        query = request.GET.get("search")
        if query:
            books = Book.objects.filter(Q(title__icontains=query) | Q(author__name__icontains=query))
        else:
            books = Book.objects.all()
        return JsonResponse([BookSerializer.serialize(book) for book in books], safe=False)

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def post(self, request):
        data = json.loads(request.body)
        author = get_object_or_404(Author, id=data.get("author_id"))
        book = Book.objects.create(
            title=data["title"],
            author=author,
            book_id=data["book_id"],
            work_id=data["work_id"],
            publication_year=data.get("publication_year"),
            average_rating=data.get("average_rating"),
            ratings_count=data.get("ratings_count"),
            text_reviews_count=data.get("text_reviews_count"),
            isbn=data.get("isbn"),
            genres=data.get("genres"),
            language=data.get("language"),
            description=data.get("description"),
        )
        return JsonResponse({"message": "Book created", "book": BookSerializer.serialize(book)}, status=201)


class BookDetailView(View):
    def get(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        return JsonResponse(BookSerializer.serialize(book))

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def put(self, request, pk):
        data = json.loads(request.body)
        book = get_object_or_404(Book, id=pk)
        for key, value in data.items():
            setattr(book, key, value)
        book.save()
        return JsonResponse({"message": "Book updated", "book": BookSerializer.serialize(book)})

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def delete(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        book.delete()
        return JsonResponse({"message": "Book deleted"})


# Author Views
class AuthorListView(View):
    def get(self, request):
        authors = Author.objects.all()
        return JsonResponse([AuthorSerializer.serialize(author) for author in authors], safe=False)

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def post(self, request):
        data = json.loads(request.body)
        author = Author.objects.create(**data)
        return JsonResponse({"message": "Author created", "author": AuthorSerializer.serialize(author)}, status=201)


class AuthorDetailView(View):
    def get(self, request, pk):
        author = get_object_or_404(Author, id=pk)
        return JsonResponse(AuthorSerializer.serialize(author))

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def put(self, request, pk):
        data = json.loads(request.body)
        author = get_object_or_404(Author, id=pk)
        for key, value in data.items():
            setattr(author, key, value)
        author.save()
        return JsonResponse({"message": "Author updated", "author": AuthorSerializer.serialize(author)})

    @method_decorator(csrf_exempt)
    @method_decorator(jwt_required)
    def delete(self, request, pk):
        author = get_object_or_404(Author, id=pk)
        author.delete()
        return JsonResponse({"message": "Author deleted"})


# Favorite Books & Recommendations
@method_decorator(csrf_exempt, name='dispatch')
class FavoriteBookView(View):
    @method_decorator(jwt_required)
    def post(self, request):
        data = json.loads(request.body)
        user = get_object_or_404(User, id=request.user_id)
        book = get_object_or_404(Book, id=data["book_id"])

        if book in user.favorite_books.all():
            user.favorite_books.remove(book)
            return JsonResponse({"message": "Book removed from favorites"})

        if user.favorite_books.count() >= 20:
            return JsonResponse({"error": "You can only have 20 favorite books"}, status=400)

        user.favorite_books.add(book)
        return JsonResponse({"message": "Book added to favorites", "recommendations": get_recommendations(user)})


def get_recommendations(user):
    favorite_books = user.favorite_books.all()
    genres = set()

    for book in favorite_books:
        if book.genres:
            genres.update(book.genres.split(","))

    recommended_books = Book.objects.filter(
        Q(genres__icontains=random.choice(list(genres))) if genres else Q()
    ).exclude(id__in=[book.id for book in favorite_books]).order_by("?")[:5]

    return [BookSerializer.serialize(book) for book in recommended_books]
