(function () {
  "use strict";

  const UPLOAD_ENDPOINT = "/admin-portal/upload-media/";
  const STATUS_ENDPOINT = (id) => `/admin-portal/upload-media/status/${id}/`;

  const POLL_MS     = 2500;
  const MAX_WAIT_MS = 300_000;

  const CSRF = () =>
    document.querySelector('meta[name="csrf-token"]')?.content ||
    document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    "";

  const FIELD_RE = /^(image|video|file|thumbnail|profile_image|profile_logo)_url$/;

  const FIELD_META = {
    image:         { accept: "image/*", label: "image",     isImage: true,  isVideo: false },
    video:         { accept: "video/*", label: "video",     isImage: false, isVideo: true  },
    file:          { accept: "*/*",     label: "file",      isImage: false, isVideo: false },
    thumbnail:     { accept: "image/*", label: "thumbnail", isImage: true,  isVideo: false },
    profile_image: { accept: "image/*", label: "image",     isImage: true,  isVideo: false },
    profile_logo:  { accept: "image/*", label: "logo",      isImage: true,  isVideo: false },
  };

  /* ── SVG icons ────────────────────────────────────────────────────────────── */
  const SVG = {
    image: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
    video: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>`,
    file:  `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
    check: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    x:     `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
  };

   function mkEl(tag, cls) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

    async function safeJson(res) {
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      /* Django returned HTML — auth redirect, error page, rate-limit page, etc. */
      const text = await res.text();
      const hint =
        res.status === 301 || res.status === 302 ? "Session expired — please refresh and log in again." :
        res.status === 403 ? "Permission denied." :
        res.status === 429 ? "Too many uploads — try again later." :
        res.status === 503 ? "Upload queue unavailable — is Celery running?" :
        `Server returned ${res.status} (non-JSON).`;
      throw new Error(hint);
    }
    return res.json();
  }

  function buildWidget(hiddenInput) {
    const name   = hiddenInput.name || hiddenInput.id || "";
    const prefix = Object.keys(FIELD_META).find(k => name.startsWith(k)) || "file";
    const meta   = FIELD_META[prefix];
    const icon   = SVG[meta.isImage ? "image" : meta.isVideo ? "video" : "file"];

    const wrap     = mkEl("div", "mu-wrap");
    const zone     = mkEl("div", "mu-zone");
    const clrBtn   = mkEl("button", "mu-clear");
    const idleWrap = mkEl("div", "mu-idle-wrap");
    const rail     = mkEl("div", "mu-rail");
    const bar      = mkEl("div", "mu-bar");
    const statusEl = mkEl("div", "mu-status is-idle");  
    const fileIn   = mkEl("input", "mu-hidden");

    zone.tabIndex = 0;
    zone.setAttribute("role", "button");
    zone.setAttribute("aria-label", `Upload ${meta.label}`);

    clrBtn.type      = "button";
    clrBtn.title     = "Remove file";
    clrBtn.innerHTML = SVG.x;

    fileIn.type   = "file";
    fileIn.accept = meta.accept;

    idleWrap.innerHTML = `
      <div class="mu-idle-icon">${icon}</div>
      <div class="mu-idle-text">Click or drag & drop</div>
      <div class="mu-idle-sub">Upload a ${meta.label}</div>
    `;

    rail.appendChild(bar);
    zone.appendChild(clrBtn);
    zone.appendChild(idleWrap);
    wrap.appendChild(fileIn);
    wrap.appendChild(zone);
    wrap.appendChild(statusEl);
    wrap.appendChild(rail);

    /* edit form — show existing URL immediately */
    const existingUrl = hiddenInput.value.trim();
    if (existingUrl) {
      renderPreview(zone, idleWrap, existingUrl, meta, null);
      setStatus(statusEl, "done", "Current file");
      bar.style.width = "100%";
    }

    /* ── Events ───────────────────────────────────────────────────────────── */
    zone.addEventListener("click", (e) => {
      if (e.target.closest(".mu-clear")) return;
      fileIn.click();
    });
    zone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileIn.click(); }
    });

    zone.addEventListener("dragover",  (e) => { e.preventDefault(); zone.classList.add("mu-over"); });
    zone.addEventListener("dragleave", ()  => zone.classList.remove("mu-over"));
    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      zone.classList.remove("mu-over");
      const f = e.dataTransfer.files[0];
      if (f) startUpload(f);
    });

    fileIn.addEventListener("change", () => {
      if (fileIn.files[0]) startUpload(fileIn.files[0]);
    });

    clrBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      hiddenInput.value = "";
      clearPreview(zone, idleWrap);
      setStatus(statusEl, "idle", "");
      bar.style.width = "0%";
    });

    /* ── Upload flow ──────────────────────────────────────────────────────── */
    async function startUpload(file) {
      renderPreview(zone, idleWrap, null, meta, file);
      setStatus(statusEl, "working", "Saving to server…");
      bar.style.width = "15%";

      const fd = new FormData();
      fd.append("file", file);

      let taskId;
      try {
        const res = await fetch(UPLOAD_ENDPOINT, {
          method:  "POST",
          headers: {
            "X-CSRFToken":      CSRF(),
            "X-Requested-With": "XMLHttpRequest",   
          },
          body: fd,
        });

        const data = await safeJson(res);

        if (!res.ok || data.error) {
          throw new Error(data.error || `Server error ${res.status}`);
        }

        /* { task_id: "...", status: "processing" }
           Celery worker now has the file — compressing + uploading to Cloudinary */
        taskId = data.task_id;
        bar.style.width = "30%";
        setStatus(statusEl, "working", "Compressing & uploading to Cloudinary…");

      } catch (err) {
        setStatus(statusEl, "error", `✗ ${err.message}`);
        bar.style.width = "0%";
        clearPreview(zone, idleWrap);
        return;
      }

      /* ── Poll until Celery task finishes ────────────────────────────────── */
      const started = Date.now();

      const timer = setInterval(async () => {
        if (Date.now() - started > MAX_WAIT_MS) {
          clearInterval(timer);
          setStatus(statusEl, "error", "Timed out — try again");
          bar.style.width = "0%";
          return;
        }

        let data;
        try {
          const res = await fetch(STATUS_ENDPOINT(taskId), {
            headers: { "X-Requested-With": "XMLHttpRequest" },          });
        
          data = await safeJson(res);
        } catch (err) {
        
          if (err.message.includes("Session") || err.message.includes("Permission")) {
            clearInterval(timer);
            setStatus(statusEl, "error", `✗ ${err.message}`);
            bar.style.width = "0%";
          }
          /* else: silent retry on next interval */
          return;
        }

        /* Possible states from upload_media_status view:
             pending  → Celery hasn't picked it up yet
             done     → { url, type } — write into hidden input
             failed   → { error } — show message
             started / retry → still working, nudge progress bar             */

        if (data.status === "done") {
          clearInterval(timer);
          hiddenInput.value = data.url;              
          renderPreview(zone, idleWrap, data.url, meta, file);
          setStatus(statusEl, "done", "Ready — file uploaded");
          bar.style.width = "100%";

        } else if (data.status === "failed") {
          clearInterval(timer);
          setStatus(statusEl, "error", `✗ Failed: ${data.error || "unknown error"}`);
          bar.style.width = "0%";
          clearPreview(zone, idleWrap);

        } else {
          /* pending / started / retry — nudge the bar forward */
          const cur = parseFloat(bar.style.width) || 30;
          bar.style.width = Math.min(cur + 4, 88) + "%";
        }

      }, POLL_MS);
    }

    return wrap;
  }

  /* ── Preview helpers ──────────────────────────────────────────────────────── */
  function renderPreview(zone, idleWrap, url, meta, file) {
    clearPreview(zone, idleWrap);
    zone.classList.add("mu-filled");
    idleWrap.style.display = "none";

    if (meta.isImage && (url || (file && file.type.startsWith("image/")))) {
      const img = document.createElement("img");
      img.className = "mu-preview-img";
      img.src = url || URL.createObjectURL(file);
      img.alt = "Preview";
      zone.appendChild(img);
    } else {
      const box = mkEl("div", "mu-preview-file");
      const iconSvg = meta.isVideo ? SVG.video : SVG.file;
      const label = file ? file.name : (url ? "Current file" : "File ready");
      box.innerHTML = `${iconSvg}<span>${label}</span>`;
      zone.appendChild(box);
    }

    const hint = mkEl("div", "mu-replace-hint");
    hint.textContent = "Click to replace";
    zone.appendChild(hint);
  }

  function clearPreview(zone, idleWrap) {
    zone.classList.remove("mu-filled");
    idleWrap.style.display = "";
    zone.querySelectorAll(".mu-preview-img, .mu-preview-file, .mu-replace-hint")
        .forEach(n => n.remove());
  }

  function setStatus(statusEl, state, text) {
    statusEl.className = `mu-status is-${state}`;
    if (state === "working") {
      statusEl.innerHTML = `<span class="mu-spinner"></span>${text}`;
    } else if (state === "done") {
      statusEl.innerHTML = `${SVG.check} ${text}`;
    } else {
      statusEl.textContent = text;
    }
  }

  /* ── Block form submit while any upload is still in progress ─────────────── */
  function guardSubmit() {
    document.addEventListener("submit", (e) => {
      const busy = document.querySelector(".mu-status.is-working");
      if (busy) {
        e.preventDefault();
        alert(
          "Please wait — media is still being compressed and uploaded to Cloudinary.\n\n" +
          "Submit again once all files show ✓"
        );
      }
    }, true);
  }

  /* ── Init: scan form and replace all matching URL inputs ─────────────────── */
  function init() {
    guardSubmit();

    document.querySelectorAll("input[type='url'], input[type='text']").forEach((input) => {
      const name = input.name || input.id || "";
      if (!FIELD_RE.test(name)) return;

      /* keep original input in DOM (hidden) — form still POSTs the URL value */
      input.classList.add("mu-hidden");

      const widget = buildWidget(input);
      input.insertAdjacentElement("afterend", widget);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();