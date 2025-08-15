document.addEventListener("DOMContentLoaded", () => {
  // Existing variables
  const generateBtn = document.getElementById("generateBtn");
  const textInput = document.getElementById("textInput");
  const audioPlayer = document.getElementById("audioPlayer");
  const playBtn = document.getElementById("playBtn");
  const pauseBtn = document.getElementById("pauseBtn");

  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const echoPlayer = document.getElementById("echoPlayer");

  let mediaRecorder;
  let audioChunks = [];

  // Session management
  let currentSessionId = getSessionIdFromURL() || generateSessionId();
  let autoRecording = false;

  // Conversational AI variables
  const convStartBtn = document.getElementById("convStartBtn");
  const convStopBtn = document.getElementById("convStopBtn");
  const autoRecordBtn = document.getElementById("autoRecordBtn");
  const convPlayer = document.getElementById("convPlayer");
  const conversationHistory = document.getElementById("conversation-history");
  let convMediaRecorder;
  let convAudioChunks = [];

  // Session management functions
  function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  function getSessionIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('session_id');
  }

  function updateURLWithSession(sessionId) {
    const url = new URL(window.location);
    url.searchParams.set('session_id', sessionId);
    window.history.pushState({}, '', url);
  }

  // Initialize session
  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("session-id").textContent = currentSessionId;
    updateURLWithSession(currentSessionId);
    loadConversationHistory();
  });

  // Session controls
  document.getElementById("newSessionBtn").addEventListener("click", () => {
    currentSessionId = generateSessionId();
    document.getElementById("session-id").textContent = currentSessionId;
    updateURLWithSession(currentSessionId);
    conversationHistory.innerHTML = "";
    document.getElementById("convStatus").textContent = "🔄 New conversation started!";
  });

  document.getElementById("clearHistoryBtn").addEventListener("click", async () => {
    try {
      await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`, {
        method: "DELETE"
      });
      conversationHistory.innerHTML = "";
      document.getElementById("convStatus").textContent = "🗑️ History cleared!";
    } catch (error) {
      console.error("Error clearing history:", error);
    }
  });

  // Load conversation history
  async function loadConversationHistory() {
    try {
      const response = await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`);
      const data = await response.json();
      
      conversationHistory.innerHTML = "";
      data.history.forEach(message => {
        addMessageToHistory(message.role, message.content);
      });
    } catch (error) {
      console.error("Error loading history:", error);
    }
  }

  // Add message to conversation history display
  function addMessageToHistory(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = role === "user" ? "user-message" : "assistant-message";
    messageDiv.style.cssText = `
      background: ${role === "user" ? "#e3f2fd" : "#f3e5f5"};
      padding: 8px;
      border-radius: 8px;
      margin: 5px 0;
      font-size: 14px;
      color: black;
      border-left: 4px solid ${role === "user" ? "#2196F3" : "#9C27B0"};
    `;
    
    messageDiv.innerHTML = `<strong>${role === "user" ? "You" : "AI"}:</strong> ${content}`;
    conversationHistory.appendChild(messageDiv);
    conversationHistory.scrollTop = conversationHistory.scrollHeight;
  }

  // Conversational AI functionality
  convStartBtn.addEventListener("click", async () => {
    console.log("Start conversation button clicked");
    await startConversationRecording();
  });

  convStopBtn.addEventListener("click", () => {
    console.log("Stop conversation button clicked");
    if (convMediaRecorder && convMediaRecorder.state === "recording") {
      convMediaRecorder.stop();
    }
    convStartBtn.disabled = false;
    convStopBtn.disabled = true;
  });

  autoRecordBtn.addEventListener("click", () => {
    autoRecording = !autoRecording;
    autoRecordBtn.textContent = `🔄 Auto Recording: ${autoRecording ? "ON" : "OFF"}`;
    autoRecordBtn.style.background = autoRecording ? "rgba(76, 175, 80, 0.3)" : "rgba(244, 67, 54, 0.3)";
  });

  async function startConversationRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      convMediaRecorder = new MediaRecorder(stream);
      convAudioChunks = [];

      convMediaRecorder.ondataavailable = event => {
        convAudioChunks.push(event.data);
      };

      convMediaRecorder.onstop = () => {
        const audioBlob = new Blob(convAudioChunks, { type: "audio/webm" });
        const convForm = new FormData();
        convForm.append("file", audioBlob, "conversation.webm");

        document.getElementById("convStatus").textContent = "🤖 Processing your message...";

        fetch(`http://127.0.0.1:8000/agent/chat/${currentSessionId}`, {
          method: "POST",
          body: convForm
        })
          .then(res => res.json())
          .then(data => {
            addMessageToHistory("user", data.user_message);
            addMessageToHistory("assistant", data.assistant_response);

            if (data.audio_url) {
              convPlayer.src = data.audio_url;
              convPlayer.style.display = "block";
              convPlayer.onended = () => {
                if (autoRecording) {
                  setTimeout(() => {
                    startConversationRecording();
                  }, 1000);
                }
              };
              convPlayer.play();
              document.getElementById("convStatus").textContent = `✅ AI responded! (${data.conversation_length} messages)`;
            } else {
              document.getElementById("convStatus").textContent = "❌ No audio response. Playing fallback.";
              playFallbackAudio();
            }
          })
          .catch(err => {
            document.getElementById("convStatus").textContent = "❌ Error in conversation. Playing fallback.";
            console.error("Conversation Error:", err);
            playFallbackAudio();
          });
      };

      convMediaRecorder.start();
      convStartBtn.disabled = true;
      convStopBtn.disabled = false;
      autoRecordBtn.style.display = "inline-block";
      document.getElementById("convStatus").textContent = "🎙️ Recording your message...";
    } catch (error) {
      console.error("Microphone error:", error);
      document.getElementById("convStatus").textContent = "❌ Microphone access denied";
    }
  }

  // Fallback audio function
  function playFallbackAudio() {
    // You can use a local fallback mp3 or TTS API with fallback text
    convPlayer.src = "/static/fallback.mp3"; // Place a fallback.mp3 in your static folder
    convPlayer.style.display = "block";
    convPlayer.play();
  }

  // AI Voice Agent functionality
  generateBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) {
      alert("Please enter some text first!");
      return;
    }

    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-audio", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: text })
      });

      const data = await response.json();
      
      if (data.audioFile) {
        audioPlayer.src = data.audioFile;
        document.getElementById("audioControls").style.display = "block";
        audioPlayer.play();
      } else {
        alert("Error: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error generating audio");
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = "Generate Audio";
    }
  });

  // Echo Bot functionality
  startBtn.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const echoForm = new FormData();
        echoForm.append("file", audioBlob, "echo.webm");

        document.getElementById("status").textContent = "🔁 Processing...";

        fetch("http://127.0.0.1:8000/tts/echo", {
          method: "POST",
          body: echoForm
        })
          .then(res => {
            if (!res.ok) {
              throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
          })
          .then(data => {
            if (data.audio_url) {
              echoPlayer.src = data.audio_url;
              echoPlayer.style.display = "block";
              echoPlayer.play();

              document.getElementById("status").textContent = "✅ Echo with Murf voice";

              if (data.transcript) {
                const transcriptionElement = document.getElementById("transcription");
                if (transcriptionElement) {
                  transcriptionElement.textContent = `🗣️ Transcript: "${data.transcript}"`;
                  transcriptionElement.style.display = "block";
                }
              }
            } else {
              document.getElementById("status").textContent = "❌ " + (data.error || "Unknown error");
            }
          })
          .catch(err => {
            document.getElementById("status").textContent = "❌ Error in echo bot";
            console.error(err);
          });
      };

      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;
      document.getElementById("status").textContent = "🎙️ Recording...";
    } catch (error) {
      console.error("Microphone error:", error);
      document.getElementById("status").textContent = "❌ Microphone access denied";
    }
  });

  stopBtn.addEventListener("click", () => {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
  });

  // Audio controls
  if (playBtn) {
    playBtn.addEventListener("click", () => {
      audioPlayer.play();
    });
  }

  if (pauseBtn) {
    pauseBtn.addEventListener("click", () => {
      audioPlayer.pause();
    });
  }
});
