import uvicorn
from fastapi import FastAPI, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig
from pydantic import BaseModel

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = 'SECRET_KEY_FOR_PROJECT'
config.JWT_ACCESS_COOKIE_NAME = "MY_ACCESS_TOKEN"
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config=config)

class UserLoginSchema(BaseModel):
    username:str
    password:str

@app.post('/login')
def auth(credentials:UserLoginSchema,response: Response):
    if credentials.password == 'test' and credentials.username == 'test':
        token = security.create_access_token(uid='1234')
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME,token)
        return { "access_token" : token }
    raise  HTTPException(status_code=401)

@app.get('/protected',dependencies=[Depends(security.access_token_required)])
def protected():
    return { "Success" : "You are authorized!" }

if __name__ == '__main__':
    uvicorn.run("main:app",reload=True)