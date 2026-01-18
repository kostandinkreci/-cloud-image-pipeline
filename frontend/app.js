const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusEl = document.getElementById("status");
const originalPreview = document.getElementById("originalPreview");
const thumbPreview = document.getElementById("thumbPreview");
const jobLink = document.getElementById("jobLink");

const UPLOAD_ENDPOINT = "/api/v1/images";

let latestThumbUrl = null;
let latestJobId = null;

function setStatus(msg) {
  statusEl.textContent = msg;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function formatBytes(bytes) {
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let v = bytes;
  while (v >= 1024 && i < units.length - 1) {
    v = v / 1024;
    i++;
  }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function resetJobLink() {
  jobLink.textContent = "—";
  jobLink.href = "#";
}

function resetDownload() {
  latestThumbUrl = null;
  latestJobId = null;
  downloadBtn.disabled = true;
}

async function downloadFromUrl(url, filename) {
  // Fetch blob to force a real "download" across origins/presigned URLs
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Download failed (${res.status})`);

  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  // Cleanup
  setTimeout(() => URL.revokeObjectURL(objectUrl), 2000);
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (!file) return;

  // Local preview immediately
  originalPreview.src = URL.createObjectURL(file);

  // Clear old thumbnail
  thumbPreview.removeAttribute("src");

  resetJobLink();
  resetDownload();

  setStatus(`Selected: ${file.name} (${formatBytes(file.size)})`);
});

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("Please choose an image first.");
    return;
  }

  uploadBtn.disabled = true;
  downloadBtn.disabled = true;
  setStatus("Uploading to API...");

  try {
    // 1) Upload -> get job ID
    const formData = new FormData();
    formData.append("file", file);

    const uploadRes = await fetch(UPLOAD_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!uploadRes.ok) {
      const text = await uploadRes.text();
      throw new Error(`Upload failed (${uploadRes.status}): ${text}`);
    }

    const { id: jobId } = await uploadRes.json();
    latestJobId = jobId;

    const jobEndpoint = `/api/v1/images/${jobId}`;

    // Update Job link
    jobLink.textContent = jobId;
    jobLink.href = jobEndpoint;

    setStatus(`Uploaded ✅ Job queued… (Job: ${jobId})`);

    // 2) Poll job until thumbnail appears
    for (let i = 0; i < 60; i++) {
      const jobRes = await fetch(jobEndpoint);

      if (!jobRes.ok) {
        const text = await jobRes.text();
        throw new Error(`Job check failed (${jobRes.status}): ${text}`);
      }

      const jobJson = await jobRes.json();

      if (jobJson.status === "FAILED") {
        setStatus(`Job failed ❌ ${jobJson.error_message || ""}`.trim());
        return;
      }

      const variants = jobJson.variants || [];
      const thumb = variants.find((v) => v.type === "thumbnail");

      if (thumb?.url) {
        latestThumbUrl = thumb.url;
        thumbPreview.src = thumb.url;

        downloadBtn.disabled = false;
        setStatus(`Thumbnail ready ✅ (Job: ${jobId})`);
        return;
      }

      setStatus(`Processing in worker… (${i + 1}/60)`);
      await sleep(1000);
    }

    setStatus("Timeout ⏳ Thumbnail not ready yet. Check worker logs.");
  } catch (err) {
    console.error(err);
    setStatus("Error: " + err.message);
  } finally {
    uploadBtn.disabled = false;
  }
});

downloadBtn.addEventListener("click", async () => {
  try {
    if (!latestThumbUrl || !latestJobId) return;

    downloadBtn.disabled = true;
    setStatus("Downloading thumbnail...");

    await downloadFromUrl(latestThumbUrl, `thumbnail-${latestJobId}.jpg`);

    setStatus(`Downloaded ✅ (Job: ${latestJobId})`);
  } catch (err) {
    console.error(err);
    setStatus("Download error: " + err.message);
  } finally {
    // Re-enable if thumbnail still exists
    downloadBtn.disabled = !latestThumbUrl;
  }
});
