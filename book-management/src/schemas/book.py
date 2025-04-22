from typing import Optional
from pydantic import BaseModel, Field

class AddBookSchema(BaseModel):
    title: str = Field(min_length=1,max_length=150)
    author:Optional[str] = None

class BookShema(AddBookSchema):
    id: int

class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=150)
    author: Optional[str] = None