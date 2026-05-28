import { CHALLENGES, LEVELS } from "./challenges.js";
import { buildRoundDeck, calculateRoundScore, createShareText, evaluateAnswer, getLevel } from "./gameLogic.js";

const STORAGE_KEY = "emoji-oracle-state-v1";
const LEADERBOARD_KEY = "emoji-oracle-leaderboard-v1";
const ROUND_SECONDS = 40;

const els = {
  playerName: document.querySelector("#playerName"),
  modeSelect: document.querySelector("#modeSelect"),
  levelSelect: document.querySelector("#levelSelect"),
  startBtn: document.querySelector("#startBtn"),
  promptCard: document.querySelector("#promptCard"),
  promptLabel: document.querySelector("#promptLabel"),
  promptValue: document.querySelector("#promptValue"),
  levelBadge: document.querySelector("#levelBadge"),
  modeBadge: document.querySelector("#modeBadge"),
  answerForm: document.querySelector("#answerForm"),
  answerInput: document.querySelector("#answerInput"),
  speakBtn: document.querySelector("#speakBtn"),
  hintBtn: document.querySelector("#hintBtn"),
  skipBtn: document.querySelector("#skipBtn"),
  feedback: document.querySelector("#feedback"),
  lesson: document.querySelector("#lesson"),
  score: document.querySelector("#score"),
  streak: document.querySelector("#streak"),
  timer: document.querySelector("#timer"),
  progress: document.querySelector("#progress"),
  progressFill: document.querySelector("#progressFill"),
  leaderboard: document.querySelector("#leaderboard"),
  shareBtn: document.querySelector("#shareBtn"),
  resetBtn: document.querySelector("#resetBtn"),
  challengeCount: document.querySelector("#challengeCount"),
  toast: document.querySelector("#toast"),
  demoBtn: document.querySelector("#demoBtn"),
  demoModal: document.querySelector("#demoModal"),
  demoVideo: document.querySelector("#demoVideo"),
  demoCloseBtn: document.querySelector("#demoCloseBtn"),
  demoModalBackdrop: document.querySelector(".demo-modal-backdrop")
};

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isListening = false;
let timerId;
let state = {
  deck: [],
  index: 0,
  score: 0,
  streak: 0,
  bestStreak: 0,
  secondsRemaining: ROUND_SECONDS,
  usedHint: false,
  active: false
};

function loadJson(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    playerName: els.playerName.value,
    mode: els.modeSelect.value,
    level: els.levelSelect.value
  }));
}

function restorePreferences() {
  const saved = loadJson(STORAGE_KEY, {});
  els.playerName.value = saved.playerName ?? "";
  els.modeSelect.value = saved.mode ?? "mixed";
  els.levelSelect.value = saved.level ?? "all";
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("show");
  window.setTimeout(() => els.toast.classList.remove("show"), 2600);
}

function getCurrentChallenge() {
  return state.deck[state.index];
}

function renderStats() {
  els.score.textContent = state.score.toLocaleString();
  els.streak.textContent = `${state.streak}x`;
  els.timer.textContent = `${state.secondsRemaining}s`;
  els.challengeCount.textContent = `${Math.min(state.index + 1, state.deck.length)} / ${state.deck.length || CHALLENGES.length}`;
  const progress = state.deck.length ? ((state.index) / state.deck.length) * 100 : 0;
  els.progressFill.style.width = `${Math.min(progress, 100)}%`;
  els.progress.setAttribute("aria-valuenow", String(Math.round(progress)));
}

function renderChallenge() {
  const challenge = getCurrentChallenge();

  if (!challenge) {
    finishGame();
    return;
  }

  const level = getLevel(challenge.level);
  state.secondsRemaining = ROUND_SECONDS;
  state.usedHint = false;
  els.promptLabel.textContent = challenge.promptLabel;
  els.promptValue.textContent = challenge.prompt;
  els.levelBadge.textContent = `${level.emoji} ${level.label}`;
  els.modeBadge.textContent = challenge.mode === "emoji-to-text" ? "Emoji → Message" : "Message → Emoji";
  els.answerInput.value = "";
  els.answerInput.placeholder = challenge.mode === "emoji-to-text" ? "Type or speak the message..." : "Type or speak emojis...";
  els.feedback.textContent = "Translate the clue. Use hint only if you need it.";
  els.feedback.className = "feedback neutral";
  els.lesson.textContent = level.description;
  els.answerInput.focus();
  renderStats();
  restartTimer();
}

function restartTimer() {
  window.clearInterval(timerId);
  timerId = window.setInterval(() => {
    if (!state.active) return;
    state.secondsRemaining -= 1;
    renderStats();
    if (state.secondsRemaining <= 0) {
      window.clearInterval(timerId);
      markIncorrect("Time! The round moved on, but your streak can rebuild quickly.");
    }
  }, 1000);
}

function startGame() {
  saveState();
  state = {
    deck: buildRoundDeck({ mode: els.modeSelect.value, level: els.levelSelect.value }),
    index: 0,
    score: 0,
    streak: 0,
    bestStreak: 0,
    secondsRemaining: ROUND_SECONDS,
    usedHint: false,
    active: true
  };

  if (!state.deck.length) {
    state.deck = buildRoundDeck();
  }

  els.promptCard.classList.remove("is-idle");
  els.answerInput.disabled = false;
  els.speakBtn.disabled = !SpeechRecognition;
  els.hintBtn.disabled = false;
  els.skipBtn.disabled = false;
  els.shareBtn.disabled = false;
  showToast("Game on. Decode fast, learn faster!");
  renderChallenge();
}

function nextChallenge(delay = 1050) {
  window.clearInterval(timerId);
  window.setTimeout(() => {
    state.index += 1;
    renderChallenge();
  }, delay);
}

function markCorrect(challenge, confidence) {
  const earned = calculateRoundScore({
    challenge,
    streak: state.streak + 1,
    secondsRemaining: state.secondsRemaining,
    usedHint: state.usedHint
  });
  state.score += earned;
  state.streak += 1;
  state.bestStreak = Math.max(state.bestStreak, state.streak);
  els.feedback.textContent = `Correct! +${earned} points • confidence ${Math.round(confidence * 100)}%`;
  els.feedback.className = "feedback success";
  els.lesson.textContent = challenge.lesson;
  renderStats();
  nextChallenge();
}

function markIncorrect(message = "Not quite. Look at the pattern, learn the clue, then try the next one.") {
  const challenge = getCurrentChallenge();
  state.streak = 0;
  els.feedback.textContent = message;
  els.feedback.className = "feedback danger";
  els.lesson.textContent = challenge ? `${challenge.lesson} Accepted examples: ${challenge.answers.slice(0, 2).join(" • ")}` : "";
  renderStats();
  nextChallenge(1600);
}

function finishGame() {
  state.active = false;
  window.clearInterval(timerId);
  saveLeaderboard();
  els.progressFill.style.width = "100%";
  els.feedback.textContent = `Round complete! Final score: ${state.score.toLocaleString()} • Best streak: ${state.bestStreak}x`;
  els.feedback.className = "feedback success";
  els.lesson.textContent = "Replay with a harder level or switch modes to build true emoji fluency.";
  els.answerInput.disabled = true;
  els.speakBtn.disabled = true;
  els.hintBtn.disabled = true;
  els.skipBtn.disabled = true;
  renderStats();
  renderLeaderboard();
}

function saveLeaderboard() {
  const board = loadJson(LEADERBOARD_KEY, []);
  const entry = {
    name: els.playerName.value.trim() || "Guest Oracle",
    score: state.score,
    streak: state.bestStreak,
    date: new Date().toISOString()
  };
  const updated = [...board, entry]
    .sort((a, b) => b.score - a.score || b.streak - a.streak || new Date(b.date) - new Date(a.date))
    .slice(0, 8);
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(updated));
}

function renderLeaderboard() {
  const board = loadJson(LEADERBOARD_KEY, []);
  els.leaderboard.innerHTML = board.length
    ? board.map((entry, index) => `
      <li>
        <span class="rank">#${index + 1}</span>
        <strong>${escapeHtml(entry.name)}</strong>
        <span>${Number(entry.score).toLocaleString()} pts</span>
        <small>${entry.streak}x streak</small>
      </li>
    `).join("")
    : `<li class="empty">No scores yet. Be the first emoji legend.</li>`;
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;"
  }[char]));
}

function submitAnswer(event) {
  event.preventDefault();
  if (!state.active) {
    startGame();
    return;
  }

  const challenge = getCurrentChallenge();
  const answer = els.answerInput.value.trim();
  if (!answer) {
    showToast("Add an answer first. Your best guess still teaches your brain.");
    return;
  }

  const result = evaluateAnswer(answer, challenge);
  if (result.isCorrect) {
    markCorrect(challenge, result.confidence);
  } else {
    markIncorrect("Creative answer, but not close enough for this clue.");
  }
}

function showHint() {
  if (!state.active) return;
  const challenge = getCurrentChallenge();
  if (!challenge) return;
  state.usedHint = true;
  els.lesson.textContent = `Hint: ${challenge.hint}`;
  els.hintBtn.disabled = true;
  showToast("Hint used: small point penalty, big learning boost.");
}

function skipChallenge() {
  markIncorrect("Skipped. Study the lesson, then win the next prompt.");
}

function setupSpeech() {
  if (!SpeechRecognition) {
    els.speakBtn.disabled = true;
    els.speakBtn.title = "Speech recognition is not supported in this browser.";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.addEventListener("start", () => {
    isListening = true;
    els.speakBtn.classList.add("listening");
    els.speakBtn.textContent = "Listening…";
  });
  recognition.addEventListener("end", () => {
    isListening = false;
    els.speakBtn.classList.remove("listening");
    els.speakBtn.textContent = "🎙 Speak";
  });
  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;
    els.answerInput.value = transcript;
    showToast(`Heard: ${transcript}`);
  });
  recognition.addEventListener("error", () => {
    isListening = false;
    showToast("Speech did not connect. Typing works perfectly too.");
  });
}

async function shareScore() {
  const text = createShareText({ score: state.score, streak: state.bestStreak || state.streak, playerName: els.playerName.value });
  if (navigator.share) {
    await navigator.share({ title: "Emoji Oracle", text }).catch(() => undefined);
  } else if (navigator.clipboard) {
    await navigator.clipboard.writeText(text);
    showToast("Share text copied to clipboard.");
  } else {
    showToast(text);
  }
}

function resetLeaderboard() {
  localStorage.removeItem(LEADERBOARD_KEY);
  renderLeaderboard();
  showToast("Leaderboard reset on this device.");
}

function openDemo() {
  els.demoModal.hidden = false;
  els.demoVideo.play().catch(() => undefined);
  document.addEventListener("keydown", handleDemoKey);
}

function closeDemo() {
  els.demoModal.hidden = true;
  els.demoVideo.pause();
  els.demoVideo.currentTime = 0;
  document.removeEventListener("keydown", handleDemoKey);
}

function handleDemoKey(event) {
  if (event.key === "Escape") closeDemo();
}

function bindEvents() {
  els.startBtn.addEventListener("click", startGame);
  els.answerForm.addEventListener("submit", submitAnswer);
  els.hintBtn.addEventListener("click", showHint);
  els.skipBtn.addEventListener("click", skipChallenge);
  els.shareBtn.addEventListener("click", shareScore);
  els.resetBtn.addEventListener("click", resetLeaderboard);
  els.speakBtn.addEventListener("click", () => { if (!isListening) recognition?.start(); });
  els.demoBtn.addEventListener("click", openDemo);
  els.demoCloseBtn.addEventListener("click", closeDemo);
  els.demoModalBackdrop.addEventListener("click", closeDemo);
  [els.playerName, els.modeSelect, els.levelSelect].forEach((el) => el.addEventListener("change", saveState));
}

restorePreferences();
setupSpeech();
bindEvents();
renderLeaderboard();
renderStats();
