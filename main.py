from fastapi import FastAPI
# import uvicorn
from routers import start_menu,verify,admin
from fastapi.staticfiles import StaticFiles
from database import Base,engine

app = FastAPI()


app.mount("/static", StaticFiles(directory= "static"), name="static",)

Base.metadata.create_all(bind=engine)

app.include_router(start_menu.router)
app.include_router(verify.router)
app.include_router(admin.router)


# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1')