import test from "node:test";
import assert from "node:assert/strict";
import { calculateRoundScore, createShareText, evaluateAnswer, normalizeAnswer, similarityScore } from "../src/gameLogic.js";

const challenge = {
  level: "rookie",
  answers: ["i love pizza", "love pizza", "pizza love"]
};

test("normalizeAnswer removes spacing, punctuation, and emoji variation selectors", () => {
  assert.equal(normalizeAnswer(" I ❤️ Pizza!!! "), "i❤pizza");
  assert.equal(normalizeAnswer("☕️"), "☕");
});

test("evaluateAnswer accepts exact and close phrase matches", () => {
  assert.equal(evaluateAnswer("I love pizza", challenge).isCorrect, true);
  assert.equal(evaluateAnswer("love pizza!", challenge).isCorrect, true);
  assert.equal(evaluateAnswer("I want tacos", challenge).isCorrect, false);
});

test("similarityScore handles partial token overlap", () => {
  assert.equal(similarityScore("running very late", "running late") >= 0.66, true);
});

test("calculateRoundScore rewards speed and penalizes hints without going below floor", () => {
  const noHint = calculateRoundScore({ challenge, streak: 2, secondsRemaining: 20, usedHint: false });
  const withHint = calculateRoundScore({ challenge, streak: 2, secondsRemaining: 20, usedHint: true });
  assert.equal(noHint > withHint, true);
  assert.equal(calculateRoundScore({ challenge, usedHint: true }) >= 25, true);
});

test("createShareText includes player, score, and streak", () => {
  const text = createShareText({ score: 900, streak: 4, playerName: "Ksg" });
  assert.match(text, /Ksg/);
  assert.match(text, /900/);
  assert.match(text, /4x/);
});
