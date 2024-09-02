# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from clients import router as clients_router

app = FastAPI()

# Mount static files for CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include the clients router
app.include_router(clients_router, prefix="/api")

# Root endpoint to serve the HTML page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
