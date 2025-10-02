from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize FastAPI app
app = FastAPI(title="Thalassemia Predictor API", version="1.0.0")

# ✅ Configure CORS for GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your SheetDB URL
SHEETDB_URL = "https://sheetdb.io/api/v1/szpu493oaui2j"

# ✅ Pydantic Model for API Validation
class PatientData(BaseModel):
    # Personal Information
    name: str
    whatsapp: str
    email: str
    age: int
    sex: str
    address: str
    caste: str
    religion: str
    
    # Medical History (Optional)
    bloodWithin3Months: Optional[str] = None
    bloodMoreThan2Times: Optional[str] = None
    fatigue: Optional[str] = None
    breathless: Optional[str] = None
    illFrequently: Optional[str] = None
    familyHistory: Optional[str] = None
    
    # CBC Parameters
    hb: float
    hct: float
    rbc: float
    wbc: float
    platelet: float
    mcv: float
    mch: float
    mchc: float
    rdwcv: float
    rdwsd: float
    mpv: float
    pdw: float
    plcr: float
    pct: float
    plcc: float
    
    # Differential Count
    neutrophils: float
    eosinophils: float
    basophils: float
    lymphocytes: float
    monocytes: float

# ✅ Utility functions
def calculate_indices(hb, rbc, mcv, mch, mchc, rdw):
    mentzer = mcv / rbc if rbc != 0 else 0
    shine_lal = (mcv ** 2 * mch) / 100 if mch != 0 else 0
    srivastava = mch / rbc if rbc != 0 else 0
    green_king = (mcv ** 2 * rdw) / (hb * 100) if hb != 0 else 0
    return round(mentzer, 2), round(shine_lal, 2), round(srivastava, 2), round(green_king, 2)

def predict_thalassemia(mentzer, mcv, mch):
    if mentzer < 13 or mcv < 80 or mch < 27:
        return "Likely Thalassemia Minor"
    else:
        return "Not Thalassemia Minor"

# ✅ Email function (unchanged)
def send_python_email(form_data):
    try:
        smtp_server = "smtpout.secureserver.net"
        port = 587
        username = "drabhijeet@muktanganfoundation.org"
        password = "Abhijeet@2025"
        
        mcv = float(form_data.get('mcv', 0))
        mch = float(form_data.get('mch', 0))
        rbc = float(form_data.get('rbc', 1))
        mentzer = mcv / rbc if rbc > 0 else 0
        
        conditions = [mentzer < 13, mcv < 80, mch < 27]
        positive_count = sum(conditions)
        
        if positive_count >= 2:
            result_text = "🟡 LIKELY THALASSEMIA MINOR"
            recommendation = "This screening suggests possible Thalassemia Minor. Please consult a hematologist for confirmatory testing."
        elif mentzer < 13:
            result_text = "🟡 POSSIBLE THALASSEMIA MINOR"
            recommendation = "This may indicate Thalassemia Minor. Please consult a hematologist."
        else:
            result_text = "✅ NOT SUGGESTIVE OF THALASSEMIA MINOR"
            recommendation = "Your screening does not suggest Thalassemia Minor."
        
        msg = MIMEMultipart()
        msg['From'] = 'Dr. Abhijeet - Muktangan Foundation <drabhijeet@muktanganfoundation.org>'
        msg['To'] = form_data['email']
        msg['Subject'] = f"Hematology Screening Results - {form_data['name']}"
        
        body = f"""Dear {form_data['name']},

PATIENT INFORMATION:
- Name: {form_data['name']}
- Age: {form_data.get('age', 'N/A')} years
- Sex: {form_data.get('sex', 'N/A')}
- Contact: {form_data.get('whatsapp', 'N/A')}

SCREENING RESULT:
{result_text}

RECOMMENDATION:
{recommendation}

Sincerely,
Dr. Abhijeet
Muktangan Foundation
"""
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, port, timeout=15)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return {"success": True, "message": "Email sent successfully", "screening_result": result_text}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ✅ SUBMIT ENDPOINT - now serving external thankyou.html
@app.post("/submit")
async def submit_form(patient_data: PatientData):
    try:
        print(f"🔄 Processing submission for: {patient_data.name}")
        
        # Calculate indices + prediction
        mentzer, shine_lal, srivastava, green_king = calculate_indices(
            patient_data.hb, patient_data.rbc, patient_data.mcv, 
            patient_data.mch, patient_data.mchc, patient_data.rdwcv
        )
        prediction = predict_thalassemia(mentzer, patient_data.mcv, patient_data.mch)
        
        # Save data to Google Sheets
        sheets_data = {"data": {"Name": patient_data.name, "Mentzer": mentzer, "Prediction": prediction}}
        requests.post(SHEETDB_URL, json=sheets_data, timeout=10)
        
        # Send Email
        send_python_email(patient_data.dict())
        
        # ✅ Serve thankyou.html (must be in same folder as app.py)
        return FileResponse("thankyou.html", media_type="text/html")
    
    except Exception as e:
        print(f"💥 API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ✅ Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "Thalassemia Predictor API", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
