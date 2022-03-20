from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
#SECRET_KEY
#Algorithm
#Expiration time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes  #60 minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})  #updating the 'to_encode' dictionary

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        #if the function is able to decode the jwt with given parameters, it is deemed verified(not tempered with) otherwise Exception
        id: str = payload.get('user_id')
        print(id)
        #validating 'id' to be string
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
        #storing data in the variable as per the return token schema with 'id' extracted out of payload
    except:
        raise JWTError
    return token_data


#get_user function can be used to as Dependency in any of the path operations. That way those path operations
#would only be accessed if they qualify with a valid token
#It will take the token from hte request automatically  , extract the 'user id', will verify the token is correct by calling verify token. If it's not valid, then user_id would not be extracted and exception will be raised pointing to a unverified token


#anytime a specific endpoint needs to be protected, that means the user needs to be login to use it, following function in that path operation can be passed as Dependency. This is basically ensuring that all the path operation's code is executed. If this dependency is there, it is only executed in case of valid token returning a user id. Thus effectively verify a logged in user. Non verified user would have exception, leading to path operation not have all dependencies run properly and unable to proceed further.
def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    token_info = verify_access_token(token, credentials_exception)

    user = db.query(
        models.User).filter(models.User.id == token_info.id).first()

    #print(user.email)
    return user  #returning the entire user model object
