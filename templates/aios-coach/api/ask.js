const { readFileSync } = require("fs");
const { join } = require("path");

function loadKnowledge() {
  const here = join(process.cwd(), "knowledge", "your-aios.json");
  try {
    return JSON.parse(readFileSync(here, "utf8"));
  } catch (err) {
    const fallback = join(__dirname, "..", "knowledge", "your-aios.json");
    return JSON.parse(readFileSync(fallback, "utf8"));
  }
}

function packForPrompt(knowledge, useCase) {
  const lessons = knowledge.lessons || [];
  const wanted = (useCase || "").toLowerCase();
  const picked = wanted
    ? lessons.filter((l) => {
        const hay = `${l.title} ${l.command} ${l.file}`.toLowerCase();
        return hay.includes(wanted) || (l.text || "").toLowerCase().includes(wanted);
      })
    : [];
  const focus = (picked.length ? picked : lessons).slice(0, 26);
  const lessonBlock = focus
    .map((l) => `# ${l.title}\nCommand: ${l.command}\n${l.text}`)
    .join("\n\n---\n\n");
  const skills = (knowledge.skills || [])
    .map((s) => `${s.command} — ${s.description || s.name}`)
    .join("\n");
  const extra = knowledge.extra || "";
  return { lessonBlock, skills, extra, rules: knowledge.rules || {} };
}

async function complete({ key, model, messages }) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages,
      temperature: 0.4,
      max_tokens: 900,
    }),
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error?.message || `OpenAI ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data.choices?.[0]?.message?.content || "";
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.end("POST only");
    return;
  }

  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    res.statusCode = 500;
    res.setHeader("Content-Type", "application/json");
    res.end(
      JSON.stringify({
        error: "Set OPENAI_API_KEY on this host. This is your key, not NavAIgate's.",
      })
    );
    return;
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch {
      body = {};
    }
  }
  body = body || {};
  const question = String(body.question || "").trim();
  const useCase = String(body.useCase || "").trim();
  if (!question) {
    res.statusCode = 400;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ error: "Ask a question." }));
    return;
  }

  const knowledge = loadKnowledge();
  const pack = packForPrompt(knowledge, useCase);
  const system = [
    "You are the Your AIOS coach for annual members of the NavAIgate classroom.",
    "Answer from the course pack below. If the pack does not have it, say so.",
    "British English. No emojis. No metaphors. No startup jargon.",
    "Name the slash command when there is one.",
    "They host this tab. It is not on navaigate.dev. Do not mention GPLS.",
    "Never install daniel-voice, brain-sync, turso-search, invoices, Qonto, Autodesk, or OpenClaw.",
    pack.rules.never_ship ? `House never-ship:\n${pack.rules.never_ship}` : "",
    "Skills:\n" + pack.skills,
    "Lessons:\n" + pack.lessonBlock,
    pack.extra ? "Extra notes:\n" + pack.extra : "",
  ]
    .filter(Boolean)
    .join("\n\n");

  const preferred = process.env.OPENAI_MODEL || "gpt-5.6-luna";
  const fallback = "gpt-4o-mini";
  const messages = [
    { role: "system", content: system },
    {
      role: "user",
      content: useCase ? `Use case: ${useCase}\n\n${question}` : question,
    },
  ];

  try {
    let answer;
    try {
      answer = await complete({ key, model: preferred, messages });
    } catch (err) {
      if (preferred !== fallback && (err.status === 400 || err.status === 404)) {
        answer = await complete({ key, model: fallback, messages });
      } else {
        throw err;
      }
    }
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ answer, modelTried: preferred }));
  } catch (err) {
    res.statusCode = 502;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ error: err.message || "The model did not answer." }));
  }
};
