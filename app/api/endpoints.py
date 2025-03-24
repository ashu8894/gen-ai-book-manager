from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.models import Book as BookModel, Review as ReviewModel
from app.schemas.schemas import BookCreate, BookUpdate, ReviewCreate, Book, SummaryRequest
from sqlalchemy.future import select
from typing import List
from app.core.auth import get_user  
from app.services.ai import generate_summary

router = APIRouter(
    dependencies=[Depends(get_user)]
)

# Create a new book.
@router.post("/books", response_model=Book)
async def create_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    new_book = BookModel(**book.dict())
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book

# Retrieve all books
@router.get("/books", response_model=List[BookCreate])
async def get_books(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel))
    return result.scalars().all()

# Retrieve specific book by ID
@router.get("/books/{id}", response_model=Book)
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Update book information
@router.put("/books/{id}", response_model=BookCreate)
async def update_book(id: int, book: BookUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    existing_book = result.scalar_one_or_none()
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict(exclude_unset=True).items():
        setattr(existing_book, key, value)
    await session.commit()
    await session.refresh(existing_book)
    return existing_book

# Delete a book
@router.delete("/books/{id}")
async def delete_book(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await session.delete(book)
    await session.commit()
    return {"message": "Book deleted successfully"}

# Add review for a book
@router.post("/books/{id}/reviews", response_model=ReviewCreate)
async def add_review(id: int, review: ReviewCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    new_review = ReviewModel(book_id=id, **review.dict())
    session.add(new_review)
    await session.commit()
    await session.refresh(new_review)
    return new_review

# Retrieve all reviews for a book
@router.get("/books/{id}/reviews", response_model=List[ReviewCreate])
async def get_reviews(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ReviewModel).where(ReviewModel.book_id == id))
    return result.scalars().all()

# Fetch a book's summary along with its average rating and a concise summary of its reviews.
@router.get("/books/{id}/summary")
async def get_book_summary(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    review_result = await session.execute(select(ReviewModel).where(ReviewModel.book_id == id))
    reviews = review_result.scalars().all()

    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 2)
        review_text = "\n".join(r.review_text for r in reviews if r.review_text)
        review_summary_prompt = f"Summarize the following reviews in a single sentence. Do not add any introduction or explanation. Only return the core content:\n{review_text}"
        review_summary = await generate_summary(review_summary_prompt)
    else:
        avg_rating = None
        review_summary = "No reviews available."

    book_summary = book.summary
    if not book_summary:
        summary_prompt = f"Summarize this book:\n{book.title} by {book.author}"
        book_summary = await generate_summary(summary_prompt)

    return {
        "book_id": id,
        "title": book.title,
        "author": book.author,
        "average_rating": avg_rating,
        "book_summary": book_summary,
        "review_summary": review_summary
    }

# Fetch book recommendations based on a given genre.
@router.get("/recommendations")
async def get_recommendations(genre: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(BookModel).where(BookModel.genre.ilike(f"%{genre}%"))
    )
    books = result.scalars().all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found for this genre")

    recommendations = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published
        }
        recommendations.append(book_data)
    return recommendations

# Generate a summary for the given book content using LLaMA3.
@router.post("/books/generate-summary")
async def generate_summary_endpoint(payload: SummaryRequest):
    prompt = f"Summarize this book:\n{payload.content}"
    summary = await generate_summary(prompt)
    return {"summary": summary}