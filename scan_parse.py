from asyncore import write
import requests
import google.generativeai as genai
import os
from google.cloud import vision
import time
from dotenv import load_dotenv
import json
load_dotenv()

client = vision.ImageAnnotatorClient()

def scan_receipt(binary_image):
        image = vision.Image(content=binary_image)
        response = client.document_text_detection(image=image)
        document = response.full_text_annotation
        return  document.text

def scan_parse_receipts(binary_image):
    rawtext = scan_receipt(binary_image)
    file_name = "receipt" + str(time.time()) + ".jpg"
    with open("temp_images/" + file_name, "wb") as f:
        f.write(binary_image)
    prompt = f"""
    Extract the following information from the Receipt text provided
    -Store name
    -Item Name its Amount and Quantity
    -HST
    -Date
    -Total 
    -filename (provided to you in example, should be same)
    
    The output should be in strict raw JSON like below:
    {{
        "storename": Store Name,
        "items": [Item Name @ Amount x Quantity, Next Item ... ],
        "HST": HST,
        "total": Total,
        "date": Date,
        "filename": {file_name}
    }}
    
    Provided Receipt text: {rawtext}
    
"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemma-3-27b-it")
    response = model.generate_content(prompt)
    result = response.text.strip()
    result = result.replace("```json", "").replace("```", "").strip()
    return result

def store(binary_image):
    try:
        receipt_json = scan_parse_receipts(binary_image)
    except Exception as e:
        return "Error scanning/parsing receipt. Please try again."

    try:
        data = json.loads(receipt_json)
    except Exception as e:
        return "Error reading receipt data."

    try:
        # post to sheets
        url = "https://script.google.com/macros/s/AKfycbzo3Dccq15c7vQq174y7wDX5lfbywCCJEeKTJg_UCE-qZzRQkPKFbV4pXaRKZVKoOcg/exec"
        requests.post(url, json=data)
    except Exception as e:
        return "Error storing to sheets."
    return "Successfully stored receipt.\n\n" + receipt_json