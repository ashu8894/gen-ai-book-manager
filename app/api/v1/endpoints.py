from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_session
from app.core.auth import get_user
from app.models.models import Book as BookModel, Review as ReviewModel
from app.schemas.schemas import BookCreate, BookUpdate, ReviewCreate, Book, SummaryRequest
from app.services.ai import generate_summary

router = APIRouter(
    dependencies=[Depends(get_user)]
)

@router.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    description="Add a new book with title, author, genre, year, and optional summary."
)
async def create_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    new_book = BookModel(**book.dict())
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book

@router.get(
    "/books",
    response_model=List[Book],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all books",
    description="Fetch all books stored in the database."
)
async def get_books(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel))
    return result.scalars().all()

@router.get(
    "/books/{id}",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a book by ID",
    description="Fetch a specific book by its ID."
)
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put(
    "/books/{id}",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    summary="Update a book",
    description="Update the information of a specific book by its ID."
)
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

@router.delete(
    "/books/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a book",
    description="Delete a book from the database by its ID."
)
async def delete_book(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await session.delete(book)
    await session.commit()
    return {"message": "Book deleted successfully"}

@router.post(
    "/books/{id}/reviews",
    response_model=ReviewCreate,
    status_code=status.HTTP_200_OK,
    summary="Add a review",
    description="Add a review for a specific book using book ID."
)
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

@router.get(
    "/books/{id}/reviews",
    response_model=List[ReviewCreate],
    status_code=status.HTTP_200_OK,
    summary="Get book reviews",
    description="Retrieve all reviews for a specific book."
)
async def get_reviews(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ReviewModel).where(ReviewModel.book_id == id))
    return result.scalars().all()

@router.get(
    "/books/{id}/summary",
    status_code=status.HTTP_200_OK,
    summary="Get book summary and average rating",
    description="Fetch the book summary and a concise review summary with average rating using LLaMA3."
)
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

@router.get(
    "/recommendations",
    status_code=status.HTTP_200_OK,
    summary="Get book recommendations",
    description="Retrieve book recommendations based on a provided genre."
)
async def get_recommendations(genre: str = Query(..., description="Genre to filter recommendations by"), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(BookModel).where(BookModel.genre.ilike(f"%{genre}%"))
    )
    books = result.scalars().all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found for this genre")

    recommendations = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published
        } for book in books
    ]
    return recommendations

@router.post(
    "/books/generate-summary",
    status_code=status.HTTP_200_OK,
    summary="Generate AI summary",
    description="Generate a book summary using the LLaMA3 model from raw content."
)
async def generate_summary_endpoint(payload: SummaryRequest):
    prompt = f"Summarize this book:\n{payload.content}"
    summary = await generate_summary(prompt)
    return {"summary": summary}
