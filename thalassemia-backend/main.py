from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# Templates setup - PRODUCTION READY
if os.getenv('FLY_APP_NAME'):
    # Production on Fly.io
    templates = Jinja2Templates(directory="/app/thalassemia-backend/templates")
else:
    # Development
    templates = Jinja2Templates(directory="templates")

# Mount static files for production
if os.getenv('FLY_APP_NAME'):
    # Production - serve from templates directory
    app.mount("/static", StaticFiles(directory="/app/thalassemia-backend/templates"), name="static")
    print("✅ Production: Static files mounted from /app/thalassemia-backend/templates")
else:
    # Development - original setup
    static_dirs = {
        "/css": "css",
        "/img": "img", 
        "/img_collarge": "img_collarge",
        "/js": "js"
    }

    for route, dir_name in static_dirs.items():
        possible_paths = [
            os.path.join(CURRENT_DIR, dir_name),
            os.path.join(PARENT_DIR, dir_name),
            dir_name
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                app.mount(route, StaticFiles(directory=path), name=dir_name)
                print(f"Mounted {route} from {path}")
                break
        else:
            print(f"Warning: Directory {dir_name} not found")
    
    # Serve CSS/JS from templates directory for development
    app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Your SheetDB URL
SHEETDB_URL = "https://sheetdb.io/api/v1/szpu493oaui2j"

# Helper function to find HTML files
def get_html_file(filename):
    if os.getenv('FLY_APP_NAME'):
        # Production paths
        possible_paths = [
            os.path.join("/app", filename),
            os.path.join("/app/thalassemia-backend/templates", filename),
            filename
        ]
    else:
        # Development paths
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
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Home page not found", status_code=404)

@app.get("/about", response_class=HTMLResponse)
async def about():
    file_path = get_html_file("about.html")
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="About page not found", status_code=404)

@app.get("/contact", response_class=HTMLResponse)
async def contact():
    file_path = get_html_file("contact.html")
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Contact page not found", status_code=404)

@app.get("/donate", response_class=HTMLResponse)
async def donate():
    file_path = get_html_file("donate.html")
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Donate page not found", status_code=404)

@app.get("/projects", response_class=HTMLResponse)
async def projects():
    file_path = get_html_file("projects.html")
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Projects page not found", status_code=404)

# Thalassemia form route
@app.get("/thalassemia", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("Thalassemia_detection.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    # Personal Information
    name: str = Form(...),
    whatsapp: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    address: str = Form(...),
    caste: str = Form(...),
    religion: str = Form(...),
    # Medical History
    bloodWithin3Months: str = Form(None),
    bloodMoreThan2Times: str = Form(None),
    fatigue: str = Form(None),
    breathless: str = Form(None),
    illFrequently: str = Form(None),
    familyHistory: str = Form(None),
    # CBC Parameters
    hb: float = Form(...),
    hct: float = Form(...),
    rbc: float = Form(...),
    wbc: float = Form(...),
    platelet: float = Form(...),
    mcv: float = Form(...),
    mch: float = Form(...),
    mchc: float = Form(...),
    rdwcv: float = Form(...),
    rdwsd: float = Form(...),
    mpv: float = Form(...),
    pdw: float = Form(...),
    plcr: float = Form(...),
    pct: float = Form(...),
    plcc: float = Form(...),
    # Differential Count
    neutrophils: float = Form(...),
    eosinophils: float = Form(...),
    basophils: float = Form(...),
    lymphocytes: float = Form(...),
    monocytes: float = Form(...)
):
    # Timestamp
    timestamp = f'"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"'
    print(f"🕐 DEBUG - Timestamp: {timestamp}")

    # Calculate CBC indices and prediction
    mentzer, shine_lal, srivastava, green_king = calculate_indices(hb, rbc, mcv, mch, mchc, rdwcv)
    prediction = predict_thalassemia(mentzer, mcv, mch)

    # ✅ STEP 1: SEND EMAIL TO PATIENT (Python version)
    print("📧 Attempting to send email to patient...")
    try:
        email_data = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "whatsapp": whatsapp,
            "hb": hb,
            "rbc": rbc,
            "mcv": mcv,
            "mch": mch,
            "mchc": mchc,
            "rdwcv": rdwcv
        }
        
        email_result = send_python_email(email_data)
        
        if email_result['success']:
            print("✅ Email sent successfully to patient!")
            print(f"📋 Screening Result: {email_result.get('screening_result', 'N/A')}")
        else:
            print(f"❌ Email sending failed: {email_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 Email sending exception: {str(e)}")

    # ✅ STEP 2: SAVE TO GOOGLE SHEETS
    print("🔄 Attempting to save to SheetDB...")
    
    # Prepare data for SheetDB
    data = {
        "data": {
            # Personal Information
            "Timestamp": timestamp,
            "Name": name,
            "WhatsApp": whatsapp,
            "Email": email,
            "Age": age,
            "Sex": sex,
            "Address": address,
            "Caste": caste,
            "Religion": religion,
            # Medical History
            "BloodWithin3Months": bloodWithin3Months,
            "BloodMoreThan2Times": bloodMoreThan2Times,
            "Fatigue": fatigue,
            "Breathless": breathless,
            "IllFrequently": illFrequently,
            "FamilyHistory": familyHistory,
            # CBC Parameters
            "Hb": hb,
            "HCT": hct,
            "RBC": rbc,
            "WBC": wbc,
            "Platelet": platelet,
            "MCV": mcv,
            "MCH": mch,
            "MCHC": mchc,
            "RDWCV": rdwcv,
            "RDWSD": rdwsd,
            "MPV": mpv,
            "PDW": pdw,
            "PLCR": plcr,
            "PCT": pct,
            "PLCC": plcc,
            # Differential Count
            "Neutrophils": neutrophils,
            "Eosinophils": eosinophils,
            "Basophils": basophils,
            "Lymphocytes": lymphocytes,
            "Monocytes": monocytes,
            # Calculated Indices
            "Mentzer": mentzer,
            "Shine_Lal": shine_lal,
            "Srivastava": srivastava,
            "Green_King": green_king,
            "Prediction": prediction
        }
    }

    # POST to SheetDB
    try:
        response = requests.post(SHEETDB_URL, json=data)
        print(f"📡 SheetDB Response Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Data saved to Google Sheet!")
        elif response.status_code == 422:
            print("❌ ERROR 422: Column mismatch in Google Sheet")
        else:
            print(f"❌ ERROR {response.status_code}: SheetDB API issue")
            
    except Exception as e:
        print(f"💥 SheetDB Exception: {str(e)}")

    # ✅ STEP 3: RETURN RESULT PAGE (Simple thank you)
    return templates.TemplateResponse("result.html", {
        "request": request
        # No data parameters needed for simple thank you page
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

# Python Email Function
def send_python_email(form_data):
    try:
        # 🔥 REPLACE THIS WITH YOUR ACTUAL GODADDY PASSWORD 🔥
        smtp_server = "smtpout.secureserver.net"
        port = 587
        username = "drabhijeet@muktanganfoundation.org"
        password = "Abhijeet@2025"  # ← REPLACE THIS
        
        # Calculate Thalassemia result
        mcv = float(form_data.get('mcv', 0))
        mch = float(form_data.get('mch', 0))
        rbc = float(form_data.get('rbc', 1))
        
        mentzer = mcv / rbc if rbc > 0 else 0
        
        # Thalassemia detection logic
        conditions = [
            mentzer < 13,
            mcv < 80,
            mch < 27
        ]
        positive_count = sum(conditions)
        
        if positive_count >= 2:
            result_text = "🟡 LIKELY THALASSEMIA MINOR"
            recommendation = "This screening suggests possible Thalassemia Minor. Please consult a hematologist for confirmatory testing including Hb electrophoresis."
        elif mentzer < 13:
            result_text = "🟡 POSSIBLE THALASSEMIA MINOR" 
            recommendation = "This may indicate Thalassemia Minor. Please consult a hematologist for further evaluation and family screening."
        else:
            result_text = "✅ NOT SUGGESTIVE OF THALASSEMIA MINOR"
            recommendation = "Your screening does not suggest Thalassemia Minor. However, clinical correlation with symptoms is advised."
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = 'Dr. Abhijeet - Muktangan Foundation <drabhijeet@muktanganfoundation.org>'
        msg['To'] = form_data['email']
        msg['Subject'] = f"Hematology Screening Results - {form_data['name']}"
        
        body = f"""Dear {form_data['name']},

Please find your hematology screening results below:

PATIENT INFORMATION:
- Name: {form_data['name']}
- Age: {form_data.get('age', 'N/A')} years
- Sex: {form_data.get('sex', 'N/A')}
- Contact: {form_data.get('whatsapp', 'N/A')}

SCREENING RESULT:
{result_text}

INTERPRETATION NOTES:
- Mentzer Index < 13 suggests Thalassemia
- MCV < 80 fL indicates Microcytosis
- MCH < 27 pg indicates Hypochromia
- This is a screening tool - consult a hematologist for definitive diagnosis

RECOMMENDATION:
{recommendation}

Please contact us if you have any questions.

Sincerely,
Dr. Abhijeet
Muktangan Foundation
drabhijeet@muktanganfoundation.org"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        return {"success": True, "message": "Email sent successfully", "screening_result": result_text}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Catch-all route for undefined paths
@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    return HTMLResponse(content="Page not found", status_code=404)