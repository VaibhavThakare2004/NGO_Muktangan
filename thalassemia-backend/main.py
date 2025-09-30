from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from datetime import datetime

app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/img_collarge", StaticFiles(directory="img_collarge"), name="img_collarge")
app.mount("/js", StaticFiles(directory="js"), name="js")

# Templates for FastAPI routes only (Thalassemia detection)
templates = Jinja2Templates(directory="templates")

# Your SheetDB URL
SHEETDB_URL = "https://sheetdb.io/api/v1/szpu493oaui2j"

# Root route - serve main index.html from root
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

# Serve other static pages from root
@app.get("/about", response_class=HTMLResponse)
async def about():
    with open("about.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/contact", response_class=HTMLResponse)
async def contact():
    with open("contact.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/donate", response_class=HTMLResponse)
async def donate():
    with open("donate.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/projects", response_class=HTMLResponse)
async def projects():
    with open("projects.html", "r") as f:
        return HTMLResponse(content=f.read())

# Thalassemia form route - uses templates
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
    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate CBC indices
    mentzer, shine_lal, srivastava, green_king = calculate_indices(hb, rbc, mcv, mch, mchc, rdw)
    prediction = predict_thalassemia(mentzer, mcv, mch)

    # Prepare data for SheetDB
    data = {
        "data": {
            "Timestamp": timestamp,
            "Name": name,
            "Phone": phone,
            "Email": email,
            "Hb": hb,
            "RBC": rbc,
            "MCV": mcv,
            "MCH": mch,
            "MCHC": mchc,
            "RDW": rdw,
            "Mentzer": mentzer,
            "Shine_Lal": shine_lal,
            "Srivastava": srivastava,
            "Green_King": green_king,
            "Prediction": prediction
        }
    }

    # POST to SheetDB
    try:
        requests.post(SHEETDB_URL, json=data)
    except Exception as e:
        print(f"Error posting to SheetDB: {e}")

    # Render result page from templates
    return templates.TemplateResponse("result.html", {
        "request": request,
        "timestamp": timestamp,
        "name": name,
        "phone": phone,
        "email": email,
        "hb": hb,
        "rbc": rbc,
        "mcv": mcv,
        "mch": mch,
        "mchc": mchc,
        "rdw": rdw,
        "mentzer": mentzer,
        "shine_lal": shine_lal,
        "srivastava": srivastava,
        "green_king": green_king,
        "prediction": prediction
    })

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