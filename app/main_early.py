# pylint: disable=no-name-in-module
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor

app = FastAPI()  # instance of fast api created
my_posts = [{
    "title": "This is post numero uno",
    "content": "content for post 1",
    "id": 1
}, {
    "title": "This is post numero duos",
    "content": "content for post 2",
    "id": 2
}]

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database='fastapi',
            user='postgres',
            password='1996',
            cursor_factory=RealDictCursor
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
    published: bool = False  # gives a default value in case nothing is provided by front-end
    # default to none if no value provided so we are not going with a default value like in previous case


'''
@app.get(
    "/"
)  # @ = python decorator, get= method, "/" = path or route path that comes after domain name of API, root()= function, entire block called path operation or just called route
def get_message():
    return {"message": "hello-world is this changing, this is without the autosave "}
'''


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    # enumerate marks every entry with indices starting from 0
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/posts")
def get_posts():
    # fastapi will automatically serialise it and convert it to json format to send it back
    return {"data": my_posts}


# obtaining specific posts, {id} field is called path parameter. Fastapi will automatically extract this id
@app.get("/posts/{id}")
# validating that the value received is int and not string. If string, the value is then converted
def get_post(id: int, response_code: Response):
    print(id)
    post_id = find_post(id)
    if not post_id:
        '''# response_code.status_code = 404  # sending appropriate status back to client
        response_code.status_code = status.HTTP_404_NOT_FOUND
        '''
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Given id {id} was not found :(")
        # return {"message": "Given id was not found"}
    return {"post_detail": f"Here is post {post_id}"}


# by default this code sends the 200 OK code, to override default code, put status code in the decorator
@app.post("/posts", status_code=status.HTTP_201_CREATED)
# post : Post ensures that data received is being validated against the Post class
def create_posts(post: Post):
    # print(post)
    # print(post.dict())
    post_dict = post.dict()  # storing value of pydantic object in variable
    # adding id field to post_dict for later retrival with a random number for uniqueness
    post_dict["id"] = randrange(1, 99999999)
    my_posts.append(post_dict)

    return {"post added": post_dict}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # will find for the index of the item that has the required ID
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exists :(")

    my_posts.pop(index)  # removed
    return {"message": f"ID {id} was removed from index {index}"}


@app.put("/posts/{id}")
# since we are receiving the same info from frontend, we wanna make sure it follows the right schema
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exists :(")
    post_dict = post.dict()
    # data received from the front end is converted and stored as dictionary
    post_dict['id'] = id
    my_posts[index] = post_dict

    return {"message": f"The post have be updated, new post is {post_dict} "}


"""
@app.post("/createposts")
def create_posts(
    new_post: dict = Body(...),
):  # catches all the fields from request body, converts them to dict and store in new_post
    print(new_post["Content"])
    print(new_post)
    return {"message": "Successfully created the post"}


"""
'''
@app.post("/createposts") #example of retrieving pydantic object and it's various attributes
def create_posts(new_post: Post):
    print(new_post.title)
    print(new_post.content)
    print(new_post.published)
    print(new_post.date)
    print(new_post)
    print(new_post.dict())
    return{"message": "Post with body received and successfully created"}
'''
