import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)










# Ilm-ul-Adad chart (simplified example)
adad_mapping = {
    'ا': 1, 'ب': 2, 'پ': 2, 'ت': 400, 'ٹ': 400, 'ث': 500,
    'ج': 3, 'چ': 3, 'ح': 8, 'خ': 600, 'د': 4, 'ڈ': 4,
    'ذ': 700, 'ر': 200, 'ز': 7, 'ژ': 7, 'س': 60, 'ش': 300,
    'ص': 90, 'ض': 800, 'ط': 9, 'ظ': 900, 'ع': 70, 'غ': 1000,
    'ف': 80, 'ق': 100, 'ک': 20, 'گ': 20, 'ل': 30, 'م': 40,
    'ن': 50, 'و': 6, 'ہ': 5, 'ء': 1, 'ی': 10, 'ے': 10
}

transliteration_mapping = {
    'ا': 'Alif', 'ب': 'Bay', 'پ': 'Pay', 'ت': 'Tay', 'ٹ': 'Tay', 'ث': 'Say',
    'ج': 'Jeem', 'چ': 'Chay', 'ح': 'Hay', 'خ': 'Khay', 'د': 'Daal', 'ڈ': 'Daal',
    'ذ': 'Zaal', 'ر': 'Ray', 'ز': 'Zay', 'ژ': 'Zhay', 'س': 'Seen', 'ش': 'Sheen',
    'ص': 'Saad', 'ض': 'Zaad', 'ط': 'Tay', 'ظ': 'Zay', 'ع': 'Ain', 'غ': 'Ghain',
    'ف': 'Fay', 'ق': 'Qaaf', 'ک': 'Kaaf', 'گ': 'Gaaf', 'ل': 'Laam', 'م': 'Meem',
    'ن': 'Noon', 'و': 'Waw', 'ہ': 'Hay', 'ء': 'Hamza', 'ی': 'Yay', 'ے': 'Yay'
}




API_Key = os.getenv("API_Key")
print(API_Key)
if not API_Key:
    raise RuntimeError("API_KEY is not set in the environment")



@app.get("/")
def home():
    return {"message": "Adad API is running"}



@app.post("/transliterate")
async def transliterate_name(request: Request):
    
    
    
    api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_Key}'
    
    try:
        data = await request.json()

        english_name = data.get('name')

        prompt = f'Translate the name "{english_name}" into Urdu.'
        payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
                ]
            }
        ]
    }
        print(payload)
        headers = {
            "Content-Type": "application/json"
        }
        print(api_url)
        resp = requests.post(api_url, json=payload, headers=headers)

        print(resp)
        response = resp.json()
        if not english_name:
            return JSONResponse({"error": "No name provided"}, status_code=400)

        
        result_text = response["candidates"][0]["content"]["parts"][0]["text"]
        print(result_text)
        return JSONResponse({"urdu_name": result_text })

    except Exception as e:
        logging.error(f"Error during transliteration: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)





@app.post("/calculate_adad")
async def calculate_adad(request: Request):
    try:
        # Get the input data (Urdu text) from the POST request
        data = await request.json()
        urdu_text = data.get('text')

        if not urdu_text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        # Initialize variables
        total_adad = 0
        adad_breakdown = []

        # Calculate the adad value of the Urdu text, create breakdown, and add English transliteration
        for char in urdu_text:
            # Ignore spaces and non-Urdu characters
            if char in adad_mapping:
                char_adad = adad_mapping[char]
                total_adad += char_adad
                char_transliteration = transliteration_mapping.get(char, "")
                adad_breakdown.append(f"{char} ({char_transliteration}) = {char_adad}")

        # Return the detailed breakdown along with the total adad value
        return JSONResponse({
            "text": urdu_text,
            "adad_value": total_adad,
            "adad_breakdown": adad_breakdown
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
