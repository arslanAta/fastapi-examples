from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.api.dependencies import SessionDep
from src.database import Base, engine
from src.models.books import BookModel
from src.schemas.book import AddBookSchema, UpdateBookSchema

book_router = APIRouter()

@book_router.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@book_router.get('/books',tags=["Book management"])
async def get_books(session:SessionDep):
    query = select(BookModel)
    result  = await session.execute(query)
    return result.scalars().all()

@book_router.post('/books',tags=["Book management"])
async def add_book(new_book:AddBookSchema,session:SessionDep):
    new_book = BookModel(
        title=new_book.title,
        author=new_book.author if new_book.author else None
    )
    session.add(new_book)
    await session.commit()
    return {"Success":"Book successfully added!"}

@book_router.get('/books/{book_id}',tags=["Book management"])
async def get_book_by_id(book_id:int,session:SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    for book in result.scalars().all():
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404)

@book_router.patch('/books/{book_id}',tags=["Book management"])
async def update_book(book_id:int,updated_book:UpdateBookSchema,session:SessionDep):
    # Get book by id
    query = select(BookModel).where(BookModel.id == book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    # Return 404 if book not exists in given id
    if not book:
        raise HTTPException(status_code=404)

    update_fields = updated_book.model_dump(exclude_unset=True)

    # Update book values dynamically
    for field, value in update_fields.items():
        setattr(book, field, value)

    # Save changes and refresh
    await session.commit()
    await session.refresh(book)

    return {"Success": f"Book {book_id} updated", "data": update_fields}

# Delete book by id
@book_router.delete('/books/{book_id}',tags=["Book management"])
async def delete_book(book_id:int,session:SessionDep):

    # Find book by id
    query = select(BookModel).where(BookModel.id==book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()

    # Return error if book in given id not exists
    if not book:
        raise HTTPException(status_code=404)

    # Delete book and commit changes
    await session.delete(book)
    await session.commit()
    return {"Success": f"Book {book_id} deleted"}
