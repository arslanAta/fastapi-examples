from fastapi import APIRouter
from src.api.book import book_router

main_router = APIRouter()
main_router.include_router(book_router)