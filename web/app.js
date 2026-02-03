const dockerStatusEl = document.getElementById("dockerStatus");
const pullBtn = document.getElementById("pullBtn");
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const startBtn = document.getElementById("startBtn");
const deviceSelect = document.getElementById("deviceSelect");
const jobsList = document.getElementById("jobsList");
const outputsList = document.getElementById("outputsList");
const previewArea = document.getElementById("previewArea");
const previewTitle = document.getElementById("previewTitle");
const logArea = document.getElementById("logArea");
const downloadZipBtn = document.getElementById("downloadZipBtn");
const logsPanel = document.getElementById("logsPanel");
const toggleSidebarBtn = document.getElementById("toggleSidebar");
const layoutEl = document.querySelector(".layout");
const tabs = document.querySelectorAll(".tab");
const tabUpload = document.getElementById("tab-upload");
const tabResults = document.getElementById("tab-results");

const state = {
  files: [],
  jobs: [],
  activeJobId: null,
  logOffset: 0,
  logTimer: null,
  logText: "",
  filePreviewUrls: [],
};

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  })[c]);
}

function renderMarkdown(md) {
  const lines = md.split(/\r?\n/);
  let html = "";
  let i = 0;

  function isTableSeparator(line) {
    return /^\s*\|?[\s:-]+\|[\s|:-]*\s*$/.test(line);
  }

  while (i < lines.length) {
    const line = lines[i];
    const next = lines[i + 1];
    if (line.includes("|") && next && isTableSeparator(next)) {
      const headers = line.split("|").map((c) => c.trim()).filter(Boolean);
      const rows = [];
      i += 2;
      while (i < lines.length && lines[i].includes("|")) {
        const cells = lines[i].split("|").map((c) => c.trim()).filter(Boolean);
        rows.push(cells);
        i += 1;
      }
      html += "<table><thead><tr>";
      headers.forEach((h) => (html += `<th>${escapeHtml(h)}</th>`));
      html += "</tr></thead><tbody>";
      rows.forEach((r) => {
        html += "<tr>";
        r.forEach((c) => (html += `<td>${escapeHtml(c)}</td>`));
        html += "</tr>";
      });
      html += "</tbody></table>";
      continue;
    }

    let block = escapeHtml(line);
    block = block.replace(/^### (.*)$/gm, "<h3>$1</h3>");
    block = block.replace(/^## (.*)$/gm, "<h2>$1</h2>");
    block = block.replace(/^# (.*)$/gm, "<h1>$1</h1>");
    block = block.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    block = block.replace(/\*(.+?)\*/g, "<em>$1</em>");
    block = block.replace(/`([^`]+)`/g, "<code>$1</code>");
    html += block + "<br>";
    i += 1;
  }

  return html;
}

function encodePath(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}

function setActiveTab(name) {
  tabs.forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  tabUpload.classList.toggle("hidden", name !== "upload");
  tabResults.classList.toggle("hidden", name !== "results");
  logsPanel.classList.toggle("hidden", name === "upload");
}

tabs.forEach((t) => {
  t.addEventListener("click", () => setActiveTab(t.dataset.tab));
});

function stripAnsi(text) {
  return text.replace(
    /[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g,
    ""
  );
}

function highlightJson(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(
      /(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*\"(?=\s*:))|(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*\")|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?/g,
      (match) => {
        if (match.startsWith("\"") && match.endsWith("\"")) {
          if (match.endsWith("\":")) {
            return `<span class="token-key">${match}</span>`;
          }
          return `<span class="token-string">${match}</span>`;
        }
        if (match === "true" || match === "false") {
          return `<span class="token-boolean">${match}</span>`;
        }
        if (match === "null") {
          return `<span class="token-null">${match}</span>`;
        }
        return `<span class="token-number">${match}</span>`;
      }
    );
}

function highlightLog(text) {
  const clean = stripAnsi(text);
  const escaped = clean.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return escaped
    .replace(
      /^\[\d{4}-\d{2}-\d{2}T[^\]]+\]/gm,
      (m) => `<span class="token-time">${m}</span>`
    )
    .replace(/(?:[A-Za-z]:)?[\\/][\w.\-\\/:]+/g, (m) => `<span class="token-path">${m}</span>`)
    .replace(/\b\d{1,3}%\b/g, (m) => `<span class="token-percent">${m}</span>`)
    .replace(/\b(Downloading|Fetching|Creating|Loading|Loaded)\b/g, '<span class="token-info">$1</span>')
    .replace(/\b(ERROR|Error|Failed)\b/g, '<span class="token-error">$1</span>')
    .replace(/\b(WARN|Warning|WARNING)\b/g, '<span class="token-warn">$1</span>')
    .replace(/\b(INFO|Info)\b/g, '<span class="token-info">$1</span>');
}

async function fetchDockerStatus() {
  const res = await fetch("/api/docker/status");
  const data = await res.json();
  if (!data.docker_ok) {
    dockerStatusEl.textContent = "Docker: not running";
    dockerStatusEl.style.color = "#ff7a7a";
    return;
  }
  dockerStatusEl.textContent = data.image_present ? "Docker: image ready" : "Docker: image missing";
  dockerStatusEl.style.color = data.image_present ? "#7af5a5" : "#ffcc66";
}

pullBtn.addEventListener("click", async () => {
  pullBtn.disabled = true;
  dockerStatusEl.textContent = "Docker: pulling image…";
  const res = await fetch("/api/docker/pull", { method: "POST" });
  const data = await res.json();
  dockerStatusEl.textContent = data.ok ? "Docker: image ready" : "Docker: pull failed";
  pullBtn.disabled = false;
});

function setFiles(files) {
  state.files = files;
  renderFileList();
}

function clearFilePreviews() {
  state.filePreviewUrls.forEach((url) => URL.revokeObjectURL(url));
  state.filePreviewUrls = [];
}

function renderFileList() {
  clearFilePreviews();
  fileList.innerHTML = "";
  if (!state.files.length) {
    const empty = document.createElement("div");
    empty.className = "small";
    empty.textContent = "No files selected";
    fileList.appendChild(empty);
    return;
  }

  state.files.forEach((f, idx) => {
    const card = document.createElement("div");
    card.className = "file-card";

    const thumb = document.createElement("div");
    thumb.className = "file-thumb";
    const ext = f.name.split(".").pop().toLowerCase();
    if (["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"].includes(ext)) {
      const url = URL.createObjectURL(f);
      state.filePreviewUrls.push(url);
      const img = document.createElement("img");
      img.src = url;
      thumb.appendChild(img);
    } else {
      thumb.textContent = ext.toUpperCase();
    }

    const name = document.createElement("div");
    name.className = "file-name";
    name.textContent = f.name;

    const actions = document.createElement("div");
    actions.className = "file-actions";
    const removeBtn = document.createElement("button");
    removeBtn.className = "btn icon";
    removeBtn.textContent = "✕";
    removeBtn.title = "Remove";
    removeBtn.addEventListener("click", () => {
      state.files.splice(idx, 1);
      renderFileList();
    });
    actions.appendChild(removeBtn);

    card.appendChild(thumb);
    card.appendChild(name);
    card.appendChild(actions);
    fileList.appendChild(card);
  });
}

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.style.borderColor = "#3b6ef5";
});

dropzone.addEventListener("dragleave", () => {
  dropzone.style.borderColor = "#3a3f4b";
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.style.borderColor = "#3a3f4b";
  setFiles(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener("change", (e) => {
  setFiles(Array.from(e.target.files));
});

startBtn.addEventListener("click", async () => {
  if (!state.files.length) {
    alert("No files selected");
    return;
  }
  const fd = new FormData();
  state.files.forEach((f) => fd.append("files", f));
  fd.append("device", deviceSelect.value);
  startBtn.disabled = true;
  const res = await fetch("/api/jobs", { method: "POST", body: fd });
  startBtn.disabled = false;
  if (!res.ok) {
    const err = await res.json();
    alert(err.detail || "Upload failed");
    return;
  }
  await loadJobs();
});

async function loadJobs() {
  const res = await fetch("/api/jobs");
  state.jobs = await res.json();
  renderJobs();
}

function renderJobs() {
  jobsList.innerHTML = "";
  state.jobs.forEach((job) => {
    const item = document.createElement("div");
    item.className = "item" + (job.id === state.activeJobId ? " active" : "");
    const title = document.createElement("div");
    title.textContent = job.id;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `${job.status} • ${job.created_at || ""}`;
    item.appendChild(title);
    item.appendChild(meta);
    item.addEventListener("click", () => selectJob(job.id));
    jobsList.appendChild(item);
  });
  if (!state.activeJobId && state.jobs.length) {
    selectJob(state.jobs[0].id);
  }
}

async function selectJob(jobId) {
  state.activeJobId = jobId;
  state.logOffset = 0;
  state.logText = "";
  logArea.textContent = "";
  renderJobs();
  await loadOutputs(jobId);
  startLogPolling(jobId);
  downloadZipBtn.disabled = false;
  setActiveTab("results");
}

async function loadOutputs(jobId) {
  outputsList.innerHTML = "";
  previewArea.innerHTML = "";
  previewTitle.textContent = "No file selected";
  const res = await fetch(`/api/jobs/${jobId}/files`);
  if (!res.ok) return;
  const data = await res.json();
  data.files.forEach((path) => {
    const item = document.createElement("div");
    item.className = "item";
    const name = document.createElement("div");
    name.className = "name";
    name.textContent = path;
    const actions = document.createElement("div");
    actions.className = "actions";
    const previewBtn = document.createElement("button");
    previewBtn.className = "btn";
    previewBtn.textContent = "Preview";
    previewBtn.addEventListener("click", () => previewFile(jobId, path));
    const downloadBtn = document.createElement("button");
    downloadBtn.className = "btn";
    downloadBtn.textContent = "Download";
    downloadBtn.addEventListener("click", () => {
      window.location.href = `/api/jobs/${jobId}/file/${encodePath(path)}`;
    });
    actions.appendChild(previewBtn);
    actions.appendChild(downloadBtn);
    item.appendChild(name);
    item.appendChild(actions);
    outputsList.appendChild(item);
  });
}

async function previewFile(jobId, path) {
  previewTitle.textContent = path;
  const ext = path.split(".").pop().toLowerCase();
  if (["md", "txt", "json"].includes(ext)) {
    const res = await fetch(`/api/jobs/${jobId}/file/${encodePath(path)}`);
    const text = await res.text();
    if (ext === "md") {
      previewArea.innerHTML = renderMarkdown(text);
    } else if (ext === "json") {
      let pretty = text;
      try {
        pretty = JSON.stringify(JSON.parse(text), null, 2);
      } catch {
        // keep raw
      }
      previewArea.innerHTML = `<pre class="code">${highlightJson(pretty)}</pre>`;
    } else {
      previewArea.innerHTML = `<pre class="code">${escapeHtml(text)}</pre>`;
    }
    return;
  }
  if (["jpg", "jpeg", "png"].includes(ext)) {
    const img = document.createElement("img");
    img.src = `/api/jobs/${jobId}/file/${encodePath(path)}`;
    previewArea.innerHTML = "";
    previewArea.appendChild(img);
    return;
  }
  previewArea.innerHTML = `<a href="/api/jobs/${jobId}/file/${encodePath(path)}">Download</a>`;
}

function startLogPolling(jobId) {
  if (state.logTimer) clearInterval(state.logTimer);
  state.logTimer = setInterval(async () => {
    const res = await fetch(`/api/jobs/${jobId}/logs?offset=${state.logOffset}`);
    if (!res.ok) return;
    const data = await res.json();
    if (data.text) {
      state.logText += data.text;
      state.logOffset = data.next_offset;
      logArea.innerHTML = highlightLog(state.logText);
      logArea.scrollTop = logArea.scrollHeight;
    }
  }, 2000);
}

downloadZipBtn.addEventListener("click", () => {
  if (!state.activeJobId) return;
  window.location.href = `/api/jobs/${state.activeJobId}/download`;
});

toggleSidebarBtn.addEventListener("click", () => {
  layoutEl.classList.toggle("collapsed");
  toggleSidebarBtn.textContent = layoutEl.classList.contains("collapsed") ? "⟩" : "⟨";
});

fetchDockerStatus();
loadJobs();
setInterval(loadJobs, 5000);
setActiveTab("upload");
