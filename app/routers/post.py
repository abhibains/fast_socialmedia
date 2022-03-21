from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db



router = APIRouter(
    prefix="/posts", tags=['Posts']
)  #because /posts always occurs, so we can just include it in prefix and remove /posts from our routes
#tags helps create different groups for the documentation


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              get_current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    #int validation does nothing ji
    #query parameter, sent as ?limit=14orWhatever from postman
    #print(f"USER HEGA {get_current_user.email}")
    #print(skip)
    posts_db = db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    #query parameter limit decides the number of posts user sees, and query parameter skip, skips first n values
    results = db.query(models.Post,
                       func.count(
                           models.Vote.post_id).label('Vote_Count')).join(
                               models.Vote,
                               models.Vote.post_id == models.Post.id,
                               isouter=True).group_by(models.Post.id).all()
    # count has a column that is non null to avoid being those rows being counted
    print(results)  #print the raw SQL to understand the underlying SQL query
    #return posts_db  #fastapi will automatically serialise the output and convert it into json
    return results


# obtaining specific posts, {id} field is called path parameter. Fastapi will automatically extract this id
@router.get("/{id}", response_model=schemas.Post)
# validating that the value received is int and not string. If string, the value is then converted
def get_post(id: int,
             response_code: Response,
             db: Session = Depends(get_db),
             get_current_user: int = Depends(oauth2.get_current_user)):
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
@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.Post)
# post : Post ensures that data received is being validated against the Post class
def create_posts(post: schemas.PostCreate,
                 db: Session = Depends(get_db),
                 get_current_user: int = Depends(oauth2.get_current_user)):
    #fields can be populated using the dict() function for pydantic object 'post' and it's unpacking feature( ** )
    #this way no manual field generation is required like in the ''' comment below
    #print(post.dict())
    newpost_db = models.Post(
        owner_id=get_current_user.id, **post.dict()
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                db: Session = Depends(get_db),
                get_current_user: int = Depends(oauth2.get_current_user)):
    #this dependency forces user to be logged in to perform any action
    deleted_db = db.query(models.Post).filter(models.Post.id == id)
    #filter is involved everytime with id
    # this is just the query which is not run yet on DB, .all or .first make it run
    post = deleted_db.first()
    if not deleted_db.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exists :(",
        )
    #print(f"get current user {get_current_user.email}")
    if post.owner_id != get_current_user.id:  #checking if post owner id matches with user who's logged in
        #if this is some other user trying to delete someone's post
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform the requested action")

    deleted_db.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
# since we are receiving the same info from frontend, we wanna make sure it follows the right schema
def update_post(id: int,
                update_post: schemas.PostCreate,
                db: Session = Depends(get_db),
                get_current_user: int = Depends(oauth2.get_current_user)):

    query = db.query(models.Post).filter(models.Post.id == id)
    post_query = query.first()
    if post_query == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exists :(")

    if post_query.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    query.update(update_post.dict(), synchronize_session=False)
    # update takes a dictionary, so we do not need to unpack
    #similar to query.update({'title':'updated title', 'content':'new content!!'}, 'published':true)}, synchronize_session = False)
    db.commit()
    return query.first()  #since commit has alr
