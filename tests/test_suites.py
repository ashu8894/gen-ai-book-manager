import asyncio
import pytest
from tests.utils import basic_auth_headers

# Test creating a new book via the API
@pytest.mark.asyncio
async def test_create_book(client):
    headers = basic_auth_headers()
    response = await client.post("/books", json={
        "title": "Test Book",
        "author": "Tester",
        "genre": "Sci-Fi",
        "year_published": 2023,
        "summary": "Test summary"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Book"

# Test retrieving all books
@pytest.mark.asyncio
async def test_get_books(client):
    headers = basic_auth_headers()
    response = await client.get("/books", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test fetching a specific book by its ID
@pytest.mark.asyncio
async def test_get_book_by_id(client):
    headers = basic_auth_headers()
    create_resp = await client.post("/books", json={
        "title": "Fetch Book",
        "author": "Author X",
        "genre": "Mystery",
        "year_published": 2022,
        "summary": "Mystery summary"
    }, headers=headers)
    book_id = create_resp.json()["id"]

    response = await client.get(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Fetch Book"

# Test updating an existing book
@pytest.mark.asyncio
async def test_update_book(client):
    headers = basic_auth_headers()
    create_resp = await client.post("/books", json={
        "title": "Old Title",
        "author": "Old Author",
        "genre": "Drama",
        "year_published": 2010,
        "summary": "Old summary"
    }, headers=headers)
    book_id = create_resp.json()["id"]

    update_resp = await client.put(f"/books/{book_id}", json={
        "title": "New Title",
        "author": "New Author",
        "genre": "Drama",
        "year_published": 2011,
        "summary": "New summary"
    }, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New Title"

# Test deleting a book and confirming it's removed
@pytest.mark.asyncio
async def test_delete_book(client):
    headers = basic_auth_headers()
    create_resp = await client.post("/books", json={
        "title": "To Be Deleted",
        "author": "Someone",
        "genre": "Thriller",
        "year_published": 2019,
        "summary": "Bye"
    }, headers=headers)
    print(create_resp.json())
    book_id = create_resp.json()["id"]
    del_resp = await client.delete(f"/books/{book_id}", headers=headers)
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/books/{book_id}", headers=headers)
    assert get_resp.status_code == 404

# Test adding a review to a book
@pytest.mark.asyncio
async def test_add_review(client):
    headers = basic_auth_headers()
    book = (await client.post("/books", json={
        "title": "Review Book",
        "author": "Critic",
        "genre": "Non-Fiction",
        "year_published": 2020,
        "summary": "Reviewable"
    }, headers=headers)).json()

    response = await client.post(f"/books/{book['id']}/reviews", json={
        "user_id": 1,
        "review_text": "Amazing book!",
        "rating": 5
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["review_text"] == "Amazing book!"

# Test retrieving all reviews for a book
@pytest.mark.asyncio
async def test_get_reviews(client):
    headers = basic_auth_headers()
    book = (await client.post("/books", json={
        "title": "Multi Review Book",
        "author": "Multiple",
        "genre": "Biography",
        "year_published": 2018,
        "summary": "Many opinions"
    }, headers=headers)).json()

    for i in range(3):
        await client.post(f"/books/{book['id']}/reviews", json={
            "user_id": i + 1,
            "review_text": f"Review {i + 1}",
            "rating": 4
        }, headers=headers)

    response = await client.get(f"/books/{book['id']}/reviews", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

# Test getting the summary of a book, including average rating
@pytest.mark.asyncio
async def test_book_summary(client):
    headers = basic_auth_headers()
    book = (await client.post("/books", json={
        "title": "Summary Book",
        "author": "Summarizer",
        "genre": "Essay",
        "year_published": 2015,
        "summary": "Placeholder summary"
    }, headers=headers)).json()

    await client.post(f"/books/{book['id']}/reviews", json={
        "user_id": 1,
        "review_text": "Very thoughtful",
        "rating": 4
    }, headers=headers)

    response = await client.get(f"/books/{book['id']}/summary", headers=headers)
    assert response.status_code == 200
    assert "average_rating" in response.json()

# Test getting book recommendations by genre
@pytest.mark.asyncio
async def test_recommendations(client):
    headers = basic_auth_headers()
    genre = "Poetry"
    await client.post("/books", json={
        "title": "Poetic One",
        "author": "Poet",
        "genre": genre,
        "year_published": 2021,
        "summary": "Poetic summary"
    }, headers=headers)

    response = await client.get(f"/recommendations?genre={genre}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

# Test AI-powered summary generation for raw book content
@pytest.mark.asyncio
async def test_generate_summary(client):
    headers = basic_auth_headers()
    response = await client.post("/books/generate-summary", json={
        "content": "This is a very long and interesting book content that needs summarizing."
    }, headers=headers)
    assert response.status_code == 200
    assert "summary" in response.json()
