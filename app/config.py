#holds code for accessing and validating env. variables
from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    #settings default values to the environment variable which the pydantic library will perform validation on
    #if no default value was provided, pydantic lib. will look for the system variable with similar name and obtain the value. If there is no such sys variable, it will raise a value_error.missing, So it is a way to access and validate the env. variables stored on the system.
    #every env variable is read as a string.
    #these variable would be required to set on the env variables on the machine (in production) but in development we can just use .env file and set all the variables there. This is way easier.
    #The convention is to name variables all cap. Pydantic accesses these variables from a case insensitive perspective, so using lower case here and upper case in .env file should not raise any issues.

    class Config:
        env_file = ".env"

    #setting up pydantic to look for env variables in .env file


settings = Settings()