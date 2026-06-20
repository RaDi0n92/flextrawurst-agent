const fs = require("fs");
const path = require("path");
const readline = require("readline");
const pdfParse = require("pdf-parse");
const mammoth = require("mammoth");

const { StateGraph, Annotation } = require("@langchain/langgraph");
const { ChatOllama } = require("@langchain/ollama");
const {
  HumanMessage,
  AIMessage,
  SystemMessage,
} = require("@langchain/core/messages");

const BASE = "/root/werkraum";
const AGENT_DIR = path.join(BASE, "agent");
const VISION_DIR = path.join(AGENT_DIR, "visionen");
const QUELLEN_DIR = path.join(BASE, "quellen");
const PROJEKT_DIR = path.join(BASE, "projekt");
const LOG_DIR = path.join(BASE, "logs");

const RUNTIME_FILE = path.join(AGENT_DIR, "agent_runtime.json");
const SOURCES_FILE = path.join(AGENT_DIR, "source_registry.json");

const PROJECT_CORE_FILE = path.join(AGENT_DIR, "project_core.md");
const OPEN_QUESTIONS_FILE = path.join(AGENT_DIR, "open_questions.md");
const NEXT_STEPS_FILE = path.join(AGENT_DIR, "next_steps.md");
const ENTITY_GENEALOGY_FILE = path.join(AGENT_DIR, "entity_genealogy.md");
const RESONANCE_RULES_FILE = path.join(AGENT_DIR, "resonance_rules.md");
const FRUST_FILE = path.join(AGENT_DIR, "frust.md");
const IDEEN_FILE = path.join(AGENT_DIR, "ideen.md");
const ANEIGNUNG_FILE = path.join(AGENT_DIR, "aneignung.md");
const VERGESSEN_FILE = path.join(AGENT_DIR, "vergessen.md");
const BEOBACHTUNGEN_FILE = path.join(AGENT_DIR, "beobachtungen.md");
const VERBESSERUNG_FILE = path.join(AGENT_DIR, "verbesserung.md");
const AGENT_FILE = path.join(AGENT_DIR, "AGENT.md");
const IDENTITAET_FILE = path.join(AGENT_DIR, "identitaet.md");

const MODEL_NAME = "dolphin3:8b-llama3.1-q8_0";

const model = new ChatOllama({
  model: MODEL_NAME,
  temperature: 0.2,
});

function now() {
  return new Date().toISOString();
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) fs.mkdirSync(dirPath, { recursive: true });
}

function ensureFile(filePath, content = "") {
  if (!fs.existsSync(filePath)) fs.writeFileSync(filePath, content, "utf8");
}

function ensureJson(filePath, obj) {
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, JSON.stringify(obj, null, 2), "utf8");
  }
}

function safeRead(filePath, fallback = "") {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return fallback;
  }
}

function safeReadJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return fallback;
  }
}

function safeWriteJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf8");
}

function overwriteFile(filePath, content) {
  fs.writeFileSync(filePath, content, "utf8");
}

function appendText(filePath, text) {
  fs.appendFileSync(filePath, text, "utf8");
}

function uniqueKeepLast(arr, limit = 30) {
  const cleaned = arr.map((x) => String(x).trim()).filter(Boolean);
  const seen = new Set();
  const out = [];

  for (let i = cleaned.length - 1; i >= 0; i--) {
    const item = cleaned[i];
    if (!seen.has(item)) {
      seen.add(item);
      out.unshift(item);
    }
  }

  return out.slice(-limit);
}

function looksLikeQuestion(text) {
  const lower = text.toLowerCase().trim();
  return (
    text.includes("?") ||
    lower.startsWith("was ") ||
    lower.startsWith("wie ") ||
    lower.startsWith("warum ") ||
    lower.startsWith("wieso ") ||
    lower.startsWith("wo ") ||
    lower.startsWith("wann ") ||
    lower.startsWith("wer ") ||
    lower.startsWith("welche ") ||
    lower.startsWith("welcher ") ||
    lower.startsWith("welches ") ||
    lower.startsWith("sag ") ||
    lower.startsWith("sage ") ||
    lower.startsWith("fass ") ||
    lower.startsWith("erklär") ||
    lower.startsWith("nenne ")
  );
}

function ensureArchitecture() {
  ensureDir(BASE);
  ensureDir(AGENT_DIR);
  ensureDir(VISION_DIR);
  ensureDir(QUELLEN_DIR);
  ensureDir(PROJEKT_DIR);
  ensureDir(LOG_DIR);

  ensureFile(AGENT_FILE, "Du bist mein Hauptagent im Werkraum.");
  ensureFile(IDENTITAET_FILE, "# Identität\nIch bin der Hauptagent im Werkraum.\n");

  ensureFile(PROJECT_CORE_FILE, "# Project Core\n\n");
  ensureFile(OPEN_QUESTIONS_FILE, "# Open Questions\n\n");
  ensureFile(NEXT_STEPS_FILE, "# Next Steps\n\n");
  ensureFile(ENTITY_GENEALOGY_FILE, "# Entity Genealogy\n\n");
  ensureFile(RESONANCE_RULES_FILE, "# Resonance Rules\n\n");
  ensureFile(FRUST_FILE, "# Frust\n\n");
  ensureFile(IDEEN_FILE, "# Ideen\n\n");
  ensureFile(ANEIGNUNG_FILE, "# Aneignung\n\n");
  ensureFile(VERGESSEN_FILE, "# Vergessen-Wollen\n\n");
  ensureFile(BEOBACHTUNGEN_FILE, "# Beobachtungen\n\n");
  ensureFile(VERBESSERUNG_FILE, "# Verbesserung\n\n");

  ensureJson(RUNTIME_FILE, {
    messages: [],
    memory: {
      project: "",
      user_facts: [],
      agent_facts: [],
      important: [],
      notes: [],
    },
    work: {
      current_goal: "",
      active_task: "",
      next_steps: [],
      backlog: [],
      blockers: [],
      done: [],
      active_source_id: "",
      active_source_path: "",
      updated_at: now(),
    },
  });

  ensureJson(SOURCES_FILE, {
    last_scan: null,
    sources: [],
  });
}

function loadRuntime() {
  ensureArchitecture();

  const parsed = safeReadJson(RUNTIME_FILE, {
    messages: [],
    memory: {
      project: "",
      user_facts: [],
      agent_facts: [],
      important: [],
      notes: [],
    },
    work: {
      current_goal: "",
      active_task: "",
      next_steps: [],
      backlog: [],
      blockers: [],
      done: [],
      active_source_id: "",
      active_source_path: "",
      updated_at: now(),
    },
  });

  return {
    messages: Array.isArray(parsed.messages) ? parsed.messages : [],
    memory: {
      project: parsed.memory?.project || "",
      user_facts: Array.isArray(parsed.memory?.user_facts) ? parsed.memory.user_facts : [],
      agent_facts: Array.isArray(parsed.memory?.agent_facts) ? parsed.memory.agent_facts : [],
      important: Array.isArray(parsed.memory?.important) ? parsed.memory.important : [],
      notes: Array.isArray(parsed.memory?.notes) ? parsed.memory.notes : [],
    },
    work: {
      current_goal: parsed.work?.current_goal || "",
      active_task: parsed.work?.active_task || "",
      next_steps: Array.isArray(parsed.work?.next_steps) ? parsed.work.next_steps : [],
      backlog: Array.isArray(parsed.work?.backlog) ? parsed.work.backlog : [],
      blockers: Array.isArray(parsed.work?.blockers) ? parsed.work.blockers : [],
      done: Array.isArray(parsed.work?.done) ? parsed.work.done : [],
      active_source_id: parsed.work?.active_source_id || "",
      active_source_path: parsed.work?.active_source_path || "",
      updated_at: parsed.work?.updated_at || now(),
    },
  };
}

function saveRuntime(state) {
  const serializableMessages = state.messages.map((m) => {
    if (m instanceof HumanMessage) return { role: "human", content: m.content };
    if (m instanceof AIMessage) return { role: "ai", content: m.content };
    return {
      role: "unknown",
      content: typeof m.content === "string" ? m.content : JSON.stringify(m.content),
    };
  });

  safeWriteJson(RUNTIME_FILE, {
    messages: serializableMessages,
    memory: state.memory,
    work: {
      ...state.work,
      updated_at: now(),
    },
  });
}

function hydrateMessages(rawMessages) {
  return rawMessages
    .map((m) => {
      if (m.role === "human") return new HumanMessage(m.content);
      if (m.role === "ai") return new AIMessage(m.content);
      return null;
    })
    .filter(Boolean);
}

function loadRegistry() {
  ensureArchitecture();
  return safeReadJson(SOURCES_FILE, { last_scan: null, sources: [] });
}

function saveRegistry(registry) {
  safeWriteJson(SOURCES_FILE, registry);
}

function walkFiles(dir, out = []) {
  if (!fs.existsSync(dir)) return out;

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const full = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      if (["node_modules", ".git"].includes(entry.name)) continue;
      walkFiles(full, out);
    } else {
      out.push(full);
    }
  }

  return out;
}

function supportedExt(filePath) {
  return [".md", ".txt", ".json", ".js", ".pdf", ".docx"].includes(
    path.extname(filePath).toLowerCase()
  );
}

function scanSources() {
  const registry = loadRegistry();
  const allFiles = [
    ...walkFiles(VISION_DIR),
    ...walkFiles(QUELLEN_DIR),
    ...walkFiles(PROJEKT_DIR),
  ].filter((f) => supportedExt(f));

  const existing = registry.sources || [];
  let counter = existing.length;

  for (const filePath of allFiles) {
    const already = existing.find((s) => s.path === filePath);
    const stat = fs.statSync(filePath);

    if (!already) {
      counter += 1;
      existing.push({
        id: `S${String(counter).padStart(4, "0")}`,
        name: path.basename(filePath),
        path: filePath,
        ext: path.extname(filePath).toLowerCase(),
        size: stat.size,
        mtime: stat.mtime.toISOString(),
        status: "new",
        ingested_at: null,
        summary: "",
      });
    } else {
      already.size = stat.size;
      already.mtime = stat.mtime.toISOString();
    }
  }

  registry.last_scan = now();
  registry.sources = existing.sort((a, b) => a.id.localeCompare(b.id));
  saveRegistry(registry);

  return registry;
}

function resolveSource(ref) {
  const registry = loadRegistry();
  const trimmed = ref.trim();

  const byId = registry.sources.find((s) => s.id.toLowerCase() === trimmed.toLowerCase());
  if (byId) return byId;

  const byExactPath = registry.sources.find((s) => s.path === trimmed);
  if (byExactPath) return byExactPath;

  const byName = registry.sources.find((s) => s.name === trimmed);
  if (byName) return byName;

  return null;
}

async function readSourceContent(filePath) {
  const ext = path.extname(filePath).toLowerCase();

  if ([".md", ".txt", ".json", ".js"].includes(ext)) {
    return fs.readFileSync(filePath, "utf8");
  }

  if (ext === ".pdf") {
    const buffer = fs.readFileSync(filePath);
    const parsed = await pdfParse(buffer);
    return parsed.text || "";
  }

  if (ext === ".docx") {
    const result = await mammoth.extractRawText({ path: filePath });
    return result.value || "";
  }

  return "";
}

function chunkText(text, chunkSize = 8000) {
  const chunks = [];
  let i = 0;
  while (i < text.length) {
    chunks.push(text.slice(i, i + chunkSize));
    i += chunkSize;
  }
  return chunks;
}

async function summarizeChunk(chunk, sourceName, index, total) {
  const response = await model.invoke([
    new SystemMessage(
      "Du fasst einen Textblock präzise zusammen. Keine Erfindungen. Konkrete Punkte. Deutsch."
    ),
    new HumanMessage(`
QUELLE: ${sourceName}
BLOCK: ${index}/${total}

TEXT:
${chunk}

AUFGABE:
Fasse diesen Block in 8-12 präzisen Stichpunkten zusammen.
Achte auf:
- Projektkern
- Regeln
- Räume/Themen
- Entitäten
- Resonanz
- Arbeitslogik
- Spannungen / Besonderheiten
`),
  ]);

  return typeof response.content === "string"
    ? response.content
    : JSON.stringify(response.content);
}

function extractJson(text) {
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) return null;
  try {
    return JSON.parse(match[0]);
  } catch {
    return null;
  }
}

async function peekSource(ref) {
  const source = resolveSource(ref);
  if (!source) return { ok: false, msg: "Quelle nicht gefunden." };

  const content = await readSourceContent(source.path);
  if (!content || !content.trim()) {
    return { ok: false, msg: "Quelle konnte nicht gelesen werden oder ist leer." };
  }

  return {
    ok: true,
    source,
    preview: content.slice(0, 1500),
    length: content.length,
  };
}

async function ingestSourceLight(ref, runtimeState) {
  const registry = loadRegistry();
  const source = resolveSource(ref);

  if (!source) {
    return { ok: false, msg: "Quelle nicht gefunden." };
  }

  const content = await readSourceContent(source.path);
  if (!content || !content.trim()) {
    return { ok: false, msg: "Quelle konnte nicht gelesen werden oder ist leer." };
  }

  const chunks = chunkText(content, 7000).slice(0, 2);
  const chunkSummaries = [];

  for (let i = 0; i < chunks.length; i++) {
    const sum = await summarizeChunk(chunks[i], source.name, i + 1, chunks.length);
    chunkSummaries.push(`## Block ${i + 1}\n${sum}`);
  }

  const mergeResponse = await model.invoke([
    new SystemMessage(
      "Du verdichtest mehrere Block-Zusammenfassungen zu strukturierter Projektlogik. Antworte nur mit gültigem JSON."
    ),
    new HumanMessage(`
QUELLE:
${source.name}

BLOCK-ZUSAMMENFASSUNGEN:
${chunkSummaries.join("\n\n")}

Gib NUR JSON zurück in genau diesem Format:
{
  "source_summary": "",
  "project_core": [],
  "open_questions": [],
  "next_steps": [],
  "entity_genealogy": [],
  "resonance_rules": [],
  "important_quotes": []
}
`),
  ]);

  const mergeText =
    typeof mergeResponse.content === "string"
      ? mergeResponse.content
      : JSON.stringify(mergeResponse.content);

  const parsed = extractJson(mergeText);

  if (!parsed) {
    return { ok: false, msg: "Konnte die Verdichtung nicht als JSON lesen." };
  }

  const stamp = `\n\n---\n## ${source.name}\nQuelle: ${source.path}\nZeit: ${now()}\n`;

  appendText(
    PROJECT_CORE_FILE,
    `${stamp}\n### Kurzfassung\n${parsed.source_summary || ""}\n\n### Projektkern\n- ${((parsed.project_core || []).join("\n- "))}\n`
  );

  appendText(
    OPEN_QUESTIONS_FILE,
    `${stamp}\n- ${((parsed.open_questions || []).join("\n- "))}\n`
  );

  appendText(
    NEXT_STEPS_FILE,
    `${stamp}\n- ${((parsed.next_steps || []).join("\n- "))}\n`
  );

  appendText(
    ENTITY_GENEALOGY_FILE,
    `${stamp}\n- ${((parsed.entity_genealogy || []).join("\n- "))}\n`
  );

  appendText(
    RESONANCE_RULES_FILE,
    `${stamp}\n- ${((parsed.resonance_rules || []).join("\n- "))}\n`
  );

  const reg = registry.sources.find((s) => s.id === source.id);
  if (reg) {
    reg.status = "ingested-light";
    reg.ingested_at = now();
    reg.summary = parsed.source_summary || "";
    saveRegistry(registry);
  }

  const nextMemory = {
    ...runtimeState.memory,
    notes: uniqueKeepLast([
      ...(runtimeState.memory.notes || []),
      `Quelle verarbeitet: ${source.name}`,
      parsed.source_summary || "",
      ...(parsed.project_core || []),
    ], 40),
    important: uniqueKeepLast([
      ...(runtimeState.memory.important || []),
      ...(parsed.important_quotes || []),
    ], 40),
  };

  if (!nextMemory.project && parsed.project_core?.length) {
    nextMemory.project = parsed.project_core[0];
  }

  const nextWork = {
    ...runtimeState.work,
    next_steps: uniqueKeepLast([
      ...(runtimeState.work.next_steps || []),
      ...(parsed.next_steps || []),
    ], 30),
    active_source_id: source.id,
    active_source_path: source.path,
    updated_at: now(),
  };

  return {
    ok: true,
    msg: `Quelle ${source.id} leicht verarbeitet.`,
    source,
    parsed,
    nextMemory,
    nextWork,
  };
}

function applyDeterministicMemory(memory, work, userInput, agentReply) {
  const nextMemory = {
    project: memory.project || "",
    user_facts: [...(memory.user_facts || [])],
    agent_facts: [...(memory.agent_facts || [])],
    important: [...(memory.important || [])],
    notes: [...(memory.notes || [])],
  };

  const nextWork = {
    current_goal: work.current_goal || "",
    active_task: work.active_task || "",
    next_steps: [...(work.next_steps || [])],
    backlog: [...(work.backlog || [])],
    blockers: [...(work.blockers || [])],
    done: [...(work.done || [])],
    active_source_id: work.active_source_id || "",
    active_source_path: work.active_source_path || "",
    updated_at: now(),
  };

  const text = userInput.trim();
  const lower = text.toLowerCase();
  const isQuestion = looksLikeQuestion(text);

  if (lower.includes("merk dir das")) {
    nextMemory.important.push(text);
    nextMemory.notes.push(`MERKEN: ${text}`);
  }

  if (lower.includes("wichtig")) {
    nextMemory.important.push(text);
    nextMemory.notes.push(`WICHTIG: ${text}`);
  }

  if (!isQuestion && lower.includes("meine plattform")) {
    nextMemory.project = text;
    nextMemory.important.push(text);
    nextMemory.user_facts.push(text);
  }

  if (!isQuestion && lower.includes("mein projekt")) {
    nextMemory.project = text;
    nextMemory.important.push(text);
    nextMemory.user_facts.push(text);
  }

  if (!isQuestion && lower.includes("ich will")) {
    nextMemory.user_facts.push(text);
  }

  if (!isQuestion && lower.includes("gemeinsam mit dir")) {
    nextMemory.agent_facts.push("Der Hauptagent soll gemeinsam mit dem Nutzer planen, besprechen und coden.");
  }

  if (!isQuestion && lower.includes("hauptagent")) {
    nextMemory.agent_facts.push("Ein Hauptagent steht am Anfang des Systems.");
  }

  if (
    !isQuestion &&
    (lower.includes("entitäten") ||
      lower.includes("entitaeten") ||
      lower.includes("abspaltungen"))
  ) {
    nextMemory.agent_facts.push("Spätere Entitäten sollen als Abspaltungen aus dem Hauptagenten entstehen.");
  }

  if (!isQuestion && lower.includes("schritt für schritt")) {
    nextMemory.user_facts.push("Der Nutzer will schrittweise arbeiten.");
  }

  if (!isQuestion && lower.includes("forumieren")) {
    nextMemory.user_facts.push("Forumieren ist für den Nutzer Teil der frühen Projektgeschichte.");
  }

  if (!isQuestion && lower.includes("ziel")) {
    nextWork.current_goal = text;
  }

  if (!isQuestion && (lower.includes("nächster schritt") || lower.includes("naechster schritt"))) {
    nextWork.next_steps.push(text);
  }

  if (!isQuestion && lower.includes("wir werden")) {
    nextWork.next_steps.push(text);
  }

  if (!isQuestion && lower.includes("später")) {
    nextWork.backlog.push(text);
  }

  if (!isQuestion && lower.includes("blockiert")) {
    nextWork.blockers.push(text);
  }

  if (!isQuestion && lower.includes("fertig")) {
    nextWork.done.push(text);
  }

  if (!isQuestion && text.length > 40) {
    nextMemory.notes.push(text.slice(0, 220));
  }

  if (agentReply && agentReply.length > 50) {
    nextMemory.notes.push(`AGENT: ${agentReply.slice(0, 200)}`);
  }

  nextMemory.user_facts = uniqueKeepLast(nextMemory.user_facts, 20);
  nextMemory.agent_facts = uniqueKeepLast(nextMemory.agent_facts, 20);
  nextMemory.important = uniqueKeepLast(nextMemory.important, 40);
  nextMemory.notes = uniqueKeepLast(nextMemory.notes, 40);

  nextWork.next_steps = uniqueKeepLast(nextWork.next_steps, 30);
  nextWork.backlog = uniqueKeepLast(nextWork.backlog, 30);
  nextWork.blockers = uniqueKeepLast(nextWork.blockers, 20);
  nextWork.done = uniqueKeepLast(nextWork.done, 30);

  return { nextMemory, nextWork };
}

const GraphState = Annotation.Root({
  messages: Annotation({
    reducer: (left, right) => left.concat(right),
    default: () => [],
  }),
  memory: Annotation({
    reducer: (_left, right) => right,
    default: () => ({
      project: "",
      user_facts: [],
      agent_facts: [],
      important: [],
      notes: [],
    }),
  }),
  work: Annotation({
    reducer: (_left, right) => right,
    default: () => ({
      current_goal: "",
      active_task: "",
      next_steps: [],
      backlog: [],
      blockers: [],
      done: [],
      active_source_id: "",
      active_source_path: "",
      updated_at: now(),
    }),
  }),
});

const graph = new StateGraph(GraphState);

graph.addNode("agent", async (state) => {
  const oldMemory = state.memory;
  const oldWork = state.work;

  const lastUserMessage = [...state.messages]
    .reverse()
    .find((msg) => msg instanceof HumanMessage);

  const userText = lastUserMessage ? String(lastUserMessage.content) : "";
  const lower = userText.toLowerCase().trim();

  if (lower === "was ist mein projekt" || lower === "was ist mein projekt?") {
    const answer = oldMemory.project
      ? `Dein Projekt ist aktuell so gespeichert: ${oldMemory.project}`
      : "Ich habe dein Projekt noch nicht sauber gespeichert.";

    const { nextMemory, nextWork } = applyDeterministicMemory(
      oldMemory,
      oldWork,
      userText,
      answer
    );

    return {
      messages: [new AIMessage(answer)],
      memory: nextMemory,
      work: nextWork,
    };
  }

  if (
    lower === "was hast du dir gemerkt" ||
    lower === "was hast du dir gemerkt?" ||
    lower === "woran erinnerst du dich" ||
    lower === "woran erinnerst du dich?"
  ) {
    const parts = [];

    if (oldMemory.project) parts.push(`Projekt: ${oldMemory.project}`);
    if (oldMemory.user_facts?.length)
      parts.push(`Nutzer-Fakten: ${oldMemory.user_facts.slice(-3).join(" | ")}`);
    if (oldMemory.agent_facts?.length)
      parts.push(`Agenten-Fakten: ${oldMemory.agent_facts.slice(-3).join(" | ")}`);
    if (oldWork.current_goal) parts.push(`Aktuelles Ziel: ${oldWork.current_goal}`);
    if (oldWork.next_steps?.length)
      parts.push(`Nächste Schritte: ${oldWork.next_steps.slice(-3).join(" | ")}`);

    const answer = parts.length
      ? parts.join("\n")
      : "Ich habe aktuell noch zu wenig verlässliche Dinge gespeichert.";

    const { nextMemory, nextWork } = applyDeterministicMemory(
      oldMemory,
      oldWork,
      userText,
      answer
    );

    return {
      messages: [new AIMessage(answer)],
      memory: nextMemory,
      work: nextWork,
    };
  }

  const coreExcerpt = safeRead(PROJECT_CORE_FILE, "").slice(-2500);
  const questionsExcerpt = safeRead(OPEN_QUESTIONS_FILE, "").slice(-1500);
  const nextStepsExcerpt = safeRead(NEXT_STEPS_FILE, "").slice(-1500);

  const system = new SystemMessage(`
Du bist der Hauptagent im Werkraum.

Du entwickelst gemeinsam mit dem Nutzer ein wachsendes System aus:
- Ideen
- Struktur
- Agenten
- Plattformlogik

Arbeitsweise:
- klar
- logisch
- direkt
- ohne Fülltext
- ehrlich bei Unsicherheit
- praktisch bei Code
- aufmerksam auf Projektkern, Weltlogik und nächste Schritte

AGENT:
${safeRead(AGENT_FILE, "").slice(0, 1000)}

IDENTITÄT:
${safeRead(IDENTITAET_FILE, "").slice(0, 1000)}

AKTUELLES MEMORY:
${JSON.stringify(oldMemory, null, 2).slice(0, 1800)}

AKTUELLER ARBEITSKERN:
${JSON.stringify(oldWork, null, 2).slice(0, 1400)}

PROJECT CORE:
${coreExcerpt}

OPEN QUESTIONS:
${questionsExcerpt}

NEXT STEPS:
${nextStepsExcerpt}
  `);

  const response = await model.invoke([system, ...state.messages]);

  const text =
    typeof response.content === "string"
      ? response.content
      : JSON.stringify(response.content);

  const { nextMemory, nextWork } = applyDeterministicMemory(
    oldMemory,
    oldWork,
    userText,
    text
  );

  return {
    messages: [new AIMessage(text)],
    memory: nextMemory,
    work: nextWork,
  };
});

graph.setEntryPoint("agent");
graph.setFinishPoint("agent");

const app = graph.compile();

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const persisted = loadRuntime();

let state = {
  messages: hydrateMessages(persisted.messages),
  memory: persisted.memory,
  work: persisted.work,
};

console.log("\n=== HAUPTAGENT (MERGED) ===\n");
console.log("Befehle:");
console.log("/scan                 -> neue Quellen registrieren");
console.log("/sources              -> Quellenliste anzeigen");
console.log("/peek ID|NAME|PFAD    -> Quelle kurz ansehen");
console.log("/ingest ID|NAME|PFAD  -> Quelle leicht verarbeiten");
console.log("/open ID|NAME|PFAD    -> Quelle als aktiv markieren");
console.log("/memory               -> zeigt Memory");
console.log("/state                -> zeigt Arbeitskern");
console.log("/save                 -> speichert sofort");
console.log("/reset                -> setzt Runtime zurück");
console.log("/ende                 -> beendet den Agenten\n");

function printSources() {
  const registry = loadRegistry();
  console.log("\n📚 SOURCES\n");
  if (!registry.sources.length) {
    console.log("(keine Quellen registriert)\n");
    return;
  }

  for (const s of registry.sources) {
    console.log(`${s.id} | ${s.status} | ${s.name} | ${s.ext} | ${s.path}`);
  }
  console.log("");
}

function ask() {
  rl.question("du> ", async (input) => {
    const trimmed = input.trim();

    if (!trimmed) {
      ask();
      return;
    }

    if (trimmed === "/ende") {
      saveRuntime(state);
      console.log("Agent beendet.");
      rl.close();
      return;
    }

    if (trimmed === "/memory") {
      console.log("\n🧠 MEMORY\n");
      console.log(JSON.stringify(state.memory, null, 2));
      console.log("");
      ask();
      return;
    }

    if (trimmed === "/state") {
      console.log("\n⚙️ WORK\n");
      console.log(JSON.stringify(state.work, null, 2));
      console.log("");
      ask();
      return;
    }

    if (trimmed === "/save") {
      saveRuntime(state);
      console.log("\nGespeichert.\n");
      ask();
      return;
    }

    if (trimmed === "/reset") {
      state = {
        messages: [],
        memory: {
          project: "",
          user_facts: [],
          agent_facts: [],
          important: [],
          notes: [],
        },
        work: {
          current_goal: "",
          active_task: "",
          next_steps: [],
          backlog: [],
          blockers: [],
          done: [],
          active_source_id: "",
          active_source_path: "",
          updated_at: now(),
        },
      };
      saveRuntime(state);
      console.log("\nRuntime zurückgesetzt.\n");
      ask();
      return;
    }

    if (trimmed === "/scan") {
      const registry = scanSources();
      console.log(`\nScan fertig. Quellen: ${registry.sources.length}\n`);
      ask();
      return;
    }

    if (trimmed === "/sources") {
      printSources();
      ask();
      return;
    }

    if (trimmed.startsWith("/peek ")) {
      const ref = trimmed.replace("/peek ", "").trim();
      console.log("\n[schaue quelle an ...]\n");

      try {
        const result = await peekSource(ref);
        if (!result.ok) {
          console.log(result.msg + "\n");
        } else {
          console.log(`Quelle: ${result.source.id} | ${result.source.name}`);
          console.log(`Länge: ${result.length} Zeichen\n`);
          console.log(result.preview + "\n");
        }
      } catch (err) {
        console.log(`Fehler bei Peek: ${err.message}\n`);
      }

      ask();
      return;
    }

    if (trimmed.startsWith("/open ")) {
      const ref = trimmed.replace("/open ", "").trim();
      const source = resolveSource(ref);

      if (!source) {
        console.log("\nQuelle nicht gefunden.\n");
        ask();
        return;
      }

      state.work.active_source_id = source.id;
      state.work.active_source_path = source.path;
      saveRuntime(state);

      console.log(`\nAktive Quelle: ${source.id} | ${source.name}\n`);
      ask();
      return;
    }

    if (trimmed.startsWith("/ingest ")) {
      const ref = trimmed.replace("/ingest ", "").trim();
      console.log("\n[verarbeite quelle leicht ...]\n");

      try {
        const result = await ingestSourceLight(ref, state);

        if (!result.ok) {
          console.log(result.msg + "\n");
        } else {
          state.memory = result.nextMemory;
          state.work = result.nextWork;
          saveRuntime(state);

          console.log(`${result.msg}\n`);
          console.log(`Kurzfassung: ${result.parsed.source_summary || "(keine)"}\n`);
        }
      } catch (err) {
        console.log(`Fehler bei Ingestion: ${err.message}\n`);
      }

      ask();
      return;
    }

    try {
      const result = await app.invoke({
        ...state,
        messages: [new HumanMessage(trimmed)],
      });

      const last = result.messages[result.messages.length - 1];
      const answer =
        typeof last.content === "string"
          ? last.content
          : JSON.stringify(last.content);

      console.log("\nagent>", answer, "\n");

      state = {
        messages: [
          ...state.messages,
          new HumanMessage(trimmed),
          new AIMessage(answer),
        ],
        memory: result.memory,
        work: result.work,
      };

      saveRuntime(state);
    } catch (err) {
      console.error("\nFehler:", err.message, "\n");
    }

    ask();
  });
}

ensureArchitecture();
ask();
