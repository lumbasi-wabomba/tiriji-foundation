// js file for handling media uploads to Cloudinary in the admin portal (for images, videos, files)
(function () {
  "use strict";

  const SIG_ENDPOINT = "/admin-portal/cloudinary-signature/";
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

  const IMAGE_EXTS = ["jpg","jpeg","png","gif","webp","bmp","tiff","svg"];
  const VIDEO_EXTS = ["mp4","mov","avi","mkv","webm","m4v"];

  function resourceType(file) {
    const ext = file.name.split(".").pop().toLowerCase();
    if (IMAGE_EXTS.includes(ext)) return "image";
    if (VIDEO_EXTS.includes(ext)) return "video";
    return "raw";
  }

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
      const hint =
        res.status === 302 || res.status === 301 ? "Session expired — please refresh and log in again." :
        res.status === 403 ? "Permission denied." :
        res.status === 429 ? "Too many requests — try again later." :
        `Server error ${res.status}.`;
      throw new Error(hint);
    }
    return res.json();
  }

  function xhrUpload(url, formData, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", url);

      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
      });

      xhr.addEventListener("load", () => {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          reject(new Error("Cloudinary returned non-JSON response."));
        }
      });

      xhr.addEventListener("error",  () => reject(new Error("Network error during upload.")));
      xhr.addEventListener("abort",  () => reject(new Error("Upload cancelled.")));
      xhr.send(formData);
    });
  }

  /* ── Widget factory ───────────────────────────────────────────────────────── */
  function buildWidget(hiddenInput) {
    const name   = hiddenInput.name || hiddenInput.id || "";
    const prefix = Object.keys(FIELD_META).find(k => name.startsWith(k)) || "file";
    const meta   = FIELD_META[prefix];
    const icon   = SVG[meta.isImage ? "image" : meta.isVideo ? "video" : "file"];

    /* ── DOM skeleton ── */
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
    clrBtn.title     = "Remove";
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

    /* existing URL on edit form */
    const existingUrl = hiddenInput.value.trim();
    if (existingUrl) {
      renderPreview(zone, idleWrap, existingUrl, meta, null);
      setStatus(statusEl, "done", "Current file");
      bar.style.width = "100%";
    }

    zone.addEventListener("click",   (e) => { if (!e.target.closest(".mu-clear")) fileIn.click(); });
    zone.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileIn.click(); } });

    zone.addEventListener("dragover",  (e) => { e.preventDefault(); zone.classList.add("mu-over"); });
    zone.addEventListener("dragleave", ()  => zone.classList.remove("mu-over"));
    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      zone.classList.remove("mu-over");
      if (e.dataTransfer.files[0]) startUpload(e.dataTransfer.files[0]);
    });

    fileIn.addEventListener("change", () => { if (fileIn.files[0]) startUpload(fileIn.files[0]); });

    clrBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      hiddenInput.value = "";
      clearPreview(zone, idleWrap);
      setStatus(statusEl, "idle", "");
      bar.style.width = "0%";
    });

    async function startUpload(file) {
      renderPreview(zone, idleWrap, null, meta, file);
      setStatus(statusEl, "working", "Preparing upload…");
      bar.style.width = "5%";

      let sig;
      try {
        const res = await fetch(SIG_ENDPOINT, {
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken":      CSRF(),
          },
        });
        sig = await safeJson(res);
        if (sig.error) throw new Error(sig.error);
      } catch (err) {
        setStatus(statusEl, "error", `✗ ${err.message}`);
        bar.style.width = "0%";
        clearPreview(zone, idleWrap);
        return;
      }

      const rType  = resourceType(file);
      const apiUrl = `https://api.cloudinary.com/v1_1/${sig.cloud_name}/${rType}/upload/q_auto:best,f_auto,w_1920,c_limit,e_auto_enhance,e_auto_color/`;

      const fd = new FormData();
      fd.append("file",           file);
      fd.append("api_key",        sig.api_key);
      fd.append("timestamp",      sig.timestamp);
      fd.append("signature",      sig.signature);
      fd.append("folder",         sig.folder);
      fd.append("transformations", sig.transformations);
      
        // ← matches signature, no mismatch
      // if (rType === "image") {
      //   fd.append("transformation", "q_auto,f_auto");
      // } else if (rType === "video") {
      //   fd.append("eager",               "vc_auto,q_auto");
      //   fd.append("eager_async",         "true");
      // }

      setStatus(statusEl, "working", "Uploading…");

      try {
        const data = await xhrUpload(apiUrl, fd, (pct) => {

          bar.style.width = pct + "%";
          setStatus(statusEl, "working", `Uploading… ${pct}%`);
        });

        if (data.error) throw new Error(data.error.message);

        hiddenInput.value = data.secure_url;
        renderPreview(zone, idleWrap, data.secure_url, meta, file);
        setStatus(statusEl, "done", "✓ Uploaded");
        bar.style.width = "100%";

      } catch (err) {
        setStatus(statusEl, "error", `✗ ${err.message}`);
        bar.style.width = "0%";
        clearPreview(zone, idleWrap);
      }
    }

    return wrap;
  }

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
      box.innerHTML = `${meta.isVideo ? SVG.video : SVG.file}<span>${file ? file.name : "Current file"}</span>`;
      zone.appendChild(box);
    }

    const hint = mkEl("div", "mu-replace-hint");
    hint.textContent = "Click to replace";
    zone.appendChild(hint);
  }

  function clearPreview(zone, idleWrap) {
    zone.classList.remove("mu-filled");
    idleWrap.style.display = "";
    zone.querySelectorAll(".mu-preview-img, .mu-preview-file, .mu-replace-hint").forEach(n => n.remove());
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

  function guardSubmit() {
    document.addEventListener("submit", (e) => {
      if (document.querySelector(".mu-status.is-working")) {
        e.preventDefault();
        alert("Please wait — a file is still uploading.\nSubmit again once you see ✓");
      }
    }, true);
  }

  function init() {
    guardSubmit();
    document.querySelectorAll("input[type='url'], input[type='text']").forEach((input) => {
      const name = input.name || input.id || "";
      if (!FIELD_RE.test(name)) return;
      input.classList.add("mu-hidden");
      input.insertAdjacentElement("afterend", buildWidget(input));
    });
  }

  document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", init)
    : init();

})();