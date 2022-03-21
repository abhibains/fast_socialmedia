from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
router = APIRouter(prefix="/users", tags=['Users'])


@router.post(  #app keyword replaced with router
    "/",
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


@router.get("/{id}", response_model=schemas.UserOut)  #
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with id:{id} found")
    return user
