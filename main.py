from fastapi import FastAPI
# import uvicorn
from routers import admin
from fastapi.staticfiles import StaticFiles


app = FastAPI()


app.include_router(admin.router)

app.mount("/static", StaticFiles(directory= "static"), name="static",)

# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1')