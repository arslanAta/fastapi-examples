import uvicorn
from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import  create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

# Creating engine for connect to database
engine = create_async_engine('sqlite+aiosqlite:///books.db')

# Creating session maker
new_session = async_sessionmaker(engine,expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class BookAuthorSchema(BaseModel):
    id: int
    name: str = Field(min_length=1,max_length=100)
    age: int = Field(ge=1)

class AddBookSchema(BaseModel):
    title: str = Field(min_length=1,max_length=150)
    author:Optional[str] = None

class BookShema(AddBookSchema):
    id: int

class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=150)
    author: Optional[str] = None

class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]

app = FastAPI()

SessionDep = Annotated[AsyncSession,Depends(get_session)]

books:list[BookShema] = []

@app.get('/books')
async def get_books(session:SessionDep):
    query = select(BookModel)
    result  = await session.execute(query)
    return result.scalars().all()

@app.post('/books')
async def add_book(new_book:AddBookSchema,session:SessionDep):
    new_book = BookModel(
        title=new_book.title,
        author=new_book.author if new_book.author else None
    )
    session.add(new_book)
    await session.commit()
    return {"Success":"Book successfully added!"}

@app.get('/books/{book_id}')
async def get_book_by_id(book_id:int,session:SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    for book in result.scalars().all():
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404)

@app.patch('/books/{book_id}')
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


@app.delete('/books/{book_id}')
async def delete_book(book_id:int,session:SessionDep):
    query = select(BookModel).where(BookModel.id==book_id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404)
    await session.delete(book)
    await session.commit()
    return {"Success": f"Book {book_id} deleted"}

# Endpoint for create database
@app.post('/setup_database')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"Success":'Database created'}

if __name__ == '__main__':
    uvicorn.run("main:app",reload=True)