from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vote", tags=['Vote'])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,
         db: Session = Depends(database.get_db),
         current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id : {vote.post_id} does not exist")
    #frJ2s2JHjP
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )  #two checks to make sure that the vote for the specific post by the specific user(think composite key)
    found_vote = vote_query.first()

    if (vote.dir == 1
        ):  # vote dir =1 means user wants to vote on the specific post
        if found_vote:  #if there exist a row with user id and post it matching, means he liked post previously
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=
                f"user {current_user.id} has already voted on post witb id  {vote.post_id}"
            )
        new_vote = models.Vote(  #this is outside if, which means if user wants to vote and no previous vote exist
            post_id=vote.post_id,
            user_id=current_user.id)  # new vote created if no vote found
        db.add(new_vote)
        db.commit()
        return {"message": "Vote added ji"}
    else:  #else part is when dir =0, when user wants to remove vote from a previously liked vote
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Vote does not exist")
        vote_query.delete(
            synchronize_session=False
        )  # if a previously liked/voted entry found, delete it
        db.commit()
        return {"message": "successfully deleted vote"}
