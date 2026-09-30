// Dedicated Interview Room Logic: Immediate Display, Live Speech Recording, Dual-Agent Reaction Matrix & SQL Archiving

let resumeText = "";
let matchingSkills = [];
let missingSkills = [];
let targetRole = "";
let interviewQuestions = [];
let currentQuestionIndex = 0;
let interviewSummary = [];

let recognition = null;
let isRecording = false;

// Dual-Agent Tracking & Reactions
let currentDifficulty = 5.0;
let questionStartTime = Date.now();
let turnsHistory = []; // { turn, question, answer, confidence, difficulty, latency_seconds, strategy, breaking_point, weak_skill }
let breakingPointsList = [];
let liveChart = null;
let finalChart = null;
let nextAdaptiveQuestion = null;

document.addEventListener("DOMContentLoaded", () => {
  if (!API.requireAuth()) return;
  API.renderUserBadge();
  setupSpeechRecognition();
  initLiveChart();

  // 1. Immediately reveal the question card so there is ZERO waiting!
  document.getElementById("loadingQuestionsCard").classList.add("d-none");
  document.getElementById("questionCard").classList.remove("d-none");

  // 2. Load context from localStorage
  resumeText = localStorage.getItem("interview_resume_text") || "";
  try {
    matchingSkills = JSON.parse(localStorage.getItem("interview_matching_skills") || "[]");
  } catch (e) { matchingSkills = []; }
  try {
    missingSkills = JSON.parse(localStorage.getItem("interview_missing_skills") || "[]");
  } catch (e) { missingSkills = []; }

  targetRole = localStorage.getItem("interview_target_role") || "";
  if (targetRole) {
    const roleElem = document.getElementById("targetRoleSubtitle");
    if (roleElem) roleElem.textContent = `Target Role: ${targetRole}`;
  }

  // 3. Immediately display standard Question 1 right away
  interviewQuestions = [
    "Could you please introduce yourself and summarize your core technical skills?",
    "Describe a challenging technical project you built, explaining the architecture and challenges solved.",
    "How do you approach debugging and optimizing performance in production?",
    "Where do you see your technical career progressing in the next few years?"
  ];
  interviewQuestions.forEach(q => prefetchQuestionAudio(q));
  displayQuestion(0);

  // 4. In background, fetch customized AI questions tailored to candidate's resume / JD
  loadTailoredQuestionsInBackground();
});

function showAlert(msg, isSuccess = false) {
  const alertBox = document.getElementById("interviewAlert");
  if (!alertBox) return;
  alertBox.textContent = msg;
  alertBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
  alertBox.classList.remove("d-none");
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideAlert() {
  const alertBox = document.getElementById("interviewAlert");
  if (alertBox) alertBox.classList.add("d-none");
}

async function loadTailoredQuestionsInBackground() {
  try {
    const res = await API.post("/api/interview/start", {
      resume_text: resumeText || "General Software Engineering candidate",
      matching_skills: matchingSkills.length > 0 ? matchingSkills : null,
      missing_skills: missingSkills.length > 0 ? missingSkills : null
    });

    if (res && res.questions && res.questions.length > 0) {
      // Do NOT interrupt Question 1 while it is being spoken!
      // Update the question pool for subsequent questions seamlessly
      const currentFirstQ = interviewQuestions[0];
      const tailoredRemaining = res.questions.filter(q => q !== currentFirstQ);
      interviewQuestions = [
        currentFirstQ,
        ...tailoredRemaining
      ];
      interviewQuestions.forEach(q => prefetchQuestionAudio(q));
      document.getElementById("interviewProgressText").textContent = `Question ${currentQuestionIndex + 1} of ${interviewQuestions.length}`;
    }
  } catch (err) {
    console.log("Background question fetch notice (using active questions):", err);
  }
}

// (Microsoft Edge-TTS handles voice synthesis via server-side streaming)

// ----------------- Real-Time Reaction Chart -----------------
function initLiveChart() {
  const canvas = document.getElementById("liveReactionChart");
  if (!canvas || typeof Chart === "undefined") return;

  const ctx = canvas.getContext("2d");
  liveChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Init'],
      datasets: [
        {
          label: 'Confidence Curve (0.0 - 1.0)',
          data: [null],
          borderColor: '#0284c7', // Cyan / Blue
          backgroundColor: 'rgba(2, 132, 199, 0.12)',
          borderWidth: 3,
          pointBackgroundColor: '#0284c7',
          pointBorderColor: '#000000',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8,
          tension: 0.35,
          yAxisID: 'yConfidence'
        },
        {
          label: 'Difficulty Level (1 - 10)',
          data: [currentDifficulty],
          borderColor: '#e11d24', // Crimson Red
          backgroundColor: 'rgba(225, 29, 36, 0.12)',
          borderWidth: 3,
          pointBackgroundColor: '#e11d24',
          pointBorderColor: '#000000',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8,
          tension: 0.35,
          yAxisID: 'yDifficulty'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: { family: "'Plus Jakarta Sans', sans-serif", weight: 'bold', size: 11 },
            color: '#000000',
            boxWidth: 14,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: '#000000',
          titleFont: { family: "'Space Mono', monospace", weight: 'bold' },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif" },
          padding: 8,
          cornerRadius: 6
        }
      },
      scales: {
        x: {
          grid: { color: '#e5e7eb' },
          ticks: { font: { family: "'Space Mono', monospace", weight: 'bold' }, color: '#000000' },
          title: { display: true, text: 'Turns', font: { weight: 'bold', size: 10 }, color: '#4b5563' }
        },
        yConfidence: {
          type: 'linear',
          display: true,
          position: 'left',
          min: 0,
          max: 1.0,
          ticks: { stepSize: 0.2, font: { weight: 'bold' }, color: '#0284c7' },
          title: { display: true, text: 'Confidence (0-1.0)', font: { weight: 'bold', size: 10 }, color: '#0284c7' }
        },
        yDifficulty: {
          type: 'linear',
          display: true,
          position: 'right',
          min: 1,
          max: 10,
          ticks: { stepSize: 2, font: { weight: 'bold' }, color: '#e11d24' },
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Difficulty (1-10)', font: { weight: 'bold', size: 10 }, color: '#e11d24' }
        }
      }
    }
  });
}

function updateLiveReactionUI(turnData, turnIndex) {
  if (!turnData) return;

  // 1. Update Strategy Badge with CSS classes
  const stratBadge = document.getElementById("liveStrategyBadge");
  if (stratBadge) {
    const strat = (turnData.strategy || "maintain").toLowerCase();
    stratBadge.className = "strategy-badge-pill";
    if (strat.includes("push")) stratBadge.classList.add("push");
    else if (strat.includes("pivot")) stratBadge.classList.add("pivot");
    else if (strat.includes("breaking")) stratBadge.classList.add("breaking");
    else if (strat.includes("ease")) stratBadge.classList.add("ease");
    else stratBadge.classList.add("maintain");
    stratBadge.textContent = `STRATEGY: ${(turnData.strategy || "MAINTAIN").toUpperCase()}`;
    stratBadge.title = turnData.strategy_description || "";
  }

  // 2. Update Difficulty & Confidence Badges
  const diffBadge = document.getElementById("liveDifficultyBadge");
  if (diffBadge) {
    diffBadge.textContent = `DIFFICULTY: ${Number(turnData.difficulty).toFixed(1)} / 10`;
  }

  const confBadge = document.getElementById("liveConfidenceBadge");
  if (confBadge) {
    const confVal = Number(turnData.confidence_score || 0);
    confBadge.textContent = `CONFIDENCE: ${(confVal * 100).toFixed(0)}% (${confVal.toFixed(2)})`;
  }

  // 3. Update Signals breakdown
  const sig = turnData.signals || {};
  const lenElem = document.getElementById("signalLength");
  const wordsCount = sig.answer_length_words || sig.length_words || 0;
  if (lenElem) lenElem.textContent = `${wordsCount} words`;
  
  const hedgingElem = document.getElementById("signalHedging");
  const hedgeList = sig.hedging_words || sig.hedging_words_found || [];
  if (hedgingElem) {
    if (hedgeList && hedgeList.length > 0) {
      hedgingElem.textContent = `"${hedgeList.join('", "')}" (-${(hedgeList.length * 0.1).toFixed(1)})`;
      hedgingElem.style.color = '#dc2626';
    } else {
      hedgingElem.textContent = "None (0 words)";
      hedgingElem.style.color = '#15803d';
    }
  }

  const latElem = document.getElementById("signalLatency");
  if (latElem) latElem.textContent = `${sig.latency_seconds || 0}s`;
  
  const contraElem = document.getElementById("signalContradiction");
  if (contraElem) {
    if (sig.contradiction_detected) {
      const reason = sig.contradiction_reason || sig.contradiction_notes || "Conflict detected";
      contraElem.textContent = "🚩 Flagged: " + reason;
      contraElem.style.color = '#dc2626';
    } else {
      contraElem.textContent = "Clear (No conflict)";
      contraElem.style.color = '#15803d';
    }
  }

  // 4. Breaking Point Alert
  const alertBox = document.getElementById("breakingPointAlert");
  const alertText = document.getElementById("breakingPointAlertText");
  if (alertBox && alertText) {
    if (turnData.breaking_point) {
      const weak = turnData.weak_skill_identified || "Core Concept";
      alertText.innerHTML = `<strong>⚠️ BREAKING POINT REACHED:</strong> 3 consecutive low confidence turns detected. Confirmed candidate knowledge limit on <u>${escapeHtml(weak)}</u>. Agent 1 is pivoting away.`;
      alertBox.classList.remove("d-none");
      if (!breakingPointsList.includes(weak)) {
        breakingPointsList.push(weak);
      }
    }
  }

  // 5. Update Chart.js data
  if (liveChart) {
    const turnLabel = `Turn ${turnIndex}`;
    liveChart.data.labels.push(turnLabel);
    liveChart.data.datasets[0].data.push(Number(turnData.confidence_score));
    liveChart.data.datasets[1].data.push(Number(turnData.difficulty));
    liveChart.update();
  }
}

function displayQuestion(index) {
  stopSpeechRecording();

  questionStartTime = Date.now();
  currentQuestionIndex = index;
  const qText = interviewQuestions[index] || "Please describe your background and core technical skills.";

  document.getElementById("questionText").textContent = qText;
  document.getElementById("interviewProgressText").textContent = `Question ${index + 1} of ${interviewQuestions.length}`;
  document.getElementById("candidateAnswerInput").value = "";
  document.getElementById("feedbackContainer").classList.add("d-none");
  document.getElementById("feedbackContent").textContent = "";
  document.getElementById("nextQuestionBtn").classList.add("d-none");
  document.getElementById("submitAnswerBtn").disabled = false;
  document.getElementById("submitAnswerBtn").textContent = "Submit Answer & Evaluate";

  // Subtitle UI
  const subBox = document.getElementById("liveSubtitleBox");
  subBox.classList.remove("active");
  document.getElementById("speechStatusText").textContent = "🎙️ The interviewer is asking the question...";
  document.getElementById("interimLiveText").textContent = "";

  // Play question with natural, warm human voice, then auto-start recording on finish!
  speakQuestionAloud(() => {
    startSpeechRecording();
  });
}

// ----------------- Friendly Microsoft Edge-TTS Audio Engine -----------------
let ttsSharedAudio = null;
let currentPlaybackSessionId = 0;
const ttsPreloadMap = new Map();

function getTtsAudio() {
  if (!ttsSharedAudio) {
    ttsSharedAudio = new Audio();
  }
  return ttsSharedAudio;
}

function updateTtsButtonUI(isPlaying) {
  const btn = document.getElementById("ttsPlayBtn");
  const textElem = document.getElementById("ttsBtnText");
  if (!btn || !textElem) return;

  if (isPlaying) {
    btn.style.backgroundColor = "var(--primary-yellow)";
    textElem.textContent = "Speaking Question...";
  } else {
    btn.style.backgroundColor = "";
    textElem.textContent = "Play Audio (TTS)";
  }
}

function stopCurrentSpeech() {
  currentPlaybackSessionId++; // Invalidate any in-flight playback callbacks immediately
  
  if (ttsSharedAudio) {
    try {
      ttsSharedAudio.pause();
      ttsSharedAudio.removeAttribute("src"); // Immediately cancels network buffer and terminates playback
      ttsSharedAudio.load();
    } catch (e) {}
    ttsSharedAudio.onended = null;
    ttsSharedAudio.onerror = null;
  }

  // Force-cancel any residual browser speech synthesis to eliminate any possibility of overlapping voices
  if ('speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }

  updateTtsButtonUI(false);
}

// Pre-fetches question audio into browser cache so it plays with ZERO delay
function prefetchQuestionAudio(text) {
  if (!text) return;
  const clean = text.trim();
  if (!clean || ttsPreloadMap.has(clean)) return;

  const url = `/api/tts/stream?text=${encodeURIComponent(clean)}&voice=en-US-AriaNeural`;
  const preloader = new Audio();
  preloader.preload = "auto";
  preloader.src = url;
  ttsPreloadMap.set(clean, url);
}

function speakQuestionAloud(onFinish) {
  const text = (document.getElementById("questionText").textContent || "").trim();
  if (!text) {
    if (onFinish) onFinish();
    return;
  }

  // 1. Completely halt and abort any previous speech or audio stream
  stopCurrentSpeech();

  const thisSessionId = currentPlaybackSessionId;
  const audio = getTtsAudio();
  const streamUrl = `/api/tts/stream?text=${encodeURIComponent(text)}&voice=en-US-AriaNeural`;

  let hasEnded = false;
  const finishPlayback = () => {
    if (hasEnded) return;
    hasEnded = true;
    if (thisSessionId !== currentPlaybackSessionId) return;

    updateTtsButtonUI(false);
    if (onFinish) onFinish();
  };

  audio.onended = () => {
    finishPlayback();
  };

  audio.onerror = (e) => {
    if (thisSessionId !== currentPlaybackSessionId) return;
    console.warn("Edge-TTS stream notice:", e);
    finishPlayback();
  };

  try {
    audio.src = streamUrl;
    updateTtsButtonUI(true);

    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          if (thisSessionId !== currentPlaybackSessionId) {
            try { audio.pause(); } catch (e) {}
          }
        })
        .catch((err) => {
          // If aborted by stopCurrentSpeech() or user clicked again, do not treat as error
          if (err.name === 'AbortError' || thisSessionId !== currentPlaybackSessionId) {
            return;
          }
          if (err.name === 'NotAllowedError') {
            console.log("Autoplay waiting for user gesture. Candidate can click 'Play Audio (TTS)'.");
            updateTtsButtonUI(false);
            return;
          }
          console.warn("Edge-TTS play notice:", err);
          finishPlayback();
        });
    }
  } catch (err) {
    console.warn("Exception playing Edge-TTS:", err);
    finishPlayback();
  }
}

function speakCurrentQuestion() {
  stopSpeechRecording();
  speakQuestionAloud(() => {
    startSpeechRecording();
  });
}

// ----------------- Speech-to-Text Live Subtitles & Recording -----------------
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onresult = (event) => {
    let interimTranscript = "";
    let finalTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }

    const subBox = document.getElementById("liveSubtitleBox");
    subBox.classList.add("active");

    if (interimTranscript) {
      document.getElementById("speechStatusText").textContent = "Listening: ";
      document.getElementById("interimLiveText").textContent = `"${interimTranscript}"`;
    }

    if (finalTranscript) {
      const input = document.getElementById("candidateAnswerInput");
      input.value = (input.value + " " + finalTranscript).trim();
      document.getElementById("speechStatusText").textContent = "Captured: ";
      document.getElementById("interimLiveText").textContent = `"${finalTranscript.trim()}"`;
    }
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition notice:", event.error);
    if (event.error === 'not-allowed') {
      stopRecordingUI();
      document.getElementById("speechStatusText").textContent = "🎙️ Microphone waiting for permission. Click 'Record Voice' above or type your answer.";
    } else if (event.error === 'no-speech') {
      // Don't cancel recording UI on brief pause in speaking
      if (isRecording) {
        document.getElementById("speechStatusText").innerHTML = '<span class="recording-indicator"></span><strong>Still listening...</strong> Speak your answer:';
      }
    } else {
      stopRecordingUI();
    }
  };

  recognition.onend = () => {
    // If recording state is still active, automatically reconnect so candidate isn't cut off
    if (isRecording) {
      try {
        recognition.start();
        return;
      } catch (e) {}
    }

    stopRecordingUI();
    const curVal = document.getElementById("candidateAnswerInput").value.trim();
    if (!curVal) {
      document.getElementById("speechStatusText").textContent = "No voice detected. You can speak again, type, or click 'Auto-write Suggested Answer'.";
    } else {
      document.getElementById("speechStatusText").textContent = "Voice captured! Review your answer below and click Submit.";
    }
  };
}

function startSpeechRecording() {
  if (!recognition) return;
  if (isRecording) return;

  try {
    recognition.start();
    isRecording = true;
    const btn = document.getElementById("micToggleBtn");
    if (btn) {
      btn.classList.add("recording");
      document.getElementById("micBtnText").textContent = "Stop Recording";
    }
    const subBox = document.getElementById("liveSubtitleBox");
    subBox.classList.add("active");
    document.getElementById("speechStatusText").innerHTML = '<span class="recording-indicator"></span><strong>Recording actively...</strong> Speak your answer:';
    document.getElementById("interimLiveText").textContent = "";
  } catch (e) {
    // If recognition is already starting or running
    if (e.name !== "InvalidStateError") {
      stopRecordingUI();
      document.getElementById("speechStatusText").textContent = "🎙️ Click 'Record Voice' above or type your answer.";
    }
  }
}

function stopSpeechRecording() {
  isRecording = false;
  if (recognition) {
    try {
      recognition.stop();
    } catch (e) {}
  }
  stopRecordingUI();
}

function toggleSpeechRecording() {
  if (isRecording) {
    stopSpeechRecording();
  } else {
    startSpeechRecording();
  }
}

function stopRecordingUI() {
  isRecording = false;
  const btn = document.getElementById("micToggleBtn");
  if (btn) {
    btn.classList.remove("recording");
    document.getElementById("micBtnText").textContent = "Record Voice";
  }
}

// ----------------- Auto-Write Suggested Answer -----------------
async function autoWriteSuggestedAnswer() {
  stopSpeechRecording();
  const qText = document.getElementById("questionText").textContent;
  const btn = document.getElementById("autoWriteBtn");
  const origText = btn.textContent;

  btn.disabled = true;
  btn.textContent = "Generating Answer...";

  try {
    const res = await API.post("/api/interview/suggest_answer", {
      question: qText,
      answer: ""
    });

    if (res && res.suggested_answer) {
      document.getElementById("candidateAnswerInput").value = res.suggested_answer;
      document.getElementById("speechStatusText").textContent = "Suggested response generated! You can modify it or submit.";
      document.getElementById("interimLiveText").textContent = "";
    }
  } catch (err) {
    showAlert("Failed to auto-generate answer. Please type directly into the box.");
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

// ----------------- Submit Answer via Dual-Agent Reaction Matrix -----------------
async function submitCurrentAnswer() {
  stopCurrentSpeech();
  stopSpeechRecording();
  hideAlert();

  const answer = document.getElementById("candidateAnswerInput").value.trim();
  if (!answer) {
    showAlert("Please speak your answer or type your response before submitting.");
    return;
  }

  const question = interviewQuestions[currentQuestionIndex] || "Interview Question";
  const submitBtn = document.getElementById("submitAnswerBtn");

  submitBtn.disabled = true;
  submitBtn.textContent = "Agent 2 & Agent 1 Analyzing...";

  // Calculate response latency in seconds
  const elapsed = (Date.now() - questionStartTime) / 1000;
  const latencySeconds = Math.max(1, Math.round(elapsed * 10) / 10);

  try {
    const turnRes = await API.post("/api/interview/turn", {
      question: question,
      answer: answer,
      current_difficulty: currentDifficulty,
      latency_seconds: latencySeconds,
      target_role: targetRole,
      matching_skills: matchingSkills,
      missing_skills: missingSkills,
      resume_text: resumeText,
      history: turnsHistory
    });

    const turnNumber = turnsHistory.length + 1;

    // Record turn in turnsHistory
    turnsHistory.push({
      turn: turnNumber,
      question: question,
      answer: answer,
      confidence: turnRes.confidence_score,
      difficulty: turnRes.difficulty,
      latency_seconds: latencySeconds,
      strategy: turnRes.strategy,
      breaking_point: turnRes.breaking_point,
      weak_skill: turnRes.weak_skill_identified
    });

    // Record in summary for final report generator
    interviewSummary.push({
      q_no: currentQuestionIndex + 1,
      question: question,
      answer: answer
    });

    // Update real-time Live UI and Graph
    updateLiveReactionUI(turnRes, turnNumber);

    // Save next question and new difficulty
    currentDifficulty = turnRes.difficulty;
    nextAdaptiveQuestion = turnRes.next_question;
    if (nextAdaptiveQuestion) {
      prefetchQuestionAudio(nextAdaptiveQuestion);
    }

    // Display feedback
    document.getElementById("feedbackContent").textContent = turnRes.feedback;
    document.getElementById("feedbackContainer").classList.remove("d-none");

    const nextBtn = document.getElementById("nextQuestionBtn");
    nextBtn.textContent = "Next Adaptive Question →";
    nextBtn.classList.remove("d-none");
  } catch (err) {
    showAlert(err.message || "Failed to evaluate answer through interview agent.");
    submitBtn.disabled = false;
  } finally {
    submitBtn.textContent = "Answer Submitted";
  }
}

function goToNextQuestion() {
  if (nextAdaptiveQuestion) {
    // Splice in the next adaptive question chosen by Agent 1
    interviewQuestions.splice(currentQuestionIndex + 1, 0, nextAdaptiveQuestion);
    nextAdaptiveQuestion = null;
  }

  if (currentQuestionIndex + 1 < interviewQuestions.length && turnsHistory.length < 12) {
    displayQuestion(currentQuestionIndex + 1);
  } else {
    completeInterviewSession();
  }
}

async function finishInterviewEarly() {
  stopCurrentSpeech();
  stopSpeechRecording();

  const curAns = document.getElementById("candidateAnswerInput").value.trim();
  if (curAns && (!interviewSummary.length || interviewSummary[interviewSummary.length - 1].q_no !== currentQuestionIndex + 1)) {
    interviewSummary.push({
      q_no: currentQuestionIndex + 1,
      question: interviewQuestions[currentQuestionIndex] || "Question",
      answer: curAns
    });
  }

  if (interviewSummary.length === 0 && turnsHistory.length === 0) {
    showAlert("Please answer at least one question before generating your assessment report.");
    return;
  }

  if (confirm("Are you ready to complete the interview now and generate your final assessment report in SQL?")) {
    await completeInterviewSession();
  }
}

async function completeInterviewSession() {
  hideAlert();
  stopSpeechRecording();

  const nextBtn = document.getElementById("nextQuestionBtn");
  if (nextBtn) {
    nextBtn.disabled = true;
    nextBtn.textContent = "Saving Report to SQL...";
  }

  const avgConf = turnsHistory.length > 0
    ? turnsHistory.reduce((acc, t) => acc + (Number(t.confidence) || 0), 0) / turnsHistory.length
    : 0.5;

  const peakDiff = turnsHistory.length > 0
    ? Math.max(...turnsHistory.map(t => Number(t.difficulty) || 5))
    : currentDifficulty;

  try {
    const reportRes = await API.post("/api/interview/finish", {
      summary_data: interviewSummary,
      turns_data: turnsHistory,
      breaking_points: breakingPointsList,
      avg_confidence: Math.round(avgConf * 100) / 100,
      peak_difficulty: Math.round(peakDiff * 10) / 10
    });

    // Display Report Card
    document.getElementById("reportScore").textContent = `${reportRes.Score}/100`;
    document.getElementById("reportAccuracy").textContent = `${reportRes.Accuracy}%`;
    document.getElementById("reportBlunder").textContent = reportRes.Blunder;
    document.getElementById("reportConfidence").textContent = reportRes.Confidence;
    document.getElementById("reportStreak").textContent = reportRes.Streak;
    document.getElementById("reportCommunication").textContent = reportRes.Communication;

    // Trajectory badges
    const finalPeakElem = document.getElementById("finalPeakDiffBadge");
    if (finalPeakElem) finalPeakElem.textContent = `PEAK DIFF: ${Number(peakDiff).toFixed(1)} / 10`;

    const finalAvgElem = document.getElementById("finalAvgConfBadge");
    if (finalAvgElem) finalAvgElem.textContent = `AVG CONF: ${(avgConf * 100).toFixed(0)}%`;

    // Render Final Session Trajectory Chart
    renderFinalSessionChart(turnsHistory);

    // Breaking Points List
    const bpBox = document.getElementById("finalBreakingPointsContainer");
    if (bpBox) {
      if (breakingPointsList.length > 0) {
        bpBox.innerHTML = `
          <div style="background-color: #fee2e2; border: 2px solid #dc2626; border-radius: 8px; padding: 0.75rem 1rem; color: #991b1b; font-weight: 700; font-size: 0.85rem;">
            <strong>⚠️ Identified Breaking Points (${breakingPointsList.length}):</strong>
            <ul style="margin: 0.4rem 0 0 1.2rem;">
              ${breakingPointsList.map(bp => `<li>${escapeHtml(bp)} (3 consecutive low-confidence answers)</li>`).join('')}
            </ul>
          </div>
        `;
      } else {
        bpBox.innerHTML = `
          <div style="background-color: #dcfce7; border: 2px solid #16a34a; border-radius: 8px; padding: 0.75rem 1rem; color: #166534; font-weight: 700; font-size: 0.85rem;">
            ✅ <strong>No Breaking Points Hit:</strong> Maintained stable confidence across all tested difficulty levels.
          </div>
        `;
      }
    }

    document.getElementById("questionCard").classList.add("d-none");
    document.getElementById("reportSection").classList.remove("d-none");
    document.getElementById("reportSection").scrollIntoView({ behavior: 'smooth' });

    showAlert("Interview completed! Your performance report and dual-agent curve have been saved into SQL.", true);
  } catch (err) {
    showAlert(err.message || "Failed to generate and save final assessment report.");
  }
}

function renderFinalSessionChart(historyData) {
  const canvas = document.getElementById("finalSessionChart");
  if (!canvas || typeof Chart === "undefined") return;

  const labels = (historyData && historyData.length > 0)
    ? historyData.map(h => `Turn ${h.turn}`)
    : ['Turn 1'];

  const confData = (historyData && historyData.length > 0)
    ? historyData.map(h => Number(h.confidence))
    : [0.5];

  const diffData = (historyData && historyData.length > 0)
    ? historyData.map(h => Number(h.difficulty))
    : [5.0];

  const ctx = canvas.getContext("2d");
  if (finalChart) {
    finalChart.destroy();
  }

  finalChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Candidate Confidence (0.0 - 1.0)',
          data: confData,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.15)',
          borderWidth: 3,
          pointRadius: 6,
          pointBackgroundColor: '#0284c7',
          tension: 0.35,
          yAxisID: 'yConf'
        },
        {
          label: 'Interrogator Difficulty (1 - 10)',
          data: diffData,
          borderColor: '#e11d24',
          backgroundColor: 'rgba(225, 29, 36, 0.15)',
          borderWidth: 3,
          pointRadius: 6,
          pointBackgroundColor: '#e11d24',
          tension: 0.35,
          yAxisID: 'yDiff'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { font: { family: "'Space Mono', monospace", weight: 'bold' } }
        },
        yConf: {
          type: 'linear',
          position: 'left',
          min: 0,
          max: 1.0,
          ticks: { stepSize: 0.2, color: '#0284c7', font: { weight: 'bold' } },
          title: { display: true, text: 'Confidence', color: '#0284c7', font: { weight: 'bold' } }
        },
        yDiff: {
          type: 'linear',
          position: 'right',
          min: 1,
          max: 10,
          ticks: { stepSize: 2, color: '#e11d24', font: { weight: 'bold' } },
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Difficulty', color: '#e11d24', font: { weight: 'bold' } }
        }
      }
    }
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
