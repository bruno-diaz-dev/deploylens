from email.charset import QP
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_database, get_connection
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

@app.get("/live")
def liveness():
    return {
        "status": "alive"
    }

@app.get("/ready")
def readyness():
    connection = None

    try:
        connection = get_connection()

        connection.execute(
            "SELECT 1 FROM deployments LIMIT 1"
        ).fetchone()

        return {
            "status": "ready",
            "database": "reachable"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Aplication not ready"
        )
    
    finally:
        if connection:
            connection.close()
