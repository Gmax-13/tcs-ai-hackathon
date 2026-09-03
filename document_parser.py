import base64
import os
import io
import json
import logging
from PyPDF2 import PdfReader
import requests

logger = logging.getLogger(__name__)

# We'll use Llama-3.2-11B-Vision for image context extraction
VISION_MODEL = "llama-3.2-11b-vision-preview"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_context_from_file(file_name: str, file_type: str, file_base64: str) -> str:
    """
    Given a base64 encoded file, extract text context.
    If PDF, use PyPDF2.
    If Image, use Groq Vision model.
    """
    logger.info(f"Extracting context from {file_name} ({file_type})")
    
    # Check if base64 has data URI prefix (e.g. data:image/png;base64,...)
    if "," in file_base64:
        file_base64 = file_base64.split(",")[1]

    try:
        if file_type == "application/pdf":
            return _parse_pdf(file_base64)
        elif file_type.startswith("image/"):
            return _parse_image(file_base64, file_type)
        else:
            return f"[Unsupported file type uploaded: {file_type}. Could not parse.]"
    except Exception as e:
        logger.error(f"Failed to parse document {file_name}: {e}")
        return f"[Failed to parse uploaded document: {file_name}]"

def _parse_pdf(file_base64: str) -> str:
    file_bytes = base64.b64decode(file_base64)
    pdf_file = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    
    extracted_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            extracted_text.append(text.strip())
            
    if not extracted_text:
        return "[No extractable text found in the PDF.]"
        
    return "\n\n".join(extracted_text)

def _parse_image(file_base64: str, file_type: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set - skipping Vision API call.")
        return "[Cannot extract text from image: API key missing]"

    # Groq Vision Payload
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Analyze this image for a hackathon project. Extract all visible text, and describe any UI wireframes, flowcharts, or architecture diagrams in detail so the context can be used by another AI mentor."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{file_type};base64,{file_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    logger.info("Calling Groq Vision API for image extraction...")
    resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
    
    if resp.status_code != 200:
        logger.warning(f"Groq Vision API error: {resp.text[:500]}")
        return "[Failed to extract text from image using Vision API]"

    data = resp.json()
    return data["choices"][0]["message"]["content"]
