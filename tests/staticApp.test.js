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
  [".svg", "image/svg+xml"],
  [".json", "application/json"]
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

test("static HTML references the required app assets and Kismoe controls", async () => {
  const html = await readText("index.html");
  assert.match(html, /Kismoe/, "missing Kismoe brand name");
  assert.match(html, /href="styles.css"/, "missing styles.css link");
  assert.match(html, /src="src\/app\.js"/, "missing src/app.js script");

  for (const id of [
    "authBtn",
    "authModal",
    "chatWidget",
    "chatToggle",
    "chatMessages",
    "chatInput"
  ]) {
    assert.match(html, new RegExp(`id="${id}"`), `missing #${id}`);
  }
});

test("responsive stylesheet includes mobile breakpoints and core Kismoe surfaces", async () => {
  const css = await readText("styles.css");
  assert.match(css, /@media \(max-width: [0-9]+px\)/, "missing mobile breakpoint");
  assert.match(css, /--bg-primary/, "missing CSS custom property --bg-primary");
  assert.match(css, /--accent-blue/, "missing CSS custom property --accent-blue");
  assert.match(css, /\.chat-widget/, "missing .chat-widget styles");
  assert.match(css, /\.service-card/, "missing .service-card styles");
});

test("all browser assets are served successfully by a static server", async () => {
  const server = createStaticServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();

  try {
    for (const asset of ["/", "/index.html", "/styles.css", "/src/app.js", "/src/chat.js", "/src/services.js", "/src/aiResponses.js", "/favicon.svg", "/privacy-policy.html", "/manifest.json"]) {
      const response = await fetch(`http://127.0.0.1:${port}${asset}`);
      assert.equal(response.status, 200, `${asset} should return 200`);
      assert.equal((await response.text()).length > 0, true, `${asset} should not be empty`);
    }
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
