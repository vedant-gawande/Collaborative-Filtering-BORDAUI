from fastapi import FastAPI
# import uvicorn
from routers import start_menu
from fastapi.staticfiles import StaticFiles


app = FastAPI()


app.include_router(start_menu.router)

app.mount("/static", StaticFiles(directory= "static"), name="static",)

# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1')