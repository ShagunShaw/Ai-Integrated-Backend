from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uvicorn


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Body of the incoming request
class ImageRequest(BaseModel):
    image: str  
    filename: str
    mimetype: str

@app.post("/process-image")
async def process_image(data: ImageRequest):
    try:
        image_bytes = base64.b64decode(data.image)

        prompt = "Extract only the company name and candidate name from the certificate. give the output in one line only separated by a comma and no other punctuation. If there is no certificate available, then just return NONE and nothing else."

        response = model.generate_content([
            prompt,
            {
                "mime_type": data.mimetype,
                "data": image_bytes
            }
        ])


        if(response.text.strip().upper() == "NONE"):
            res= {"status": "not verified", "response": response.text.strip().upper()}
            return res

        text= response.text.split(",")
        jsonResponse = {
            "Company": text[0].strip(),
            "Candidate": text[1].strip(),
            "status": "verified"
        }

        return jsonResponse

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use PORT if defined, else 5000
    uvicorn.run("index:app", host="0.0.0.0", port=port, reload=True)