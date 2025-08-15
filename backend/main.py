from fastapi import FastAPI, Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
import google.generativeai as genai
import assemblyai as aai
import requests
import os
from dotenv import load_dotenv
import uuid
from typing import Dict, List

# Load the .env file
load_dotenv()

# Get the API keys from environment
MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Configure AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

app = FastAPI()

# In-memory chat history storage
# Structure: {session_id: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
chat_history: Dict[str, List[Dict[str, str]]] = {}

# Serve static frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def serve_home():
    return FileResponse("../frontend/index.html")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class TextRequest(BaseModel):
    text: str

@app.post("/generate-audio")
def generate_audio(request: TextRequest):
    if not MURF_API_KEY:
        print("❌ API key missing in environment.")
        return JSONResponse(status_code=500, content={"error": "API key not found."})

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": request.text,
        "voice_id": "en-IN-isha",   # Make sure this voice ID is valid
        "format": "mp3"
    }

    try:
        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )

        print("📤 Payload sent to Murf:", payload)
        print("📥 Murf API response:", response.status_code, response.text)

        if response.status_code == 200:
            result = response.json()
            return {"audio_url": result.get("audioFile")}
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"Status {response.status_code}: {response.text}"}
            )

    except Exception as e:
        print("❌ Exception while calling Murf:", str(e))
        return JSONResponse(status_code=500, content={"error": "Something went wrong."})

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    file_location = os.path.join(uploads_dir, file.filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_kb": round(len(content) / 1024, 2)
    }

@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    audio_data = await file.read()

    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(audio_data)
        return {"transcript": transcript.text}
    except Exception as e:
        print("❌ Transcription failed:", str(e))
        return {"error": "Transcription failed. Try again."}

@app.post("/tts/echo")
async def echo_bot_v2(file: UploadFile = File(...)):
    # 1. Read audio
    audio_data = await file.read()

    # 2. Transcribe using AssemblyAI
    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(audio_data).text
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}

    # 3. Generate Murf TTS from transcript
    murf_api_key = os.getenv("MURF_API_KEY")
    headers = {
        "api-key": murf_api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": transcript,
        "voice_id": "en-IN-isha",  # Replace with any valid Murf voice ID
        "format": "mp3"
    }

    try:
        murf_response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )

        if murf_response.status_code == 200:
            return {"audio_url": murf_response.json().get("audioFile")}
        else:
            return {
            "audio_url": murf_response.json().get("audioFile"),
            "transcript": transcript}
    except Exception as e:
        return {"error": f"Murf request error: {str(e)}"}

@app.post("/llm/query")
async def query_llm_with_audio(file: UploadFile = File(...)):
    """
    Complete pipeline: Audio -> Transcription -> LLM -> TTS -> Audio Response
    """
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Gemini API key not found."})
    
    if not MURF_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Murf API key not found."})
    
    try:
        # Step 1: Read and transcribe audio
        audio_data = await file.read()
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_data)
        
        if not transcript.text:
            return JSONResponse(status_code=400, content={"error": "Could not transcribe audio"})
        
        user_query = transcript.text
        print(f"📝 User said: {user_query}")
        
        # Step 2: Send to Gemini LLM
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Add a prompt to keep responses concise for TTS
        prompt = f"Please provide a concise and helpful response (under 200 words) to this question: {user_query}"
        
        response = model.generate_content(prompt)
        llm_response = response.text
        print(f"🤖 LLM Response: {llm_response}")
        
        # Step 3: Limit response length for Murf (max 3000 characters)
        if len(llm_response) > 2900:  # Leave some buffer
            llm_response = llm_response[:2900] + "..."
        
        # Step 4: Convert LLM response to speech using Murf
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": llm_response,
            "voice_id": "en-IN-isha",
            "format": "mp3"
        }
        
        murf_response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )
        
        if murf_response.status_code == 200:
            audio_url = murf_response.json().get("audioFile")
            return {
                "user_query": user_query,
                "llm_response": llm_response,
                "audio_url": audio_url,
                "model": "gemini-1.5-flash"
            }
        else:
            print(f"❌ Murf API error: {murf_response.status_code} - {murf_response.text}")
            return JSONResponse(
                status_code=500,
                content={"error": f"TTS generation failed: {murf_response.text}"}
            )
            
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"LLM query pipeline failed: {str(e)}"}
        )

FALLBACK_TEXT = "I'm having trouble connecting right now."

def murf_tts(text):
    """Generate TTS audio using Murf or fallback."""
    try:
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_id": "en-IN-isha",
            "format": "mp3"
        }
        murf_response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload,
            timeout=15
        )
        if murf_response.status_code == 200:
            return murf_response.json().get("audioFile")
        else:
            print("Murf error:", murf_response.text)
    except Exception as e:
        print("Murf TTS exception:", e)
    # Fallback: Try to generate fallback audio
    if text != FALLBACK_TEXT:
        return murf_tts(FALLBACK_TEXT)
    return None

@app.post("/agent/chat/{session_id}")
async def conversational_agent(
    session_id: str = Path(..., description="Session ID for chat history"),
    file: UploadFile = File(...)
):
    try:
        # STT
        try:
            audio_data = await file.read()
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_data)
            user_message = transcript.text.strip()
        except Exception as stt_error:
            print("STT error:", stt_error)
            user_message = FALLBACK_TEXT

        # LLM
        try:
            if user_message == FALLBACK_TEXT:
                llm_response = FALLBACK_TEXT
            else:
                if session_id not in chat_history:
                    chat_history[session_id] = []
                chat_history[session_id].append({"role": "user", "content": user_message})
                conversation_context = ""
                for message in chat_history[session_id]:
                    if message["role"] == "user":
                        conversation_context += f"User: {message['content']}\n"
                    else:
                        conversation_context += f"Assistant: {message['content']}\n"
                prompt = f"""You are a helpful AI assistant. Respond naturally and concisely.
Conversation history:
{conversation_context}
Respond to the latest user message."""
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                llm_response = response.text.strip()
        except Exception as llm_error:
            print("LLM error:", llm_error)
            llm_response = FALLBACK_TEXT

        # TTS
        try:
            if len(llm_response) > 2900:
                llm_response = llm_response[:2900] + "..."
            audio_url = murf_tts(llm_response)
        except Exception as tts_error:
            print("TTS error:", tts_error)
            audio_url = murf_tts(FALLBACK_TEXT)

        # Save assistant response
        chat_history[session_id].append({"role": "assistant", "content": llm_response})

        return {
            "session_id": session_id,
            "user_message": user_message,
            "assistant_response": llm_response,
            "audio_url": audio_url,
            "conversation_length": len(chat_history[session_id]),
            "model": "gemini-1.5-flash"
        }
    except Exception as e:
        print("General error:", e)
        audio_url = murf_tts(FALLBACK_TEXT)
        return {
            "session_id": session_id,
            "user_message": FALLBACK_TEXT,
            "assistant_response": FALLBACK_TEXT,
            "audio_url": audio_url,
            "conversation_length": len(chat_history.get(session_id, [])),
            "model": "gemini-1.5-flash"
        }

@app.get("/agent/history/{session_id}")
def get_chat_history(session_id: str = Path(..., description="Session ID")):
    """Get chat history for a session"""
    if session_id in chat_history:
        return {
            "session_id": session_id,
            "history": chat_history[session_id],
            "message_count": len(chat_history[session_id])
        }
    else:
        return {
            "session_id": session_id,
            "history": [],
            "message_count": 0
        }

@app.delete("/agent/history/{session_id}")
def clear_chat_history(session_id: str = Path(..., description="Session ID")):
    """Clear chat history for a session"""
    if session_id in chat_history:
        del chat_history[session_id]
        return {"message": f"Chat history cleared for session {session_id}"}
    else:
        return {"message": f"No chat history found for session {session_id}"}