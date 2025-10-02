from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# ✅ Email function
def send_python_email(form_data):
    try:
        smtp_server = "smtpout.secureserver.net"
        port = 587
        username = "drabhijeet@muktanganfoundation.org"
        password = "Abhijeet@2025"
        
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
        
        # ✅ Save to Google Sheets
        timestamp = f'"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"'
        
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
        
        # ✅ Return HTML Thank You Page with updated style and removed button
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Thank You - Muktangan Foundation</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    position: relative;
                    overflow: hidden;
                }
                
                body::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: 
                        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
                    pointer-events: none;
                }
                
                .success-container {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    padding: 60px 50px;
                    border-radius: 24px;
                    box-shadow: 
                        0 25px 50px rgba(0, 0, 0, 0.15),
                        0 0 0 1px rgba(255, 255, 255, 0.1);
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                    position: relative;
                    z-index: 1;
                    animation: slideUp 0.8s ease-out;
                }
                
                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .success-icon {
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 30px;
                    box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% {
                        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
                    }
                    50% {
                        box-shadow: 0 10px 40px rgba(76, 175, 80, 0.5);
                    }
                    100% {
                        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
                    }
                }
                
                .success-icon::before {
                    content: '✓';
                    color: white;
                    font-size: 50px;
                    font-weight: bold;
                }
                
                h1 {
                    color: #2d3748;
                    font-size: 3rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .subtitle {
                    color: #4a5568;
                    font-size: 1.3rem;
                    font-weight: 500;
                    margin-bottom: 15px;
                    line-height: 1.5;
                }
                
                .message {
                    color: #718096;
                    font-size: 1.1rem;
                    line-height: 1.6;
                    margin-bottom: 40px;
                }
                
                .info-box {
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    border-radius: 16px;
                    padding: 25px;
                    margin-top: 30px;
                }
                
                .info-title {
                    color: #667eea;
                    font-weight: 600;
                    font-size: 1.1rem;
                    margin-bottom: 10px;
                }
                
                .info-text {
                    color: #4a5568;
                    font-size: 0.95rem;
                    line-height: 1.5;
                }
                
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(0, 0, 0, 0.1);
                    color: #718096;
                    font-size: 0.9rem;
                }
                
                @media (max-width: 600px) {
                    .success-container {
                        padding: 40px 30px;
                        margin: 10px;
                        border-radius: 20px;
                    }
                    
                    h1 {
                        font-size: 2.2rem;
                    }
                    
                    .subtitle {
                        font-size: 1.1rem;
                    }
                    
                    .success-icon {
                        width: 80px;
                        height: 80px;
                    }
                    
                    .success-icon::before {
                        font-size: 40px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="success-container">
                <div class="success-icon"></div>
                <h1>Thank You!</h1>
                <p class="subtitle">Your form has been successfully submitted.</p>
                <p class="message">We appreciate your participation in our Thalassemia screening program.</p>
                
                <div class="info-box">
                    <div class="info-title">📧 Next Steps</div>
                    <div class="info-text">
                        You will receive your screening results via email shortly. 
                        Please check your inbox and spam folder.
                    </div>
                </div>
                
                <div class="footer">
                    <strong>Muktangan Foundation</strong><br>
                    Healthcare & Medical Screening Services
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"💥 API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ✅ Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Thalassemia Predictor API",
        "timestamp": datetime.now().isoformat()
    }

# ✅ For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)