from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime
from utils import calculate_indices, predict_thalassemia

app = FastAPI()

# Templates inside 'templates/' folder (for thalassemia pages)
templates = Jinja2Templates(directory="templates")

# Template outside, in project root (for main index.html)
root_templates = Jinja2Templates(directory=".")

# Your SheetDB URL
SHEETDB_URL = "https://sheetdb.io/api/v1/szpu493oaui2j"

# ----------------------
# Routes
# ----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Main homepage route (index.html outside templates folder)
    """
    return root_templates.TemplateResponse("index.html", {"request": request})


@app.get("/thalassemia", response_class=HTMLResponse)
async def thalassemia_page(request: Request):
    """
    Thalassemia detector page
    """
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
    """
    Handles form submission from Thalassemia_detection.html
    """
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

    # POST to SheetDB (adds a row automatically)
    requests.post(SHEETDB_URL, json=data)

    # Render result page
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
