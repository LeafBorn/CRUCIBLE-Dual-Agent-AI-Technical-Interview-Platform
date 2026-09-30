// Preparation Page Logic: Documents Listing, PDF Previews, and Cheatsheet Generation

document.addEventListener("DOMContentLoaded", () => {
  if (!API.requireAuth()) return;
  API.renderUserBadge();
  loadDocuments();
});

function showAlert(msg, isSuccess = false) {
  const alertBox = document.getElementById("prepAlert");
  if (!alertBox) return;
  alertBox.textContent = msg;
  alertBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
  alertBox.classList.remove("d-none");
}

function hideAlert() {
  const alertBox = document.getElementById("prepAlert");
  if (alertBox) alertBox.classList.add("d-none");
}

async function loadDocuments() {
  hideAlert();
  const tbody = document.getElementById("documentsTableBody");

  try {
    const res = await API.get("/api/documents/list");
    const docs = res.documents || [];

    if (docs.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">
            No documents found in the documents directory.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = "";
    docs.forEach(doc => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>
          <div class="d-flex align-center gap-2">
            <svg style="width: 18px; height: 18px; color: var(--primary); flex-shrink: 0;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <span style="font-weight: 500;">${escapeHtml(doc.name)}</span>
          </div>
        </td>
        <td style="font-weight: 600; color: #4b5563; font-size: 0.85rem;">${doc.size_display}</td>
        <td style="font-weight: 600; color: #4b5563; font-size: 0.85rem;">${doc.modified}</td>
        <td style="text-align: center;">
          <div class="d-flex justify-between" style="justify-content: center; gap: 0.5rem;">
            <button class="btn-brutal-white" style="padding: 0.35rem 0.85rem; font-size: 0.8rem;" onclick="openPdfPreview('${escapeHtml(doc.name)}', '${doc.view_url}', '${doc.download_url}')">Preview</button>
            <a href="${doc.download_url}" class="btn-brutal-red btn-brutal-sm" download style="padding: 0.35rem 0.9rem; font-size: 0.8rem;">Download</a>
          </div>
        </td>
      `;

      tbody.appendChild(tr);
    });
  } catch (err) {
    showAlert(err.message || "Failed to load preparation documents.");
  }
}

function openPdfPreview(filename, viewUrl, downloadUrl) {
  document.getElementById("modalDocTitle").textContent = filename;
  const iframe = document.getElementById("docViewerIframe");
  iframe.src = viewUrl;

  const downloadBtn = document.getElementById("modalDownloadLink");
  downloadBtn.href = downloadUrl;

  document.getElementById("pdfViewerModal").classList.add("active");
}

function closePdfModal() {
  const modal = document.getElementById("pdfViewerModal");
  modal.classList.remove("active");
  document.getElementById("docViewerIframe").src = "about:blank";
}

async function triggerCheatsheetGeneration() {
  hideAlert();
  const btn = document.getElementById("genCheatsheetBtn");
  const originalHtml = btn.innerHTML;

  btn.disabled = true;
  btn.textContent = "Generating Cheatsheet...";

  try {
    const res = await API.post("/api/cheatsheet/generate", {});
    
    // Show success banner
    const resultCard = document.getElementById("cheatsheetResultCard");
    document.getElementById("cheatsheetFileName").textContent = res.filename;

    const previewBtn = document.getElementById("previewCheatsheetBtn");
    previewBtn.onclick = () => openPdfPreview(res.filename, res.view_url, res.download_url);

    const downloadBtn = document.getElementById("downloadCheatsheetBtn");
    downloadBtn.href = res.download_url;

    resultCard.classList.remove("d-none");
    showAlert("Cheatsheet generated and saved to documents folder!", true);

    // Refresh document table
    await loadDocuments();
  } catch (err) {
    showAlert(err.message || "Failed to generate cheatsheet.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
