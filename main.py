from fastapi import FastAPI,Request,HTTPException
# import uvicorn
from routers import start_menu,verify,admin,user
from fastapi.staticfiles import StaticFiles
from database import Base,engine
from fastapi.responses import HTMLResponse,Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class DesktopOnlyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get("User-Agent")
        if not user_agent or "mobile" in user_agent.lower() or "android" in user_agent.lower() or "ios" in user_agent.lower():
            with open("templates/desktop_only.html") as f:
                content = f.read()
            return Response(content=content, status_code=200)
        response = await call_next(request)
        return response

app = FastAPI(max_upload_size = 50*1024*1024)
app.add_middleware(DesktopOnlyMiddleware)


app.mount("/static", StaticFiles(directory= "static"), name="static",)

Base.metadata.create_all(bind=engine)

app.include_router(start_menu.router)
app.include_router(verify.router)
app.include_router(admin.router)
app.include_router(user.router)


@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def handle_exception(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        with open("templates/no_token.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=404)
    elif exc.status_code == 404:
        with open("templates/page_not_found.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        with open("templates/Internal_server_error.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)

# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1')