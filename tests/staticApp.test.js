import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const ROOT = process.cwd();
const MIME_TYPES = new Map([
  [".html", "text/html"],
  [".css", "text/css"],
  [".js", "text/javascript"],
  [".mp4", "video/mp4"]
]);

async function readText(path) {
  return readFile(join(ROOT, path), "utf8");
}

function createStaticServer() {
  return createServer(async (request, response) => {
    try {
      const requestPath = request.url === "/" ? "/index.html" : request.url;
      const safePath = normalize(requestPath).replace(/^([/\\])+/, "");
      const file = await readFile(join(ROOT, safePath));
      response.writeHead(200, { "content-type": MIME_TYPES.get(extname(safePath)) ?? "application/octet-stream" });
      response.end(file);
    } catch {
      response.writeHead(404);
      response.end("not found");
    }
  });
}

test("static HTML references the required app assets and controls", async () => {
  const html = await readText("index.html");
  assert.match(html, /<title>Emoji Oracle/);
  assert.match(html, /href="styles.css"/);
  assert.match(html, /type="module" src="src\/app.js"/);

  for (const id of [
    "playerName",
    "modeSelect",
    "levelSelect",
    "startBtn",
    "answerInput",
    "speakBtn",
    "hintBtn",
    "skipBtn",
    "leaderboard",
    "shareBtn",
    "demoBtn",
    "demoModal",
    "demoVideo"
  ]) {
    assert.match(html, new RegExp(`id="${id}"`), `missing #${id}`);
  }
});

test("responsive stylesheet includes mobile breakpoints and core game surfaces", async () => {
  const css = await readText("styles.css");
  assert.match(css, /@media \(max-width: 9[0-9]{2}px\)/);
  assert.match(css, /@media \(max-width: [56][0-9]{2}px\)/);
  assert.match(css, /\.prompt-card/);
  assert.match(css, /\.leaderboard/);
  assert.match(css, /\.feedback\.success/);
  assert.match(css, /\.feedback\.danger/);
});

test("all browser assets are served successfully by a static server", async () => {
  const server = createStaticServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();

  try {
    for (const asset of ["/", "/index.html", "/styles.css", "/src/app.js", "/src/challenges.js", "/src/gameLogic.js", "/docs/demo.mp4"]) {
      const response = await fetch(`http://127.0.0.1:${port}${asset}`);
      assert.equal(response.status, 200, `${asset} should return 200`);
      assert.equal((await response.text()).length > 0, true, `${asset} should not be empty`);
    }
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
