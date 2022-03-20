from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['authentication'])


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):
    #so instead of doing, user_credentials = schemas.UserLogin, fastapi provides a built in built in schema
    #however the fields of this built in schema are { 'username ': blahblah , 'password':'blahblah'}
    #also input from postman comes as 'form' rather than 'raw'

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No user with email : {user_credentials.username} found")

    #now we need to hash the provided password and compare to the hashed on the database, what accomplish that in utils

    if not utils.verify(user_credentials.password, user.password):
        #sending plain received password and hashed password from the database
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Incorrect credentials")

    access_token = oauth2.create_access_token(data={'user_id': user.id})
    #just passing user_id as the data to the token creator, can pass more stuff

    return {"access_token": access_token, "token_type": "bearer"}
