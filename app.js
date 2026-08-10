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

    // Resume Context Elements & State
    const resumeBtn = document.getElementById('resumeBtn');
    const resumeDot = document.getElementById('resumeDot');
    const resumeModal = document.getElementById('resumeModal');
    const closeResumeModalBtn = document.getElementById('closeResumeModalBtn');
    const resumeToggle = document.getElementById('resumeToggle');
    const dropzone = document.getElementById('dropzone');
    const resumeFileInput = document.getElementById('resumeFileInput');
    const resumeTextArea = document.getElementById('resumeTextArea');
    const resumeStatusBox = document.getElementById('resumeStatusBox');
    const resumeStatusText = document.getElementById('resumeStatusText');
    const saveResumeBtn = document.getElementById('saveResumeBtn');
    const clearResumeBtn = document.getElementById('clearResumeBtn');

    let resumeText = localStorage.getItem('ace_resume_text') || '';
    let resumeActive = localStorage.getItem('ace_resume_active') !== 'false';

    // Initialize Resume UI State
    if (resumeTextArea) resumeTextArea.value = resumeText;
    if (resumeToggle) resumeToggle.checked = resumeActive;
    updateResumeStatusUI();

    // Modal Event Handlers
    if (resumeBtn) {
        resumeBtn.addEventListener('click', () => {
            resumeModal.classList.remove('hidden');
        });
    }

    if (closeResumeModalBtn) {
        closeResumeModalBtn.addEventListener('click', () => {
            resumeModal.classList.add('hidden');
        });
    }

    if (resumeModal) {
        resumeModal.addEventListener('click', (e) => {
            if (e.target === resumeModal) resumeModal.classList.add('hidden');
        });
    }

    // PDF Dropzone & File Pick Handler
    if (dropzone && resumeFileInput) {
        dropzone.addEventListener('click', () => resumeFileInput.click());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                await processResumeFile(e.dataTransfer.files[0]);
            }
        });

        resumeFileInput.addEventListener('change', async (e) => {
            if (e.target.files && e.target.files[0]) {
                await processResumeFile(e.target.files[0]);
            }
        });
    }

    // Process uploaded File (.pdf or .txt)
    async function processResumeFile(file) {
        resumeStatusText.textContent = `Processing file ${file.name}...`;
        try {
            if (file.name.endsWith('.pdf')) {
                const arrayBuffer = await file.arrayBuffer();
                const extractedText = await extractPdfText(arrayBuffer);
                resumeTextArea.value = extractedText;
                resumeStatusText.textContent = `✅ Successfully extracted ${extractedText.split(/\s+/).length} words from PDF! Click "Save & Apply".`;
            } else {
                const text = await file.text();
                resumeTextArea.value = text;
                resumeStatusText.textContent = `✅ Successfully loaded text file! Click "Save & Apply".`;
            }
        } catch (err) {
            console.error('File parsing error:', err);
            resumeStatusText.textContent = `❌ Failed to read file: ${err.message || 'Unknown error'}`;
        }
    }

    // Extract text from PDF using pdf.js
    async function extractPdfText(arrayBuffer) {
        if (typeof pdfjsLib === 'undefined') {
            throw new Error('PDF.js library is loading or blocked by network.');
        }
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let fullText = '';
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            const page = await pdf.getPage(pageNum);
            const tokenContent = await page.getTextContent();
            const pageText = tokenContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
        }
        return fullText.trim();
    }

    // Save Resume Action
    if (saveResumeBtn) {
        saveResumeBtn.addEventListener('click', () => {
            resumeText = resumeTextArea.value.trim();
            resumeActive = resumeToggle.checked;
            localStorage.setItem('ace_resume_text', resumeText);
            localStorage.setItem('ace_resume_active', resumeActive ? 'true' : 'false');
            updateResumeStatusUI();
            resumeModal.classList.add('hidden');
        });
    }

    // Clear Resume Action
    if (clearResumeBtn) {
        clearResumeBtn.addEventListener('click', () => {
            resumeText = '';
            resumeTextArea.value = '';
            localStorage.removeItem('ace_resume_text');
            updateResumeStatusUI();
        });
    }

    if (resumeToggle) {
        resumeToggle.addEventListener('change', () => {
            resumeActive = resumeToggle.checked;
            localStorage.setItem('ace_resume_active', resumeActive ? 'true' : 'false');
            updateResumeStatusUI();
        });
    }

    // Update Status Indicators in Header & Modal
    function updateResumeStatusUI() {
        const hasText = resumeText && resumeText.trim().length > 0;
        if (resumeActive && hasText) {
            if (resumeDot) resumeDot.className = 'status-dot active-green';
            if (resumeStatusBox) {
                resumeStatusBox.style.background = 'rgba(16, 185, 129, 0.12)';
                resumeStatusBox.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                resumeStatusBox.style.color = '#10b981';
            }
            if (resumeStatusText) {
                resumeStatusText.textContent = `🟢 Resume Active (${resumeText.trim().split(/\s+/).length} words loaded)`;
            }
        } else if (hasText) {
            if (resumeDot) resumeDot.className = 'status-dot yellow';
            if (resumeStatusBox) {
                resumeStatusBox.style.background = 'rgba(245, 158, 11, 0.12)';
                resumeStatusBox.style.borderColor = 'rgba(245, 158, 11, 0.4)';
                resumeStatusBox.style.color = '#f59e0b';
            }
            if (resumeStatusText) {
                resumeStatusText.textContent = `🟡 Resume Saved (Personalization Disabled)`;
            }
        } else {
            if (resumeDot) resumeDot.className = 'status-dot grey';
            if (resumeStatusBox) {
                resumeStatusBox.style.background = 'rgba(255, 255, 255, 0.03)';
                resumeStatusBox.style.borderColor = 'var(--border-color)';
                resumeStatusBox.style.color = 'var(--text-muted)';
            }
            if (resumeStatusText) {
                resumeStatusText.textContent = `⚪ No resume loaded. Upload a PDF or paste text above.`;
            }
        }
    }

    // Build Dynamic System Prompt with Resume Context
    function getSystemPrompt() {
        const basePrompt = `You are the candidate sitting in a real technical interview.
The user is the interviewer.

ROLE & PERSONA:
- You are ONLY the candidate. Never act like an interview coach, teacher, mentor, interviewer, or AI assistant.
- Answer questions naturally, confidently, and concisely, exactly like an experienced Data Scientist in an active job interview.
- Always remain in candidate persona.

CRITICAL PHRASING RULES (NO FILLER OPENERS):
- NEVER start answers with "In my experience...", "In my previous experience...", "In my past role...", or "In my career..." as a default opener.
- For theoretical, algorithmic, or conceptual questions, explain the concept directly and concisely without prepending personal filler phrases.
- Only discuss personal projects or past work when specifically asked about your projects, experience, behavioral situations, or architecture decisions.

SELF-INTRODUCTION RULE (START WITH NAME):
- When asked to introduce yourself ("Tell me about yourself", "Introduce yourself", "Walk me through your resume", "Who are you?", "Give your intro"):
  * Start immediately with your candidate name and professional title from your resume, e.g.:
    "Hi, I'm [Candidate Name], a Data Scientist specializing in Machine Learning and Generative AI."
  * NEVER start a self-introduction with "In my experience...".
  * Flow naturally: Name & Title -> Core Specializations & Skills -> 1-2 major project highlights with metrics -> Career focus.

CODING & DSA QUESTIONS:
- When the interviewer asks a coding, algorithm, or Data Structures & Algorithms (DSA) question (e.g. "Write a function to...", "How would you code this?", "Implement two sum", "Write Python code for..."):
  * Briefly state your intuition and approach (e.g. "I'll use a hash map to achieve O(N) time complexity. Here is the code:").
  * Provide clean, optimal, well-commented, working code in Python (unless another language is requested).
  * Briefly explain the time and space complexity and key edge cases after the code.

PROJECT & RESUME GROUNDING:
- The candidate resume is your sole source of truth for your professional history, skills, tools, and metrics.
- Speak in natural first-person ("I built...", "I chose...", "We optimized...").
- Never fabricate companies, projects, numbers, or tools not supported by the resume.
- If you lack direct experience with something, be honest: "I haven't worked with that directly in production, but I understand how it works conceptually..."

SCENARIO & CONTEXT COMPREHENSION:
- Interviewers frequently describe a complex scenario, case study, system constraints, or background context before asking their question.
- You MUST ingest and comprehend the ENTIRE scenario, identify the core challenge or constraints (e.g., latency, scale, imbalanced data, real-time requirements), and tailor your technical answer directly to that scenario rather than giving a generic answer or answering only the last sentence.

VOICE & TEXT-TO-SPEECH FORMATTING:
- For spoken conversational answers, produce clean text without unnecessary markdown or bullet points.
- When writing code for coding/DSA questions, write standard clean code blocks so the interviewer can read the code.
- Do not repeat the interviewer's question.
- Do not say meta phrases like "Here is the answer", "As an AI", or "According to my resume".`;

        if (resumeActive && resumeText && resumeText.trim()) {
            return basePrompt + `\n\n==================================================\nCANDIDATE RESUME CONTEXT\n==================================================\nThe following resume belongs to the candidate you are impersonating during this interview.\nUse this resume as your absolute source of truth for your name, background, projects, tools, metrics, and experience.\n\nCANDIDATE RESUME:\n${resumeText.trim()}\n\n==================================================\nRESUME-GROUNDED INSTRUCTIONS\n==================================================\n1. CANDIDATE NAME & SELF-INTRODUCTION:\n   - Identify the candidate's name from the resume above.\n   - When asked "Tell me about yourself", "Introduce yourself", "Walk me through your resume", or "Give a self intro":\n     * ALWAYS start directly with your name from the resume, e.g.: "Hi, I'm [Candidate Name from Resume], a Data Scientist with [X years] of experience focusing on..."\n     * DO NOT start with "In my experience...".\n     * Summarize role, key technologies, 1-2 top projects with concrete metrics/impact from the resume, and career goals.\n2. BAN ON "IN MY EXPERIENCE" AS A CATCHPHRASE:\n   - Do NOT use "In my experience..." as an opener.\n   - Answer theoretical / technical questions directly without filler.\n3. CODING & DSA QUESTIONS:\n   - When asked to code or solve an algorithm/DSA problem, write clean, efficient, complete Python code with brief complexity analysis.\n4. SCENARIO QUESTIONS:\n   - Comprehend the full scenario described by the interviewer and address all system/business constraints.\n5. ACCURACY & HONESTY:\n   - Stick strictly to the technologies, metrics, and experience in the resume.\n   - If asked about something not in your resume, state honestly that you haven't worked on it directly, then explain conceptually.`;
        }

        return basePrompt;
    }

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
    const muteBtn = document.getElementById('muteBtn');
    const muteIcon = document.getElementById('muteIcon');
    const muteBtnText = document.getElementById('muteBtnText');
    let isMuted = localStorage.getItem('ace_is_muted') === 'true';

    updateMuteUI();

    if (muteBtn) {
        muteBtn.addEventListener('click', () => {
            isMuted = !isMuted;
            localStorage.setItem('ace_is_muted', isMuted ? 'true' : 'false');
            if (isMuted && synth && synth.speaking) {
                synth.cancel();
            }
            updateMuteUI();
        });
    }

    function updateMuteUI() {
        if (!muteBtn) return;
        if (isMuted) {
            muteBtn.classList.add('muted');
            if (muteIcon) {
                muteIcon.innerHTML = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>';
            }
            if (muteBtnText) muteBtnText.textContent = 'Unmute';
            muteBtn.title = 'Unmute Spoken Audio Playback';
        } else {
            muteBtn.classList.remove('muted');
            if (muteIcon) {
                muteIcon.innerHTML = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>';
            }
            if (muteBtnText) muteBtnText.textContent = 'Mute';
            muteBtn.title = 'Mute Spoken Audio Playback';
        }
    }

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
                            content: getSystemPrompt()
                        },
                        { role: 'user', content: userPrompt }
                    ],
                    temperature: 0.7,
                    max_tokens: 300
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error?.message || `HTTP ${response.status}`);
            }

            const data = await response.json();
            const aiText = data.choices[0].message.content.replace(/\*/g, '').replace(/#/g, '').trim();

            appendMessage('Assistant', aiText, false);
            // Get the stop button from the just-appended message
            const lastMsg = chatHistory.lastElementChild;
            speakResponse(aiText, lastMsg ? lastMsg._stopBtn : null);

            micStatusLabel.textContent = 'Tap microphone to speak';
            statusText.textContent = 'Groq LLaMA 3.3 Connected';

        } catch (err) {
            console.error('Groq API Error:', err);
            const fallbackMsg = "I'm having trouble processing that request right now. Please verify your Groq API Key.";
            appendMessage('Assistant', fallbackMsg, false);
            const lastErrMsg = chatHistory.lastElementChild;
            speakResponse(fallbackMsg, lastErrMsg ? lastErrMsg._stopBtn : null);
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
     * @param {string} text - The text to speak
     * @param {HTMLElement|null} stopBtn - Optional stop button to update state when speech ends
     */
    function speakResponse(text, stopBtn = null) {
        if (!synth) return;
        synth.cancel(); // Stop previous speech

        if (isMuted) return; // Skip audio output if muted

        // Reset all other stop buttons across chat
        document.querySelectorAll('.msg-stop-btn.is-speaking').forEach(btn => {
            btn.classList.remove('is-speaking');
            btn.innerHTML = getStopIcon() + ' Stop';
        });

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.88;
        utterance.pitch = 1.0;

        const voices = synth.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
        if (preferredVoice) utterance.voice = preferredVoice;

        if (stopBtn) {
            stopBtn.classList.add('is-speaking');
            stopBtn.innerHTML = getStopActiveIcon() + ' Stop';
        }

        utterance.onend = () => {
            if (stopBtn) {
                stopBtn.classList.remove('is-speaking');
                stopBtn.innerHTML = getStopIcon() + ' Stop';
            }
        };
        utterance.onerror = () => {
            if (stopBtn) {
                stopBtn.classList.remove('is-speaking');
                stopBtn.innerHTML = getStopIcon() + ' Stop';
            }
        };

        synth.speak(utterance);
    }

    /** SVG icon helpers */
    function getStopIcon() {
        return '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="4" y="4" width="16" height="16" rx="2"></rect></svg>';
    }
    function getStopActiveIcon() {
        return '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="4" y="4" width="16" height="16" rx="2"><animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite"/></rect></svg>';
    }
    function getRepeatIcon() {
        return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>';
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

        // Add Stop & Repeat buttons for assistant messages
        if (!isUser) {
            const actions = document.createElement('div');
            actions.className = 'msg-actions';

            const stopBtn = document.createElement('button');
            stopBtn.className = 'msg-action-btn msg-stop-btn';
            stopBtn.innerHTML = getStopIcon() + ' Stop';
            stopBtn.title = 'Stop reading this response';
            stopBtn.addEventListener('click', () => {
                if (synth && synth.speaking) {
                    synth.cancel();
                    stopBtn.classList.remove('is-speaking');
                    stopBtn.innerHTML = getStopIcon() + ' Stop';
                }
            });

            const repeatBtn = document.createElement('button');
            repeatBtn.className = 'msg-action-btn msg-repeat-btn';
            repeatBtn.innerHTML = getRepeatIcon() + ' Repeat';
            repeatBtn.title = 'Repeat this response';
            repeatBtn.addEventListener('click', () => {
                speakResponse(text, stopBtn);
            });

            actions.appendChild(stopBtn);
            actions.appendChild(repeatBtn);
            content.appendChild(actions);

            // Store stopBtn reference so speakResponse can update it on initial read
            msgDiv._stopBtn = stopBtn;
        }

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
