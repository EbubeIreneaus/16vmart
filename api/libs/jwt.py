import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from settings import setting
from fastapi import HTTPException, status


HASH_ALG="HS256"

def encode(data: dict) ->str:
    token = jwt.encode(data, setting.JWT_SECRET,algorithm=HASH_ALG)
    return token


def decode(token:str):
    try:
        data = jwt.decode(token, setting.JWT_SECRET,algorithms=[HASH_ALG])
        return data
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
    except ExpiredSignatureError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
