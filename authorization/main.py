from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column
from sqlalchemy import  select

engine = create_async_engine('sqlite+aiosqlite:///users.db')

new_session = async_sessionmaker(engine,expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

app = FastAPI()

SessionDep = Annotated[AsyncSession,Depends(get_session)]

config = AuthXConfig()
config.JWT_SECRET_KEY = 'SECRET_KEY_FOR_PROJECT'
config.JWT_ACCESS_COOKIE_NAME = "MY_ACCESS_TOKEN"
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config=config)

class Base(DeclarativeBase):
    pass

class UserLoginSchema(BaseModel):
    username:str = Field(max_length=25)
    password: str = Field(max_length=25)


class UserModel(Base):
    __tablename__ = 'users'

    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str]
    password:Mapped[str]


@app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post('/login')
async def auth(credentials:UserLoginSchema,response: Response,session:SessionDep):
    query = select(UserModel).where(UserModel.username == credentials.username)
    result = await session.execute(query)
    if result.scalars().first().password == credentials.password:
        token = security.create_access_token(uid='1234')
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME,token)
        return { "access_token" : token }
    raise  HTTPException(status_code=401)

@app.post('/create_user')
async def create_user(new_user:UserLoginSchema,session:SessionDep):
    user = UserModel(
        username = new_user.username,
        password = new_user.password
    )
    session.add(user)
    await session.commit()
    return { "Success" : "User created successfully!" }

@app.get('/protected',dependencies=[Depends(security.access_token_required)])
def protected():
    return { "Success" : "You are authorized!" }

if __name__ == '__main__':
    uvicorn.run("main:app",reload=True)