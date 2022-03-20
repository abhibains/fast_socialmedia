# pylint: disable=no-name-in-module
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint


class PostBase(BaseModel):

    title: str
    content: str
    published: bool = (False)
    # gives a default value in case nothing is provided by front-end)
    # default to none if no value provided so we are not going with a default value like in previous case


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):  #responsible for sending the post schema out
    # returns the following fields in addition to the ones mentioned by PostBase
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut  #returns a pydantic type model called UserOut

    class Config():
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    Vote_Count: int  #keep the names of the return keywords same as that decides or applied in the query


class CreateUser(BaseModel):
    email: EmailStr  #we can make sure the entered string is a valid email using Pydantic valid email property, needs email validator installed(already installed as per pip freeze)
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  #direction of the vote, 1 for voting, 0 for removing
