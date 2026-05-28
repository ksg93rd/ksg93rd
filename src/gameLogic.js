import { CHALLENGES, LEVELS } from "./challenges.js";

const COMBINING_MARKS = /[\uFE0E\uFE0F]/g;
const SKIN_TONE_MODIFIERS = /[\u{1F3FB}-\u{1F3FF}]/gu;
const PUNCTUATION = /[.,!?;:'"`~()[\]{}<>/_\\|-]/g;
const WHITESPACE = /\s+/g;

export function normalizeAnswer(value = "") {
  return value
    .toString()
    .toLowerCase()
    .replace(COMBINING_MARKS, "")
    .replace(SKIN_TONE_MODIFIERS, "")
    .replace(/&/g, "and")
    .replace(PUNCTUATION, " ")
    .replace(WHITESPACE, "")
    .trim();
}

export function normalizePhrase(value = "") {
  return value
    .toString()
    .toLowerCase()
    .replace(COMBINING_MARKS, "")
    .replace(SKIN_TONE_MODIFIERS, "")
    .replace(/&/g, "and")
    .replace(PUNCTUATION, " ")
    .replace(WHITESPACE, " ")
    .trim();
}

export function tokenize(value = "") {
  return normalizePhrase(value).split(" ").filter(Boolean);
}

export function similarityScore(input, answer) {
  const normalizedInput = normalizeAnswer(input);
  const normalizedAnswer = normalizeAnswer(answer);

  if (!normalizedInput || !normalizedAnswer) return 0;
  if (normalizedInput === normalizedAnswer) return 1;
  if (normalizedInput.includes(normalizedAnswer) || normalizedAnswer.includes(normalizedInput)) return 0.88;

  const inputTokens = new Set(tokenize(input));
  const answerTokens = new Set(tokenize(answer));
  if (!inputTokens.size || !answerTokens.size) return 0;

  const matches = [...answerTokens].filter((token) => inputTokens.has(token)).length;
  return matches / Math.max(answerTokens.size, inputTokens.size);
}

export function evaluateAnswer(input, challenge) {
  const bestScore = Math.max(...challenge.answers.map((answer) => similarityScore(input, answer)));
  return {
    isCorrect: bestScore >= 0.72,
    confidence: Number(bestScore.toFixed(2))
  };
}

export function getLevel(levelId) {
  return LEVELS.find((level) => level.id === levelId) ?? LEVELS[0];
}

export function calculateRoundScore({ challenge, streak = 0, secondsRemaining = 0, usedHint = false }) {
  const level = getLevel(challenge.level);
  const streakBonus = Math.min(streak, 5) * 18;
  const speedBonus = Math.max(0, secondsRemaining) * 3;
  const hintPenalty = usedHint ? 35 : 0;
  return Math.max(25, level.points + streakBonus + speedBonus - hintPenalty);
}

export function buildRoundDeck({ mode = "mixed", level = "all" } = {}) {
  const filtered = CHALLENGES.filter((challenge) => {
    const modeMatches = mode === "mixed" || challenge.mode === mode;
    const levelMatches = level === "all" || challenge.level === level;
    return modeMatches && levelMatches;
  });

  return [...filtered].sort(() => Math.random() - 0.5);
}

export function createShareText({ score, streak, playerName }) {
  const safeName = playerName?.trim() || "Emoji Oracle";
  return `${safeName} scored ${score} with a ${streak}x streak in Emoji Oracle! Can you decode emojis faster?`;
}
