# pylint: disable=no-name-in-module
from fastapi import FastAPI
from . import models, oauth2
from .database import engine, SessionLocal
from .routers import post, user, auth, vote
from .config import Settings
from fastapi.middleware.cors import CORSMiddleware

# setting = Settings()
# print(setting.database_username)
#models.Base.metadata.create_all(bind=engine) #tells sqlalchemy to create all of the model tables
#since alembic is taking care of all the revision, it can be commented out
app = FastAPI()  # instance of fast api created
origins = ["*"]  #list of sites that are allowed  to talk to api
app.add_middleware(  #middleware is basically a function that runs before every request. A request to router first goes to middleware and then to the router
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)  # origin- list of domians allowed to talk to the api
"""
@app.get(
    "/"
)  # @ = python decorator, get= method, "/" = path or route path that comes after domain name of API, root()= function, entire block called path operation or just called route
def get_message():
    return {"message": "hello-world is this changing, this is without the autosave "}
"""
app.include_router(post.router)
#including the router from the 'post.py' in 'routers' folder. The control reaches here and then jumps to routers/post.py/ and looks for match
app.include_router(user.router)  #from .routers import post, user
#we separated all our apth operations into different files and then we make use of APIRouter and then include them in the main file
app.include_router(auth.router)

app.include_router(vote.router)
