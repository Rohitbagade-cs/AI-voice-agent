# 🤖 AI Voice Agents Dashboard

A futuristic conversational AI platform that enables natural voice interactions powered by cutting-edge speech recognition, language models, and text-to-speech technologies.

![AI Voice Agents Dashboard](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)

## ✨ Features

### 🎙️ **Voice Conversation**
- **Hold-to-Talk Interface**: Intuitive push-to-talk functionality with visual feedback
- **Real-time Speech Recognition**: Powered by AssemblyAI for accurate transcription
- **Natural Language Processing**: Advanced AI responses using Google Gemini
- **High-Quality Text-to-Speech**: Premium voice synthesis with Murf.ai

### 🚀 **Futuristic UI/UX**
- **Glassmorphism Design**: Modern frosted glass effects with neon accents
- **Animated Components**: Pulse rings, gradient borders, and floating particles
- **Responsive Layout**: Seamless experience across desktop and mobile devices
- **Dark Theme**: Cyberpunk-inspired color scheme with neon highlights

### 💾 **Session Management**
- **Persistent Conversations**: Automatic session tracking and history storage
- **Multiple Sessions**: Create new conversations or clear history
- **Auto-Recording**: Optional continuous conversation mode
- **Message History**: Visual chat bubbles with user and AI avatars

### 🛡️ **Error Handling**
- **Robust Fallbacks**: Graceful degradation when APIs are unavailable
- **Connection Monitoring**: Real-time status updates and error notifications
- **Retry Mechanisms**: Automatic fallback to alternative services

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  External APIs  │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)     │◄──►│                 │
│                 │    │                 │    │ • AssemblyAI    │
│ • Voice UI      │    │ • Session Mgmt  │    │ • Google Gemini │
│ • Audio Player  │    │ • Error Handle  │    │ • Murf.ai       │
│ • Animations    │    │ • API Routes    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**

#### Backend
- **FastAPI**: High-performance async web framework
- **Python 3.8+**: Core backend language
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

#### Frontend
- **Vanilla JavaScript**: Modern ES6+ features
- **HTML5**: Semantic markup with audio/media APIs
- **CSS3**: Advanced animations and glassmorphism effects
- **Web Audio API**: Real-time audio recording and playback

#### AI Services
- **AssemblyAI**: Speech-to-text transcription
- **Google Gemini**: Large language model for conversations
- **Murf.ai**: Premium text-to-speech synthesis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser with microphone access
- API keys for required services

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-voice-agents.git
cd ai-voice-agents
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the backend directory:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
MURF_API_KEY=your_murf_api_key_here

# Optional Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 4. Get API Keys

#### AssemblyAI (Speech Recognition)
1. Sign up at [assemblyai.com](https://www.assemblyai.com/)
2. Get your API key from the dashboard
3. Add to `.env` file

#### Google Gemini (Language Model)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env` file

#### Murf.ai (Text-to-Speech)
1. Register at [murf.ai](https://murf.ai/)
2. Subscribe to API access
3. Get your API key from settings
4. Add to `.env` file

### 5. Start the Backend Server
```bash
# From backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Frontend Setup
```bash
# Open new terminal
cd frontend

# Serve static files (choose one method):

# Method 1: Python HTTP server
python -m http.server 3000

# Method 2: Node.js (if you have it)
npx serve . -p 3000

# Method 3: Use any static file server
```

### 7. Access the Application
Open your browser and navigate to:
- **Frontend**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`

## 📁 Project Structure

```
ai-voice-agents/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── static/             # Static file serving
├── frontend/
│   ├── index.html          # Main application
│   ├── style.css           # Futuristic styling
│   ├── script.js           # Frontend logic
│   └── assets/             # Images and icons
├── README.md               # Project documentation
└── .gitignore             # Git ignore file
```

## 🎯 Usage Guide

### Starting a Conversation
1. **Open the Application**: Navigate to the frontend URL
2. **Grant Microphone Access**: Allow browser permissions
3. **Hold to Talk**: Press and hold the mic button
4. **Speak Naturally**: Release when finished
5. **Listen to Response**: AI will respond with voice

### Session Management
- **New Chat**: Click "🔄 New Chat" to start fresh
- **Clear History**: Remove all messages from current session
- **Auto-Continue**: Toggle for hands-free conversation

### Advanced Features
- **Session Persistence**: Conversations are saved automatically
- **Error Recovery**: System handles API failures gracefully
- **Mobile Support**: Fully responsive design

## 🛠️ API Endpoints

### Conversational Agent
```http
POST /agent/chat/{session_id}
Content-Type: multipart/form-data

# Upload audio file for processing
# Returns: JSON with transcription, AI response, and audio URL
```

### Session Management
```http
GET /agent/history/{session_id}
# Returns: Conversation history for session

DELETE /agent/history/{session_id}
# Clears: All messages for the session
```

### Health Check
```http
GET /health
# Returns: API status and version
```

## 🔧 Configuration

### Backend Settings
Edit `main.py` to customize:
- **CORS settings**: Modify allowed origins
- **File upload limits**: Adjust maximum file sizes
- **Response timeouts**: Configure API timeout values

### Frontend Customization
Edit `style.css` for:
- **Color schemes**: Change neon colors and gradients
- **Animation speeds**: Modify transition durations
- **Layout dimensions**: Adjust container sizes

## 🚨 Troubleshooting

### Common Issues

#### "Error loading ASGI app. Could not import module 'main'"
```bash
# Ensure you're in the correct directory
cd backend
uvicorn main:app --reload
```

#### "Microphone access denied"
- Grant microphone permissions in browser settings
- Use HTTPS for production (required for audio access)

#### "API key errors"
- Verify all API keys are correctly set in `.env`
- Check API key validity and quotas
- Ensure environment variables are loaded

#### "CORS errors"
- Update allowed origins in FastAPI CORS middleware
- Check that frontend and backend URLs match

### Performance Optimization
- **Audio Format**: Use WebM for better compression
- **Session Cleanup**: Implement automatic old session removal
- **Caching**: Add response caching for repeated queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AssemblyAI** for speech recognition technology
- **Google** for Gemini language model
- **Murf.ai** for high-quality text-to-speech
- **FastAPI** community for excellent documentation
- **30 Days of AI Voice Agents** challenge inspiration

## 📞 Support

For support, email your-email@example.com or join our [Discord community](https://discord.gg/yourserver).

## 🚀 Future Roadmap

- [ ] **Multi-language Support**: Expand to support multiple languages
- [ ] **Voice Cloning**: Custom voice synthesis options
- [ ] **Sentiment Analysis**: Emotion detection in conversations
- [ ] **Integration APIs**: Webhook support for external systems
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Cloud Deployment**: One-click deployment to AWS/GCP/Azure

---

<div align="center">
  <strong>Built with ❤️ for the future of AI conversation</strong>
  <br>
  <em>Experience the next generation of voice AI today!</em>
</div>