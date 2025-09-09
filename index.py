from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure the Gemini model
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Request body model
class ImageRequest(BaseModel):
    image: str  # base64 string
    filename: str
    mimetype: str

@app.post("/process-image")
async def process_image(data: ImageRequest):
    try:
        image_bytes = base64.b64decode(data.image)

        # You can also ask a custom question here:
        prompt = "Extract only the company name and candidate name from the certificate. give the output in one line only separated by a comma and no other punctuation."

        response = model.generate_content([
            prompt,
            {
                "mime_type": data.mimetype,
                "data": image_bytes
            }
        ])

        return {"response": response.text}

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to process image")