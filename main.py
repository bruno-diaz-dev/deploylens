from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_database
from routes.deployments import router as deployments_router


app = FastAPI()

app.include_router(deployments_router)


create_database()


app.mount(
    "/static",
    StaticFiles(directory="static") ,
    name="static"
)

templates = Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )