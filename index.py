from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uvicorn
import json  # added
from fastapi.middleware.cors import CORSMiddleware  # added

load_dotenv()

app = FastAPI()

# Add CORS middleware (allow all origins, methods, headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
GEN_CONFIG = {  # added: force JSON and reduce creativity
    "response_mime_type": "application/json",
    "temperature": 0
}

# Body of the incoming request
class ImageRequest(BaseModel):
    image: str  
    filename: str
    mimetype: str

@app.post("/process-image")
async def process_image(data: ImageRequest):
    try:
        # Basic validation
        if not data.mimetype or not data.mimetype.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid or unsupported mimetype")

        try:
            image_bytes = base64.b64decode(data.image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")

        # Hardened prompt: classification + extraction with strict JSON output only
        prompt = """
You are given an image that may or may not be a certificate issued to a person.
Task:
1) Decide if the image is a certificate (training/completion/award/experience/etc.).
2) If yes, extract:
   - company: Issuing organization/company name as printed.
   - candidate: Recipient's name as printed.
3) If no or unsure, mark it as not a certificate.

Rules:
- Do NOT guess; if uncertain or text unreadable, isCertificate must be false.
- If isCertificate is false, set company and candidate to null.
- Return ONLY a single JSON object with these keys exactly:
  {
    "isCertificate": boolean,
    "confidence": number between 0 and 1,
    "company": string or null,
    "candidate": string or null
  }
- No extra text, no explanations, no additional keys.
"""

        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": data.mimetype,
                    "data": image_bytes
                }
            ],
            generation_config=GEN_CONFIG
        )

        if not getattr(response, "text", None):
            raise HTTPException(status_code=502, detail="Empty response from model")

        try:
            model_json = json.loads(response.text.strip())
        except Exception:
            # Log the unexpected model output for debugging
            print("Unexpected model output:", response.text)
            raise HTTPException(status_code=502, detail="Model returned unexpected format")

        is_cert = bool(model_json.get("isCertificate"))
        confidence = float(model_json.get("confidence") or 0)
        company = (model_json.get("company") or "") if model_json.get("company") is not None else ""
        candidate = (model_json.get("candidate") or "") if model_json.get("candidate") is not None else ""

        # Sanity checks for verified result
        def _is_valid_text(s: str) -> bool:
            return isinstance(s, str) and 1 <= len(s.strip()) <= 150

        if not is_cert or confidence < 0.6 or not (_is_valid_text(company) and _is_valid_text(candidate)):
            return {
                "status": "unverified",
                "reason": "Image is not a certificate or confidence too low"
            }

        # Verified
        return {
            "Company": company.strip(),
            "Candidate": candidate.strip(),
            "status": "verified"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to process image")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # use PORT if defined, else 5000
    uvicorn.run("index:app", host="127.0.0.1", port=port, reload=True)