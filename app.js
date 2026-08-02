/**
 * ACE THE INTERVIEW - HYBRID VOICE CHATBOT (Web Speech API + Groq Cloud API)
 * Designed for 100% FREE Hugging Face Static Spaces Deployment (Zero PRO Subscription Required!)
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const micBtn = document.getElementById('micBtn');
    const micStatusLabel = document.getElementById('micStatusLabel');
    const chatHistory = document.getElementById('chatHistory');
    const textForm = document.getElementById('textForm');
    const textInput = document.getElementById('textInput');
    const clearBtn = document.getElementById('clearBtn');
    const canvas = document.getElementById('audioVisualizer');
    const canvasCtx = canvas.getContext('2d');
    const statusText = document.getElementById('statusText');

    // Speech Recognition & Synthesis APIs
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;
    let synth = window.speechSynthesis;

    // Canvas Dimensions
    function resizeCanvas() {
        if (canvas && canvas.parentElement) {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initial Waveform
    drawIdleWaveform();

    // Check Speech Recognition Availability
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            micBtn.classList.add('recording');
            micStatusLabel.textContent = 'Listening... Speak into microphone';
            micStatusLabel.style.color = '#ec4899';
            drawActiveWaveform();
        };

        recognition.onresult = async (event) => {
            const userSpeech = event.results[0][0].transcript;
            console.log('Recognized User Speech:', userSpeech);
            stopListening();

            if (userSpeech.trim()) {
                appendMessage('User', userSpeech, true);
                await processWithGroq(userSpeech);
            } else {
                micStatusLabel.textContent = "Didn't catch that. Tap microphone to try again.";
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech Recognition Error:', event.error);
            stopListening();
            micStatusLabel.textContent = `Mic error (${event.error}). Tap to retry.`;
        };

        recognition.onend = () => {
            stopListening();
        };
    } else {
        micStatusLabel.textContent = 'Web Speech API not supported in this browser. Use Chrome/Edge.';
    }

    // Controls
    micBtn.addEventListener('click', toggleListening);
    textForm.addEventListener('submit', handleTextSubmit);
    clearBtn.addEventListener('click', handleResetSession);

    function toggleListening() {
        if (!recognition) {
            alert('Speech Recognition is not supported in your browser. Please use Google Chrome or Microsoft Edge.');
            return;
        }
        if (isListening) {
            recognition.stop();
            stopListening();
        } else {
            try {
                recognition.start();
            } catch (e) {
                console.warn('Recognition start exception:', e);
            }
        }
    }

    function stopListening() {
        isListening = false;
        micBtn.classList.remove('recording');
        micStatusLabel.textContent = 'Tap microphone to speak';
        micStatusLabel.style.color = '#9ca3af';
        drawIdleWaveform();
    }

    /**
     * Query Groq Cloud LLaMA 3.3 API
     */
    async function processWithGroq(userPrompt) {
        micStatusLabel.textContent = 'Groq AI Thinking...';
        statusText.textContent = 'Querying Groq LLaMA 3.3...';

        // Retrieve Groq API key securely from localStorage or prompt user
        let apiKey = localStorage.getItem('GROQ_API_KEY') || '';
        if (!apiKey) {
            apiKey = prompt('Please enter your Groq API Key (starts with gsk_):');
            if (apiKey && apiKey.trim()) {
                apiKey = apiKey.trim();
                localStorage.setItem('GROQ_API_KEY', apiKey);
            } else {
                throw new Error('Groq API Key is required.');
            }
        }


        try {
            const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: 'llama-3.3-70b-versatile',
                    messages: [
                        {
                            role: 'system',
                            content: 'You are an expert Data Science and Generative AI Interview Coach. STRICT DOMAIN RULE: You ONLY answer questions related to Data Science, Machine Learning, Deep Learning, Statistics, MLOps, NLP, Computer Vision, and Generative AI (LLMs, RAG, Transformers, Fine-Tuning, Diffusion). If the user asks a question OUTSIDE of Data Science and Generative AI (e.g. cooking, general non-AI topics), respond EXACTLY: "I am specifically designed for Data Science and Generative AI interview preparation. Please ask a question related to Data Science, Machine Learning, or AI concepts." FOR DATA SCIENCE & GEN-AI QUESTIONS: Provide a clear, easy-to-understand sample response demonstrating EXACTLY how a candidate should articulate their answer in a real Data Science job interview. Speak directly in first-person ("In my experience...") as the candidate giving their spoken response. Keep it structured, clear, professional, and concise (2-4 sentences) without markdown formatting, bullet points, asterisks, or intro filler.'
                        },
                        { role: 'user', content: userPrompt }
                    ],
                    temperature: 0.7,
                    max_tokens: 250
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error?.message || `HTTP ${response.status}`);
            }

            const data = await response.json();
            const aiText = data.choices[0].message.content.replace(/\*/g, '').replace(/#/g, '').trim();

            appendMessage('Assistant', aiText, false);
            speakResponse(aiText);

            micStatusLabel.textContent = 'Tap microphone to speak';
            statusText.textContent = 'Groq LLaMA 3.3 Connected';

        } catch (err) {
            console.error('Groq API Error:', err);
            const fallbackMsg = "I'm having trouble processing that request right now. Please verify your Groq API Key.";
            appendMessage('Assistant', fallbackMsg, false);
            speakResponse(fallbackMsg);
            micStatusLabel.textContent = 'Tap microphone to speak';
            statusText.textContent = 'API Error';
        }
    }

    /**
     * Text Input Fallback
     */
    async function handleTextSubmit(e) {
        e.preventDefault();
        const text = textInput.value.trim();
        if (!text) return;

        appendMessage('User', text, true);
        textInput.value = '';
        await processWithGroq(text);
    }

    /**
     * Text-to-Speech Output via SpeechSynthesis API
     */
    function speakResponse(text) {
        if (!synth) return;
        synth.cancel(); // Stop previous speech

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.88; // Slower, comfortable pace for clear word listening

        utterance.pitch = 1.0;

        const voices = synth.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
        if (preferredVoice) utterance.voice = preferredVoice;

        synth.speak(utterance);
    }

    /**
     * Append Chat Message Bubble
     */
    function appendMessage(sender, text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = isUser ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const name = document.createElement('div');
        name.className = 'sender-name';
        name.textContent = isUser ? 'You' : 'Voice Assistant';

        const textPara = document.createElement('p');
        textPara.textContent = text;

        content.appendChild(name);
        content.appendChild(textPara);
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    /**
     * Reset Session
     */
    function handleResetSession() {
        if (synth) synth.cancel();
        chatHistory.innerHTML = `
            <div class="message assistant-message">
                <div class="avatar">🤖</div>
                <div class="message-content">
                    <div class="sender-name">Voice Assistant</div>
                    <p>Conversation reset. I am ready for your next question!</p>
                </div>
            </div>
        `;
        micStatusLabel.textContent = 'Tap microphone to speak';
    }

    /**
     * Idle Waveform Visualizer
     */
    function drawIdleWaveform() {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.beginPath();
        canvasCtx.moveTo(0, canvas.height / 2);
        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        canvasCtx.lineWidth = 2;
        canvasCtx.stroke();
    }

    /**
     * Animated Waveform while Listening
     */
    let waveOffset = 0;
    function drawActiveWaveform() {
        if (!isListening) return;
        requestAnimationFrame(drawActiveWaveform);

        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.beginPath();
        canvasCtx.lineWidth = 3;
        canvasCtx.strokeStyle = '#ec4899';

        const width = canvas.width;
        const height = canvas.height;
        waveOffset += 0.15;

        for (let x = 0; x < width; x += 5) {
            const y = height / 2 + Math.sin(x * 0.03 + waveOffset) * 20;
            if (x === 0) canvasCtx.moveTo(x, y);
            else canvasCtx.lineTo(x, y);
        }
        canvasCtx.stroke();
    }
});
