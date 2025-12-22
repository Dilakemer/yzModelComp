import os
import time
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from huggingface_hub import InferenceClient

load_dotenv()

# Gemini Modelleri (Gemma hariç, yüksek kotalı)
GEMINI_MODELS = [
    "gemini-2.5-flash-lite",        # 10 RPM, 250K TPM - EN YÜKSEK KOTA
    "gemini-2.5-flash",             # 5 RPM, 250K TPM
    "gemini-robotics-er-1.5-preview", # 10 RPM, 250K TPM
]

# Hugging Face Modelleri (Açık kaynak, ücretsiz)
HUGGINGFACE_MODELS = [
    "Qwen/Qwen2.5-Coder-32B-Instruct", 
    "meta-llama/Llama-3.2-3B-Instruct",
]

def get_all_models():
    """Tüm mevcut modelleri döndürür"""
    models = []
    for model in GEMINI_MODELS:
        models.append({"name": model, "provider": "gemini"})
    for model in HUGGINGFACE_MODELS:
        models.append({"name": model, "provider": "huggingface"})
    return models

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.configured = True
        else:
            self.configured = False
    
    def generate(self, prompt: str, model_name: str = "gemini-2.0-flash-lite") -> dict:
        if not self.configured:
            return {
                "success": False,
                "error": "Gemini API key not configured",
                "response": None,
                "response_time": 0
            }
        
        try:
            start_time = time.time()
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            end_time = time.time()
            
            return {
                "success": True,
                "response": response.text,
                "response_time": round(end_time - start_time, 2),
                "model": model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "response_time": 0
            }

class HuggingFaceService:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.configured = self.api_key and self.api_key != "your_huggingface_api_key_here"
        if self.configured:
            self.client = InferenceClient(token=self.api_key)
        else:
            self.client = None
    
    def generate(self, prompt: str, model_name: str = "microsoft/Phi-3-mini-4k-instruct") -> dict:
        if not self.configured:
            return {
                "success": False,
                "error": "Hugging Face API key not configured",
                "response": None,
                "response_time": 0
            }
        
        try:
            start_time = time.time()
            
            # Chat completion formatı kullan
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                model=model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            end_time = time.time()
            text = response.choices[0].message.content
            
            return {
                "success": True,
                "response": text,
                "response_time": round(end_time - start_time, 2),
                "model": model_name
            }
        except Exception as e:
            # Fallback: text_generation dene
            try:
                start_time = time.time()
                text = self.client.text_generation(
                    prompt=prompt,
                    model=model_name,
                    max_new_tokens=500,
                    temperature=0.7,
                )
                end_time = time.time()
                
                return {
                    "success": True,
                    "response": text,
                    "response_time": round(end_time - start_time, 2),
                    "model": model_name
                }
            except Exception as e2:
                return {
                    "success": False,
                    "error": str(e2),
                    "response": None,
                    "response_time": 0
                }

# Global servis örnekleri
gemini_service = GeminiService()
huggingface_service = HuggingFaceService()

def test_question_with_model(question: str, model_name: str, provider: str) -> dict:
    """Bir soruyu belirtilen model ile test eder"""
    if provider == "gemini":
        return gemini_service.generate(question, model_name)
    elif provider == "huggingface":
        return huggingface_service.generate(question, model_name)
    else:
        return {
            "success": False,
            "error": f"Unknown provider: {provider}",
            "response": None,
            "response_time": 0
        }

def test_question_with_all_models(question: str) -> list:
    """Bir soruyu tüm modellerle test eder"""
    results = []
    for model_info in get_all_models():
        result = test_question_with_model(
            question, 
            model_info["name"], 
            model_info["provider"]
        )
        result["model_name"] = model_info["name"]
        result["provider"] = model_info["provider"]
        results.append(result)
    return results
