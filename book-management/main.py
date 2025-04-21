import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

class BookAuthorSchema(BaseModel):
    id: int
    name: str = Field(min_length=1,max_length=100)
    age: int = Field(ge=1)

class AddBookSchema(BaseModel):
    name: str = Field(min_length=1,max_length=150)
    author: Optional[BookAuthorSchema] = None
    tags: Optional[list[str]] = None

class BookShema(AddBookSchema):
    id: int

app = FastAPI()

books:list[BookShema] = []

@app.get('/books')
def get_books():
    return books

@app.post('/books')
def add_book(new_book:AddBookSchema):
    book = BookShema(
        id=len(books) + 1,
        name=new_book.name,
        tags=new_book.tags,
        author=new_book.author if new_book.author else None
    )
    books.append(book)
    return book

@app.get('/books/{book_id}')
def get_book_by_id(book_id:int):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404)

@app.delete('/books/{book_id}')
def delete_book(book_id):
    for book in books:
        if book.id == book_id:
            books.remove(book)
            return book
    raise HTTPException(status_code=404)

@app.patch('/books/{book_id}')
def update_book(book_id:int,updated_book:AddBookSchema):
    for index, book in enumerate(books):
        if book.id == book_id:

            updated_data = updated_book.model_dump(exclude_unset=True)

            updated_book_instance = book.model_copy(update=updated_data)

            books[index] = updated_book_instance
            return updated_book_instance

    raise HTTPException(status_code=404)

@app.delete('/books/{book_id}')
def delete_book(book_id:int):
    for book in books:
        if book.id == book_id:
            books.remove(book)
            return {"Sucess":"Book is successfully deleted"}
    raise HTTPException(status_code=404)

if __name__ == '__main__':
    uvicorn.run("main:app",reload=True)