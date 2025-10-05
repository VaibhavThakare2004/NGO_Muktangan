from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import requests
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.responses import FileResponse
import os


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
    hct: Optional[float] = None
    rbc: float
    wbc: Optional[float] = None
    platelet: Optional[float] = None
    mcv: float
    mch: float
    mchc: float
    rdwcv: float
    rdwsd: float
    mpv: Optional[float] = None
    pdw: Optional[float] = None
    plcr: Optional[float] = None
    pct: Optional[float] = None
    plcc: Optional[float] = None
    
    # Differential Count
    neutrophils: Optional[float] = None
    eosinophils: Optional[float] = None
    basophils: Optional[float] = None
    lymphocytes: Optional[float] = None
    monocytes: Optional[float] = None

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

# ✅ Email function
def send_python_email(form_data):
    try:
        smtp_server = "smtpout.secureserver.net"
        port = 587
        username = os.environ.get('SMTP_USERNAME', 'drabhijeet@muktanganfoundation.org')
        password = os.environ.get('SMTP_PASSWORD', 'Abhijeet@2025')
        
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
        
        # SMTP connection
        try:
            server = smtplib.SMTP(smtp_server, port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            return {"success": True, "message": "Email sent successfully", "screening_result": result_text}
            
        except smtplib.SMTPException:
            # Try alternative port 465 with SSL
            try:
                server = smtplib.SMTP_SSL('smtpout.secureserver.net', 465, timeout=15)
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                return {"success": True, "message": "Email sent successfully", "screening_result": result_text}
            except Exception as ssl_error:
                return {"success": False, "error": f"SMTP failed: {ssl_error}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ✅ SUBMIT ENDPOINT - Returns HTML Thank You Page
@app.post("/submit")
async def submit_form(patient_data: PatientData):
    try:
        print(f"🔄 Processing submission for: {patient_data.name}")
        
        # Calculate indices and prediction
        mentzer, shine_lal, srivastava, green_king = calculate_indices(
            patient_data.hb, patient_data.rbc, patient_data.mcv, 
            patient_data.mch, patient_data.mchc, patient_data.rdwcv
        )
        
        prediction = predict_thalassemia(mentzer, patient_data.mcv, patient_data.mch)
        
        # Prepare data for email and sheets
        form_data_dict = patient_data.dict()
        form_data_dict.update({
            "mentzer": mentzer,
            "prediction": prediction
        })
        
        # ✅ Send email
        email_result = send_python_email(form_data_dict)
        
        # ✅ Save to Google Sheets - Using Indian Standard Time
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_time = datetime.now(ist_timezone)
        timestamp = f'"{ist_time.strftime("%Y-%m-%d %H:%M:%S IST")}"'
        
        sheets_data = {
            "data": {
                # Personal Information
                "Timestamp": timestamp,
                "Name": patient_data.name,
                "WhatsApp": patient_data.whatsapp,
                "Email": patient_data.email,
                "Age": patient_data.age,
                "Sex": patient_data.sex,
                "Address": patient_data.address,
                "Caste": patient_data.caste,
                "Religion": patient_data.religion,
                # Medical History
                "BloodWithin3Months": patient_data.bloodWithin3Months,
                "BloodMoreThan2Times": patient_data.bloodMoreThan2Times,
                "Fatigue": patient_data.fatigue,
                "Breathless": patient_data.breathless,
                "IllFrequently": patient_data.illFrequently,
                "FamilyHistory": patient_data.familyHistory,
                # CBC Parameters
                "Hb": patient_data.hb,
                "HCT": patient_data.hct,
                "RBC": patient_data.rbc,
                "WBC": patient_data.wbc,
                "Platelet": patient_data.platelet,
                "MCV": patient_data.mcv,
                "MCH": patient_data.mch,
                "MCHC": patient_data.mchc,
                "RDWCV": patient_data.rdwcv,
                "RDWSD": patient_data.rdwsd,
                "MPV": patient_data.mpv,
                "PDW": patient_data.pdw,
                "PLCR": patient_data.plcr,
                "PCT": patient_data.pct,
                "PLCC": patient_data.plcc,
                # Differential Count
                "Neutrophils": patient_data.neutrophils,
                "Eosinophils": patient_data.eosinophils,
                "Basophils": patient_data.basophils,
                "Lymphocytes": patient_data.lymphocytes,
                "Monocytes": patient_data.monocytes,
                # Calculated Indices
                "Mentzer": mentzer,
                "Shine_Lal": shine_lal,
                "Srivastava": srivastava,
                "Green_King": green_king,
                "Prediction": prediction
            }
        }
        
        # Send to SheetDB
        sheets_response = requests.post(SHEETDB_URL, json=sheets_data, timeout=10)
        sheets_success = sheets_response.status_code == 201
        
        # ✅ Read and return the thankyou.html file content directly as HTML response
        try:
            with open("thankyou.html", "r", encoding="utf-8") as file:
                html_content = file.read()
            return HTMLResponse(content=html_content, status_code=200)
        except FileNotFoundError:
            # Fallback to inline HTML if file not found
            fallback_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thank You - Thalassemia CBC Predictor</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #8B5CF6, #DDD6FE); }
                    .container { background: white; padding: 40px; border-radius: 20px; max-width: 400px; margin: 0 auto; }
                    .success-icon { font-size: 60px; color: #10B981; margin-bottom: 20px; }
                    h1 { color: #8B5CF6; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <h1>Thank You!</h1>
                    <p>Your form has been successfully submitted.</p>
                    <p>You will receive your screening results via email shortly.</p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=fallback_html, status_code=200)
        
    except Exception as e:
        print(f"💥 API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ✅ Health check endpoint
@app.get("/")
async def health_check():
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.now(ist_timezone)
    return {
        "status": "healthy", 
        "service": "Thalassemia Predictor API",
        "timestamp": ist_time.isoformat()
    }

# ✅ For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
