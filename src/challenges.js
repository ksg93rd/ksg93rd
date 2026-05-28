export const LEVELS = [
  {
    id: "rookie",
    label: "Rookie",
    emoji: "🌱",
    description: "Friendly prompts with obvious clues.",
    points: 100
  },
  {
    id: "spark",
    label: "Spark",
    emoji: "⚡",
    description: "Short phrases and playful twists.",
    points: 160
  },
  {
    id: "pro",
    label: "Pro",
    emoji: "🚀",
    description: "Harder idioms, feelings, and context clues.",
    points: 240
  }
];

export const CHALLENGES = [
  {
    id: "e-001",
    mode: "emoji-to-text",
    level: "rookie",
    prompt: "☀️😄",
    promptLabel: "Decode this emoji message",
    answers: ["happy day", "sunny day", "good morning", "bright and happy", "feeling happy"],
    hint: "Think of a positive day with sunshine.",
    lesson: "Emoji messages often combine emotion + context. ☀️ adds brightness; 😄 adds joy."
  },
  {
    id: "e-002",
    mode: "emoji-to-text",
    level: "rookie",
    prompt: "🍕❤️",
    promptLabel: "Decode this emoji message",
    answers: ["i love pizza", "love pizza", "pizza love", "i like pizza"],
    hint: "The heart shows affection for the food.",
    lesson: "A heart can mean love, like, favorite, or support depending on the noun beside it."
  },
  {
    id: "e-003",
    mode: "emoji-to-text",
    level: "spark",
    prompt: "📚🔥🧠",
    promptLabel: "Decode this emoji message",
    answers: ["study hard", "learning intensely", "brain on fire", "smart studying", "power study"],
    hint: "Books + fire + brain points toward intense learning.",
    lesson: "Abstract emojis like 🔥 can mean excellence, intensity, or excitement."
  },
  {
    id: "e-004",
    mode: "emoji-to-text",
    level: "spark",
    prompt: "⏰🏃‍♀️💨",
    promptLabel: "Decode this emoji message",
    answers: ["running late", "late", "in a hurry", "rushing", "hurry up"],
    hint: "A clock and fast running usually means time pressure.",
    lesson: "Motion marks such as 💨 can turn a simple action into urgency."
  },
  {
    id: "e-005",
    mode: "emoji-to-text",
    level: "pro",
    prompt: "🌧️➡️🌈",
    promptLabel: "Decode this emoji message",
    answers: ["after the rain comes a rainbow", "better days ahead", "hope after hard times", "things get better", "rainbow after rain"],
    hint: "This is a hopeful phrase about trouble turning into beauty.",
    lesson: "Emoji stories can express metaphors, not just literal objects."
  },
  {
    id: "t-001",
    mode: "text-to-emoji",
    level: "rookie",
    prompt: "I am happy",
    promptLabel: "Reply with emojis that mean this",
    answers: ["😄", "😀", "😊", "😁", "🙂"],
    hint: "Use a smiling face.",
    lesson: "There are many valid emotional emojis; tone decides which one fits best."
  },
  {
    id: "t-002",
    mode: "text-to-emoji",
    level: "rookie",
    prompt: "Time for coffee",
    promptLabel: "Reply with emojis that mean this",
    answers: ["☕", "⏰☕", "☕⏰", "🕒☕", "☕️"],
    hint: "A cup emoji is the core idea.",
    lesson: "Use one clear anchor emoji, then add context if needed."
  },
  {
    id: "t-003",
    mode: "text-to-emoji",
    level: "spark",
    prompt: "Movie night with friends",
    promptLabel: "Reply with emojis that mean this",
    answers: ["🎬🌙👯", "🎥🌙👫", "🍿🎬👫", "🎞️🌃👯", "🍿🎥🌙"],
    hint: "Think film, night, and people together.",
    lesson: "Emoji translations work best when they preserve the major nouns and mood."
  },
  {
    id: "t-004",
    mode: "text-to-emoji",
    level: "spark",
    prompt: "Great idea",
    promptLabel: "Reply with emojis that mean this",
    answers: ["💡", "🔥💡", "👏💡", "🤩💡", "✅💡"],
    hint: "A light bulb often means an idea.",
    lesson: "Some emojis are symbols: 💡 maps to idea, not just a physical bulb."
  },
  {
    id: "t-005",
    mode: "text-to-emoji",
    level: "pro",
    prompt: "Level up your mind",
    promptLabel: "Reply with emojis that mean this",
    answers: ["🧠⬆️", "🧠🚀", "📈🧠", "🧠✨", "🎮🧠⬆️"],
    hint: "Use brain plus growth, launch, or upward motion.",
    lesson: "For abstract phrases, translate intent instead of word-for-word spelling."
  }
];
