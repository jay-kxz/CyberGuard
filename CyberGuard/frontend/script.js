"use strict";
// CyberGuard frontend. Concepts: DOM, events, fetch, async/await, JSON, validation.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const MAX_FILE = 25 * 1024 * 1024, MAX_LOG = 5 * 1024 * 1024;

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast.id); toast.id = setTimeout(() => (t.hidden = true), 4000);
}

function show(id) {
  $$(".view").forEach(v => (v.hidden = v.id !== "v-" + id));
  $$("nav button").forEach(b => {
    const on = b.dataset.view === id;
    b.classList.toggle("on", on);
    on ? b.setAttribute("aria-current", "page") : b.removeAttribute("aria-current");
    if (on) $("#title").textContent = b.textContent;
  });
  document.body.classList.remove("open");
  $("#menu").setAttribute("aria-expanded", "false");
  if (id === "history") loadHistory();
}

// All server calls go through here so errors are handled in one place.
async function api(path, opts = {}) {
  let r;
  try { r = await fetch(path, opts); }
  catch { throw new Error("Cannot reach the CyberGuard server. It is not running yet."); }
  let j;
  try { j = await r.json(); }
  catch { throw new Error("The server sent a reply that is not valid JSON (HTTP " + r.status + ")."); }
  if (!j.ok) throw new Error(j.error || "Request failed (HTTP " + r.status + ").");
  return j;
}

const int = (v, name) => {
  if (!/^-?\d+$/.test(String(v).trim())) throw new Error(name + " must be a whole number.");
  const x = Number(v);
  if (!Number.isSafeInteger(x)) throw new Error(name + " is too large.");
  return x;
};
const list = s => s.split(/[,\s]+/).filter(Boolean).map((x, i) => int(x, "Score " + (i + 1)));

// One entry per tool: where to send the data, and how to check and package it.
const TOOLS = {
  identifier: { url: "/api/analyze", build: f => {
    if (!f.text.value.trim()) throw new Error("Enter some text first.");
    return { text: f.text.value }; } },
  score: { url: "/api/calculate", build: f => {
    const s = list(f.scores.value);
    if (s.length < 1 || s.length > 10) throw new Error("Enter 1 to 10 whole numbers.");
    return { scores: s }; } },
  pointers: { url: "/api/pointers", build: f => ({ a: int(f.a.value, "First number"), b: int(f.b.value, "Second number") }) },
  assessment: { url: "/api/assessment", build: f => {
    const s = list(f.scores.value);
    if (!f.user.value.trim()) throw new Error("Enter a user name.");
    if (s.length !== 5) throw new Error("Enter exactly 5 scores.");
    const base = int(f.baseline.value, "Baseline");
    if ([...s, base].some(x => x < 0 || x > 100)) throw new Error("Scores and baseline must be between 0 and 100.");
    return { user: f.user.value.trim(), scores: s, baseline: base }; } },
  file: { url: "/api/file-hash", build: f => {
    const file = f.file.files[0];
    if (!file) throw new Error("Choose a file first.");
    if (file.size > MAX_FILE) throw new Error("That file is larger than 25 MB.");
    const ref = f.reference.value.trim();
    if (ref && !/^[0-9a-f]{64}$/i.test(ref)) throw new Error("A reference hash has exactly 64 hexadecimal characters.");
    const d = new FormData(); d.append("file", file); d.append("reference", ref);
    return d; } },
  password: { url: "/api/password-strength", build: f => {
    if (!f.password.value) throw new Error("Enter a sample password.");
    return { password: f.password.value }; } },
  log: { url: "/api/log-analysis", build: async f => {
    const file = f.file.files[0];
    if (!file) throw new Error("Choose a .log or .txt file.");
    if (!/\.(log|txt)$/i.test(file.name)) throw new Error("Only .log and .txt files are accepted.");
    if (file.size > MAX_LOG) throw new Error("That log file is larger than 5 MB.");
    return { filename: file.name, content: await file.text() }; } },
  ip: { url: "/api/ip-validation", build: f => {
    if (!f.address.value.trim()) throw new Error("Enter an IP address.");
    return { address: f.address.value.trim() }; } },
  report: { url: "/api/report", build: f => ({ type: f.kind.value, format: f.format.value }) }
};

// A list of records becomes a small table with one column per key.
function listTable(arr) {
  const t = document.createElement("table"), keys = Object.keys(arr[0]);
  const h = t.createTHead().insertRow();
  keys.forEach(k => { const c = document.createElement("th"); c.textContent = k.replace(/_/g, " "); h.append(c); });
  const b = t.createTBody();
  arr.forEach(o => { const r = b.insertRow(); keys.forEach(k => (r.insertCell().textContent = String(o[k] ?? ""))); });
  return t;
}

// Builds a key/value table. textContent keeps untrusted text from running as HTML.
function tableFrom(o) {
  const t = document.createElement("table"); t.className = "kv";
  for (const [k, v] of Object.entries(o)) {
    const r = t.insertRow(), h = document.createElement("th");
    h.textContent = k.replace(/_/g, " "); r.append(h);
    const c = r.insertCell();
    if (v && typeof v === "object" && !Array.isArray(v)) c.append(tableFrom(v));
    else if (Array.isArray(v) && v.length && v[0] && typeof v[0] === "object") c.append(listTable(v));
    else if (Array.isArray(v) && !v.length) c.textContent = "none";
    else c.textContent = Array.isArray(v) ? v.join(", ") : String(v);
  }
  return t;
}

$$("form.tool").forEach(f => f.addEventListener("submit", async e => {
  e.preventDefault();
  const out = f.nextElementSibling, btn = $(".go", f), label = btn.textContent, spec = TOOLS[f.dataset.tool];
  btn.disabled = true; btn.textContent = "Working"; out.className = "result"; out.textContent = "Working...";
  try {
    const body = await spec.build(f);
    const opts = body instanceof FormData
      ? { method: "POST", body }
      : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    const j = await api(spec.url, opts);
    if (typeof j.data.content === "string") {          // a report: show the text and offer a download
      const { content, ...rest } = j.data;
      const pre = document.createElement("pre"), a = document.createElement("a");
      pre.className = "report"; pre.textContent = content;
      a.className = "copy"; a.textContent = "Download " + j.data.filename; a.download = j.data.filename;
      a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
      out.replaceChildren(tableFrom(rest), pre, a);
    } else out.replaceChildren(tableFrom(j.data));
    const hash = j.data.sha256;
    if (hash) {
      const c = document.createElement("button"); c.type = "button"; c.className = "copy"; c.textContent = "Copy hash";
      c.onclick = () => navigator.clipboard.writeText(hash).then(() => toast("Hash copied."), () => toast("Copy failed."));
      out.append(c);
    }
    toast(j.persisted === false ? "Done, but the database is offline so it was not saved." : "Done.");
  } catch (err) {
    out.className = "result err"; out.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = label; }
}));

function rowsTable(rows) {
  const t = document.createElement("table"), h = t.createTHead().insertRow();
  ["Time", "Module", "Summary", "Status"].forEach(x => { const c = document.createElement("th"); c.textContent = x; h.append(c); });
  const b = t.createTBody();
  rows.forEach(r => { const tr = b.insertRow();
    [r.analysis_timestamp, r.module_name, r.result_summary, r.status].forEach(v => (tr.insertCell().textContent = v ?? "")); });
  return t;
}

async function loadHistory() {
  try {
    const rows = (await api("/api/history")).data;
    if (!rows.length) return;
    $("#hist").replaceChildren(rowsTable(rows));
    $("#recent").replaceChildren(rowsTable(rows.slice(0, 5)));
  } catch (e) { $("#hist").textContent = e.message; }
}

async function loadDash() {
  try {
    const d = (await api("/api/dashboard")).data;
    $$("[data-stat]").forEach(e => (e.textContent = d[e.dataset.stat] ?? 0));
    $("#dashNote").textContent = "Live numbers from the database.";
    loadHistory();
  } catch { $("#dashNote").textContent = "Numbers appear once the server and database are connected."; }
}

async function health() {
  const p = $("#pill");
  try { await api("/api/health"); p.textContent = "Server online"; p.className = "pill up"; }
  catch { p.textContent = "Server offline"; p.className = "pill down"; }
}

// Start-up: wire events, build the tool cards, load live data.
$("nav").addEventListener("click", e => { const b = e.target.closest("button"); if (b) show(b.dataset.view); });
$("#menu").addEventListener("click", () => {
  const open = document.body.classList.toggle("open");
  $("#menu").setAttribute("aria-expanded", open);
});
document.addEventListener("keydown", e => { if (e.key === "Escape") document.body.classList.remove("open"); });
$("#idText").addEventListener("input", e => ($("#count").textContent = e.target.value.length + " characters"));
$("#refresh").addEventListener("click", loadHistory);
$$("nav button[data-desc]").forEach(b => {
  const c = document.createElement("button"), s = document.createElement("strong"), d = document.createElement("span");
  c.className = "card tc"; s.textContent = b.textContent; d.textContent = b.dataset.desc;
  c.append(s, d); c.onclick = () => show(b.dataset.view); $("#cards").append(c);
});
show("overview"); health(); loadDash();
