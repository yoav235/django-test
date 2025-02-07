from .models import Book, Author

class AuthorSerializer:
    @staticmethod
    def serialize(author):
        return {
            "id": author.id,
            "name": author.name,
            "gender": author.gender,
            "image_url": author.image_url,
            "about": author.about,
            "fans_count": author.fans_count,
            "works_count": author.works_count,
            "goodreads_id": author.goodreads_id,
            "books": [book.book_id for book in author.books.all()]  # Get list of book IDs
        }

class BookSerializer:
    @staticmethod
    def serialize(book):
        return {
            "id": book.id,
            "title": book.title,
            "author": AuthorSerializer.serialize(book.author) if book.author else None,  # Nested Author
            "book_id": book.book_id,
            "work_id": book.work_id,
            "publication_year": book.publication_year,
            "average_rating": book.average_rating,
            "ratings_count": book.ratings_count,
            "text_reviews_count": book.text_reviews_count,
            "isbn": book.isbn,
            "genres": book.genres.split(",") if book.genres else [],  # Convert comma-separated genres into a list
            "language": book.language,
            "description": book.description,
            "favorite_by": [user.id for user in book.favorite_by.all()]  # List of user IDs who marked it as favorite
        }
