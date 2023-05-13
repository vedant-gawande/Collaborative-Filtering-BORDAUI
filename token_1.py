from fastapi import Request,status
from jose import JWTError, jwt
from repository.config import setting
from fastapi.responses import HTMLResponse

def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt

async def verify_token(request:Request) -> bool:
    token = request.cookies.get("access_token")
    with open("templates/no_token.html", "r") as f:
        content = f.read()
    try:
        # payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        # username: str = payload.get("sub")
        # if username is None:
        if not token:
            return HTMLResponse(content=content, status_code=403)
        return True
    except JWTError:
        with open("templates/Internal_server_error.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=401)
        
def get_token(request:Request):
    errors = []
    try:
        token = request.cookies.get("access_token")
        if token is None:
            errors.append("Kindly login first")
            return None,errors
        else:
            scheme, _ , param = token.partition(" ")
            payload = jwt.decode(param,setting.SECRET_KEY,algorithms=setting.ALGORITHM)
            return payload
    except Exception as e:
        print(e)
        