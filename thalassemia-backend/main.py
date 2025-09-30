from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from datetime import datetime
import os

app = FastAPI()

# Get current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# Mount static files only if directories exist
static_dirs = {
    "/css": "css",
    "/img": "img", 
    "/img_collarge": "img_collarge",
    "/js": "js"
}

for route, dir_name in static_dirs.items():
    # Check both current directory and parent directory
    possible_paths = [
        os.path.join(CURRENT_DIR, dir_name),
        os.path.join(PARENT_DIR, dir_name),
        dir_name  # relative path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            app.mount(route, StaticFiles(directory=path), name=dir_name)
            print(f"Mounted {route} from {path}")
            break
    else:
        print(f"Warning: Directory {dir_name} not found")

# Templates for FastAPI routes
templates = Jinja2Templates(directory="templates")

# Your SheetDB URL
SHEETDB_URL = "https://sheetdb.io/api/v1/szpu493oaui2j"

# Helper function to find HTML files
def get_html_file(filename):
    possible_paths = [
        os.path.join(PARENT_DIR, filename),
        os.path.join(CURRENT_DIR, filename),
        filename
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Root route and other routes...
@app.get("/", response_class=HTMLResponse)
async def home():
    file_path = get_html_file("index.html")
    if file_path:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Home page not found", status_code=404)

@app.get("/about", response_class=HTMLResponse)
async def about():
    file_path = get_html_file("about.html")
    if file_path:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="About page not found", status_code=404)

@app.get("/contact", response_class=HTMLResponse)
async def contact():
    file_path = get_html_file("contact.html")
    if file_path:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Contact page not found", status_code=404)

@app.get("/donate", response_class=HTMLResponse)
async def donate():
    file_path = get_html_file("donate.html")
    if file_path:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Donate page not found", status_code=404)

@app.get("/projects", response_class=HTMLResponse)
async def projects():
    file_path = get_html_file("projects.html")
    if file_path:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Projects page not found", status_code=404)

# ... rest of your routes (thalassemia, submit) remain the same
@app.get("/thalassemia", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("Thalassemia_detection.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    hb: float = Form(...),
    rbc: float = Form(...),
    mcv: float = Form(...),
    mch: float = Form(...),
    mchc: float = Form(...),
    rdw: float = Form(...)
):
    # ... your submit function code
    pass

# Your utility functions
def calculate_indices(hb, rbc, mcv, mch, mchc, rdw):
    mentzer = mcv / rbc if rbc != 0 else 0
    shine_lal = (mcv ** 2 * mch) / 100 if mch != 0 else 0
    srivastava = mch / rbc if rbc != 0 else 0
    green_king = (mcv ** 2 * rdw) / (hb * 100) if hb != 0 else 0
    return round(mentzer,2), round(shine_lal,2), round(srivastava,2), round(green_king,2)

def predict_thalassemia(mentzer, mcv, mch):
    if mentzer < 13 or mcv < 80 or mch < 27:
        return "Likely Thalassemia Minor"
    else:
        return "Not Thalassemia Minor"