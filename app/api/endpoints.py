from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.models import Book as BookModel, Review as ReviewModel
from app.schemas.schemas import BookCreate, BookUpdate, ReviewCreate, Book
from sqlalchemy.future import select
from typing import List
from app.core.auth import get_user  

router = APIRouter(
    dependencies=[Depends(get_user)]
)

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
@router.get("/books/{id}", response_model=BookCreate)
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, message="Book not found")
    return book

# Update book information
@router.put("/books/{id}", response_model=BookCreate)
async def update_book(id: int, book: BookUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    existing_book = result.scalar_one_or_none()
    if not existing_book:
        raise HTTPException(status_code=404, message="Book not found")
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
        raise HTTPException(status_code=404, message="Book not found")
    await session.delete(book)
    await session.commit()
    return {"message": "Book deleted successfully"}

# Add review for a book
@router.post("/books/{id}/reviews", response_model=ReviewCreate)
async def add_review(id: int, review: ReviewCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).where(BookModel.id == id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, message="Book not found")
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