# pylint: disable=no-name-in-module
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import Optional
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()  # instance of fast api created

my_posts = [
    {
        "title": "This is post numero uno",
        "content": "content for post 1",
        "id": 1
    },
    {
        "title": "This is post numero duos",
        "content": "content for post 2",
        "id": 2
    },
]

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="1996",
            cursor_factory=RealDictCursor,
        )  # cursor_factory parameter is used to obtain the name of the columns while using Postgres from python app hence the .extra imports
        cursor = conn.cursor()  # cursor is used to make changes to database
        print("Database connection established...")
        break  # breaks out of the while loop if succesfully connected otherwise retries
    except Exception as error:
        print("No connection to database available, retrying in 2 secs")
        print(f"Error reported {error}")
        time.sleep(2)
"""
@app.get(
    "/"
)  # @ = python decorator, get= method, "/" = path or route path that comes after domain name of API, root()= function, entire block called path operation or just called route
def get_message():
    return {"message": "hello-world is this changing, this is without the autosave "}
"""


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    # enumerate marks every entry with indices starting from 0
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts_db = db.query(models.Post).all()

    return posts_db  #fastapi will automatically serialise the output and convert it into json


# obtaining specific posts, {id} field is called path parameter. Fastapi will automatically extract this id
@app.get("/posts/{id}")
# validating that the value received is int and not string. If string, the value is then converted
def get_post(id: int, response_code: Response, db: Session = Depends(get_db)):
    get_post = db.query(models.Post).filter(
        models.Post.id == id).first()  #.all keeps looking after finding match
    if not get_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} was not found :(",
        )
        # return {"message": "Given id was not found"}
    return get_post


# by default this code sends the 200 OK code, to override default code, put status code in the decorator
@app.post("/posts",
          status_code=status.HTTP_201_CREATED,
          response_model=schemas.Post)
# post : Post ensures that data received is being validated against the Post class
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    #fields can be populated using the dict() function for pydantic object 'post' and it's unpacking feature( ** )
    #this way no manual field generation is required like in the ''' comment below
    #print(post.dict())
    newpost_db = models.Post(
        **post.dict()
    )  #post models for pydantic(for validation) and database Post table are different
    '''newpost_db = models.Post(
        title=post.title, content=post.content,
        published=post.published)  #setting field equals to post paramter input
    '''
    db.add(newpost_db)
    # above query is just a query, in order to run it against the DB and make changes we need .add()
    db.commit()  # to commit the changes
    db.refresh(newpost_db)
    # mimics the RETURNING keyword where it stores the new changes to the provided parameter variable
    return newpost_db
    # THIS IS WILL VALID RESULT BACK TO API BUT NO CHANGES ON DB UNLESS YOU COMMIT, because these are staged changes and in order to finalise the changes, commit is used.


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_db = db.query(models.Post).filter(models.Post.id == id)
    #filter is involved everytime with id
    # this is just the query which is not run yet on DB, .all or .first make it run
    if not deleted_db.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exists :(",
        )
    deleted_db.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
# since we are receiving the same info from frontend, we wanna make sure it follows the right schema
def update_post(id: int,
                update_post: schemas.PostCreate,
                db: Session = Depends(get_db)):

    query = db.query(models.Post).filter(models.Post.id == id)
    post_query = query.first()
    if post_query == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exists :(")
    query.update(update_post.dict(), synchronize_session=False)
    # update takes a dictionary, so we do not need to unpack
    #similar to query.update({'title':'updated title', 'content':'new content!!'}, 'published':true)}, synchronize_session = False)
    db.commit()
    return query.first(
    )  #since commit has already been made, this would pick the entry same id but updated content.


@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut
)  #returning the message as per according to the pydantic schema model which has to be converted because the query provides SQLALCHEMY model to beign with
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):

    hashed_pwd = utils.hashpassword(user.password)
    #providing the password field of the request body stored in 'user'
    #user here is the variable stroing the request body in a pydantic object
    user.password = hashed_pwd
    #storing the hashed password back in the request body before it is added to the db

    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.Post.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with id:{id} found")
    return user


"""
@app.post("/createposts")
def create_posts(
    new_post: dict = Body(...),
):  # catches all the fields from request body, converts them to dict and store in new_post
    print(new_post["Content"])
    print(new_post)
    return {"message": "Successfully created the post"}


"""
"""
@app.post("/createposts") #example of retrieving pydantic object and it's various attributes
def create_posts(new_post: Post):
    print(new_post.title)
    print(new_post.content)
    print(new_post.published)
    print(new_post.date)
    print(new_post)
    print(new_post.dict())
    return{"message": "Post with body received and successfully created"}
"""
