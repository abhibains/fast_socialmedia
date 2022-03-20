# pylint: disable=no-name-in-module
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models
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


class Post(BaseModel):

    title: str
    content: str
    published: bool = (
        False  # gives a default value in case nothing is provided by front-end
    )
    # default to none if no value provided so we are not going with a default value like in previous case


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
def get_posts():
    cursor.execute(
        """ SELECT * FROM posts """)  # cursor executes SQL code within """ """
    posts_db = cursor.fetchall()
    # all the result from the previous SQL query is fetched and stored
    # fastapi will automatically serialise it and convert it to json format to send it back
    return {"data": posts_db}


# obtaining specific posts, {id} field is called path parameter. Fastapi will automatically extract this id
@app.get("/posts/{id}")
# validating that the value received is int and not string. If string, the value is then converted
def get_post(id: int, response_code: Response):
    stringed_int = str(
        id
    )  #we need a string here because we need 'id' to be a string because the SQL query is string itself. At the same time we want to     validate it as 'int' because we don't want user to send a string as id for the request
    print(f"************ value is {stringed_int} ************")
    cursor.execute(
        """ SELECT * FROM posts WHERE id = %s """, (stringed_int, )
    )  # for some reason converting double digits to strings is throwing an error. The solution is psycopg2 has this weird issue where it needs a tuple
    #https://stackoverflow.com/questions/21524482/psycopg2-typeerror-not-all-arguments-converted-during-string-formatting
    get_post = cursor.fetchone()
    if not get_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} was not found :(",
        )
        # return {"message": "Given id was not found"}
    return {"post_detail": get_post}


# by default this code sends the 200 OK code, to override default code, put status code in the decorator
@app.post("/posts", status_code=status.HTTP_201_CREATED)
# post : Post ensures that data received is being validated against the Post class
def create_posts(post: Post):
    cursor.execute(
        """ INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published)
    )  #must avoid using f strings to directly uses post.title and others in VALUES()
    #any time a entry is created in Postgres, it can be obtained using RETURNING keyword
    #using the above method makes psycopg2 sanitize the input to avoid SQL injections
    newpost_db = cursor.fetchone()
    conn.commit()
    return {
        "post added": newpost_db
    }  # THIS IS WILL VALID RESULT BACK TO API BUT NO CHANGES ON DB UNLESS YOU COMMIT, because these are staged changes and in order to finalise the changes, commit is used.


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""",
                   (str(id), ))
    deleted_db = cursor.fetchone()
    conn.commit()

    if not deleted_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exists :(",
        )

    return {"deleted post": deleted_db}


@app.put("/posts/{id}")
# since we are receiving the same info from frontend, we wanna make sure it follows the right schema
def update_post(id: int, post: Post):
    cursor.execute(
        """ UPDATE posts SET title =%s, content =%s , published=%s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id)))
    updated_db = cursor.fetchone()
    conn.commit()
    if updated_db == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exists :(")
    return {"updated post": updated_db}


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
