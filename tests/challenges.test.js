import test from "node:test";
import assert from "node:assert/strict";
import { CHALLENGES, LEVELS } from "../src/challenges.js";
import { buildRoundDeck, getLevel } from "../src/gameLogic.js";

const VALID_MODES = new Set(["emoji-to-text", "text-to-emoji"]);
const levelIds = new Set(LEVELS.map((level) => level.id));

test("challenge catalog has unique ids and complete playable content", () => {
  const ids = new Set();

  for (const challenge of CHALLENGES) {
    assert.equal(ids.has(challenge.id), false, `duplicate challenge id: ${challenge.id}`);
    ids.add(challenge.id);
    assert.equal(VALID_MODES.has(challenge.mode), true, `${challenge.id} has an invalid mode`);
    assert.equal(levelIds.has(challenge.level), true, `${challenge.id} has an invalid level`);
    assert.equal(challenge.prompt.trim().length > 0, true, `${challenge.id} needs a prompt`);
    assert.equal(challenge.promptLabel.trim().length > 0, true, `${challenge.id} needs a prompt label`);
    assert.equal(challenge.hint.trim().length > 0, true, `${challenge.id} needs a hint`);
    assert.equal(challenge.lesson.trim().length > 0, true, `${challenge.id} needs a lesson`);
    assert.equal(Array.isArray(challenge.answers), true, `${challenge.id} answers must be an array`);
    assert.equal(challenge.answers.length >= 3, true, `${challenge.id} needs at least 3 accepted answers`);
  }
});

test("every difficulty supports both game directions", () => {
  for (const level of LEVELS) {
    const modesForLevel = new Set(
      CHALLENGES.filter((challenge) => challenge.level === level.id).map((challenge) => challenge.mode)
    );
    assert.equal(modesForLevel.has("emoji-to-text"), true, `${level.id} needs emoji-to-text challenges`);
    assert.equal(modesForLevel.has("text-to-emoji"), true, `${level.id} needs text-to-emoji challenges`);
  }
});

test("deck builder filters by mode and difficulty", () => {
  for (const mode of VALID_MODES) {
    const deck = buildRoundDeck({ mode, level: "all" });
    assert.equal(deck.length > 0, true, `${mode} deck should not be empty`);
    assert.equal(deck.every((challenge) => challenge.mode === mode), true, `${mode} deck should only include ${mode}`);
  }

  for (const level of LEVELS) {
    const deck = buildRoundDeck({ mode: "mixed", level: level.id });
    assert.equal(deck.length > 0, true, `${level.id} deck should not be empty`);
    assert.equal(deck.every((challenge) => challenge.level === level.id), true, `${level.id} deck should only include ${level.id}`);
  }
});

test("unknown levels fall back safely", () => {
  assert.equal(getLevel("missing-level").id, LEVELS[0].id);
});
