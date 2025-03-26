from pydantic import BaseModel, Field
from typing import Optional, List

class BookBase(BaseModel):
    title: str = Field(..., example="The Lean Startup")
    author: str = Field(..., example="Eric Ries")
    genre: str = Field(..., example="Business")
    year_published: int = Field(..., example=2011)
    summary: Optional[str] = Field(None, example="A book about building lean startups using scientific methodology.")

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Updated Book Title")
    author: Optional[str] = Field(None, example="Updated Author")
    genre: Optional[str] = Field(None, example="Updated Genre")
    year_published: Optional[int] = Field(None, example=2022)
    summary: Optional[str] = Field(None, example="Updated summary of the book.")

class ReviewCreate(BaseModel):
    user_id: int = Field(..., example=101)
    review_text: str = Field(..., example="A must-read for anyone building a startup!")
    rating: float = Field(..., example=4.5)

class SummaryRequest(BaseModel):
    content: str = Field(..., example="This is a detailed narrative about how startups can grow using customer feedback and iteration.")
