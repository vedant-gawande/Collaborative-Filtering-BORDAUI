from fastapi import FastAPI
# import uvicorn
from routers import start_menu
from fastapi.staticfiles import StaticFiles
from database import Base,engine

app = FastAPI()


app.include_router(start_menu.router)

app.mount("/static", StaticFiles(directory= "static"), name="static",)

Base.metadata.create_all(engine)

# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1')