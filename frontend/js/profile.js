// Candidate Profile & SQL History Viewer Logic

document.addEventListener("DOMContentLoaded", () => {
  if (!API.requireAuth()) return;
  API.renderUserBadge();
  loadProfile();
  loadHistory();
});

function showAlert(msg, isSuccess = false) {
  const alertBox = document.getElementById("profileAlert");
  if (!alertBox) return;
  alertBox.textContent = msg;
  alertBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
  alertBox.classList.remove("d-none");
}

function hideAlert() {
  const alertBox = document.getElementById("profileAlert");
  if (alertBox) alertBox.classList.add("d-none");
}

async function loadProfile() {
  hideAlert();
  try {
    const data = await API.get("/api/profile");
    if (!data) return;

    document.getElementById("profUsername").textContent = data.username || "--";
    document.getElementById("profTargetRoleInput").value = data.target_role === "Not specified" ? "" : (data.target_role || "");
    document.getElementById("profScore").textContent = `${data.score || 0}%`;

    renderTags("profResumeSkills", data.resume_skill || [], "pill-tag", "No resume skills recorded yet.");
    renderTags("profMatchingSkills", data.matching_skill || [], "pill-tag pill-tag-matched", "No matching skills recorded.");
    renderTags("profMissingSkills", data.missing_skill || [], "pill-tag pill-tag-missing", "None recorded.");
  } catch (err) {
    showAlert(err.message || "Failed to load candidate profile.");
  }
}

function renderTags(containerId, list, tagClass, emptyMsg) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!list || list.length === 0) {
    container.innerHTML = `<span style="color:#6b7280; font-size:0.85rem;">${emptyMsg}</span>`;
    return;
  }

  list.forEach(item => {
    const tag = document.createElement("span");
    tag.className = tagClass;
    tag.textContent = item;
    container.appendChild(tag);
  });
}

async function saveTargetRole() {
  hideAlert();
  const targetRole = document.getElementById("profTargetRoleInput").value.trim();

  try {
    await API.put("/api/profile", { target_role: targetRole });
    showAlert("Target role updated successfully!", true);
  } catch (err) {
    showAlert(err.message || "Failed to save target role.");
  }
}

let cachedHistory = [];
let modalChartInstance = null;

async function loadHistory() {
  const tbody = document.getElementById("historyTableBody");

  try {
    const res = await API.get("/api/profile/history");
    const history = res.history || [];
    cachedHistory = history;

    if (history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: #6b7280; padding: 2.5rem 1rem;">
            No interview history found yet. Go to <a href="/" style="color: var(--red-primary); font-weight: 700;">Home</a> to conduct your first mock interview!
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = "";
    history.forEach((h, idx) => {
      const tr = document.createElement("tr");

      // Format confidence badge matching Image 3 (Soft pink / pill)
      const conf = (h.confidence || "low").toLowerCase();
      let confBadge = `<span class="pill-tag" style="background:#fee2e2; color:#991b1b; padding:0.2rem 0.6rem; font-size:0.75rem;">${escapeHtml(h.confidence || 'Low')}</span>`;
      if (conf.includes("high")) {
        confBadge = `<span class="pill-tag pill-tag-matched" style="padding:0.2rem 0.6rem; font-size:0.75rem;">High</span>`;
      } else if (conf.includes("moderate")) {
        confBadge = `<span class="pill-tag" style="background:#fef08a; padding:0.2rem 0.6rem; font-size:0.75rem;">Moderate</span>`;
      }

      const hasBreaking = h.breaking_points && h.breaking_points.length > 0;

      tr.innerHTML = `
        <td style="font-size: 0.85rem; font-weight: 600; white-space: nowrap;">${escapeHtml(h.created_at || 'Recent')}</td>
        <td><strong style="color: #1d4ed8; font-size: 1.05rem;">${h.score}/100</strong></td>
        <td style="font-weight: 700;">${h.accuracy}%</td>
        <td><span style="color: ${h.blunder > 0 ? '#dc2626' : '#6b7280'}; font-weight: 800;">${h.blunder}</span></td>
        <td>${confBadge}</td>
        <td><strong>${h.streak}</strong></td>
        <td style="max-width: 260px; font-size: 0.85rem; color: #374151;">${escapeHtml(h.communication || '--')}</td>
        <td>
          <button class="btn-brutal-white" style="font-size:0.75rem; padding: 0.35rem 0.65rem; background: #bae6fd; font-weight: 800; cursor: pointer;" onclick="openTrajectoryModal(${idx})">
            📈 View Curve ${hasBreaking ? '⚠️' : ''}
          </button>
        </td>
      `;

      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--danger-text);">
          Failed to load interview history.
        </td>
      </tr>
    `;
  }
}

function openTrajectoryModal(idx) {
  const h = cachedHistory[idx];
  if (!h) return;

  const modal = document.getElementById("trajectoryModal");
  if (!modal) return;

  document.getElementById("modalSessionTitle").textContent = `Interview Session #${h.id} Reaction Curve`;
  document.getElementById("modalSessionDate").textContent = `Recorded: ${h.created_at || 'Recent'}`;
  document.getElementById("modalPeakDiff").textContent = `Peak Difficulty: ${(Number(h.peak_difficulty) || 5.0).toFixed(1)} / 10`;
  document.getElementById("modalAvgConf").textContent = `Avg Confidence: ${((Number(h.avg_confidence) || 0.5) * 100).toFixed(0)}%`;

  // Render Breaking Points
  const bpContainer = document.getElementById("modalBreakingPoints");
  const bps = h.breaking_points || [];
  if (bps.length > 0) {
    bpContainer.innerHTML = `
      <div style="background-color: #fee2e2; border: 2px solid #dc2626; border-radius: 8px; padding: 0.65rem 0.85rem; color: #991b1b; font-weight: 700; font-size: 0.825rem;">
        ⚠️ <strong>Identified Breaking Points:</strong> ${bps.map(b => escapeHtml(b)).join(", ")} (3 consecutive low-confidence turns).
      </div>
    `;
  } else {
    bpContainer.innerHTML = `
      <div style="background-color: #dcfce7; border: 2px solid #16a34a; border-radius: 8px; padding: 0.65rem 0.85rem; color: #166534; font-weight: 700; font-size: 0.825rem;">
        ✅ <strong>No Breaking Points Hit:</strong> Candidate maintained resilience throughout the difficulty shifts.
      </div>
    `;
  }

  // Render Chart
  const turns = h.turns_data || [];
  const canvas = document.getElementById("modalTrajectoryChart");
  if (canvas && typeof Chart !== "undefined") {
    const labels = turns.length > 0 ? turns.map(t => `Turn ${t.turn}`) : ['Start'];
    const confData = turns.length > 0 ? turns.map(t => Number(t.confidence)) : [0.5];
    const diffData = turns.length > 0 ? turns.map(t => Number(t.difficulty)) : [5.0];

    if (modalChartInstance) {
      modalChartInstance.destroy();
    }

    const ctx = canvas.getContext("2d");
    modalChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Candidate Confidence (0.0 - 1.0)',
            data: confData,
            borderColor: '#0284c7',
            backgroundColor: 'rgba(2, 132, 199, 0.15)',
            borderWidth: 3,
            pointRadius: 6,
            pointBackgroundColor: '#0284c7',
            tension: 0.35,
            yAxisID: 'yConf'
          },
          {
            label: 'Difficulty Level (1 - 10)',
            data: diffData,
            borderColor: '#e11d24',
            backgroundColor: 'rgba(225, 29, 36, 0.15)',
            borderWidth: 3,
            pointRadius: 6,
            pointBackgroundColor: '#e11d24',
            tension: 0.35,
            yAxisID: 'yDiff'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { font: { family: "'Space Mono', monospace", weight: 'bold' } } },
          yConf: {
            type: 'linear',
            position: 'left',
            min: 0,
            max: 1.0,
            ticks: { stepSize: 0.2, color: '#0284c7', font: { weight: 'bold' } },
            title: { display: true, text: 'Confidence', color: '#0284c7', font: { weight: 'bold' } }
          },
          yDiff: {
            type: 'linear',
            position: 'right',
            min: 1,
            max: 10,
            ticks: { stepSize: 2, color: '#e11d24', font: { weight: 'bold' } },
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'Difficulty', color: '#e11d24', font: { weight: 'bold' } }
          }
        }
      }
    });
  }

  // Populate Turns Table
  const turnsBody = document.getElementById("modalTurnsTableBody");
  if (turnsBody) {
    if (turns.length === 0) {
      turnsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #6b7280; padding: 1rem;">No granular turn metrics archived for this older session.</td></tr>`;
    } else {
      turnsBody.innerHTML = "";
      turns.forEach(t => {
        const row = document.createElement("tr");
        const strat = (t.strategy || "maintain").toLowerCase();
        let badgeClass = "strategy-badge-pill";
        if (strat.includes("push")) badgeClass += " push";
        else if (strat.includes("pivot")) badgeClass += " pivot";
        else if (strat.includes("breaking")) badgeClass += " breaking";
        else if (strat.includes("ease")) badgeClass += " ease";
        else badgeClass += " maintain";

        row.innerHTML = `
          <td style="font-weight: 800;">#${t.turn}</td>
          <td>
            <div style="font-weight: 700; color: #1f2937; margin-bottom: 0.2rem;">Q: ${escapeHtml(t.question || '')}</div>
            <div style="color: #4b5563; font-style: italic;">A: ${escapeHtml((t.answer || '').slice(0, 120))}${t.answer && t.answer.length > 120 ? '...' : ''}</div>
          </td>
          <td style="font-weight: 700; white-space: nowrap;">${t.latency_seconds || 0}s</td>
          <td><span style="font-weight: 800; color: #0284c7;">${((Number(t.confidence) || 0) * 100).toFixed(0)}%</span></td>
          <td><span style="font-weight: 800; color: #e11d24;">${Number(t.difficulty || 5).toFixed(1)}/10</span></td>
          <td><span class="${badgeClass}" style="font-size: 0.7rem; padding: 0.2rem 0.5rem;">${(t.strategy || 'MAINTAIN').toUpperCase()}</span></td>
        `;
        turnsBody.appendChild(row);
      });
    }
  }

  modal.classList.remove("d-none");
}

function closeTrajectoryModal() {
  const modal = document.getElementById("trajectoryModal");
  if (modal) modal.classList.add("d-none");
  if (modalChartInstance) {
    modalChartInstance.destroy();
    modalChartInstance = null;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
