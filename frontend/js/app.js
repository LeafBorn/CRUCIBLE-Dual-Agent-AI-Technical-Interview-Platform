// Home Page Application Logic: Resume Loading, Skill Matching, and Instant Interview Launch

let resumeText = "";
let resumeSkills = [];
let matchingSkills = [];
let missingSkills = [];

document.addEventListener("DOMContentLoaded", async () => {
  if (!API.requireAuth()) return;
  API.renderUserBadge();
  setupDragAndDrop();
  await loadCurrentResumeIfExists();
});

function showAlert(msg, isSuccess = false) {
  const alertBox = document.getElementById("homeAlert");
  if (!alertBox) return;
  alertBox.textContent = msg;
  alertBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'}`;
  alertBox.classList.remove("d-none");
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideAlert() {
  const alertBox = document.getElementById("homeAlert");
  if (alertBox) alertBox.classList.add("d-none");
}

async function loadCurrentResumeIfExists() {
  try {
    const res = await API.get("/api/resume/current");
    if (res && res.has_resume) {
      resumeText = res.resume_text || "";
      resumeSkills = res.resume_skills || [];
      matchingSkills = res.matching_skills || [];
      missingSkills = res.missing_skills || [];

      if (res.target_role) {
        const roleInput = document.getElementById("targetRoleInput");
        if (roleInput) roleInput.value = res.target_role;
      }

      document.getElementById("loadedFileName").textContent = "Active Resume Document";
      document.getElementById("loadedFilePages").textContent = "";
      document.getElementById("uploadStatus").classList.remove("d-none");

      if (resumeSkills.length > 0) {
        const countBadge = document.getElementById("skillsCountBadge");
        if (countBadge) {
          countBadge.textContent = `${resumeSkills.length}`;
          countBadge.classList.remove("d-none");
        }
      }
    }
  } catch (e) {
    console.log("No previous resume active:", e);
  }
}

// ----------------- Drag & Drop / File Upload -----------------
function setupDragAndDrop() {
  const dropZone = document.getElementById("dropZone");
  if (!dropZone) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    }, false);
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
    }, false);
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadResumeFile(files[0]);
    }
  });
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files && files.length > 0) {
    uploadResumeFile(files[0]);
  }
}

async function uploadResumeFile(file) {
  hideAlert();
  const formData = new FormData();
  formData.append("file", file);

  const dropZone = document.getElementById("dropZone");
  const uploadText = dropZone.querySelector(".upload-text");
  const originalText = uploadText.innerHTML;
  uploadText.textContent = "Processing and extracting skills...";

  try {
    const res = await API.upload("/api/resume/upload", formData);
    resumeText = res.text || "";
    resumeSkills = res.resume_skills || [];

    // Update UI
    document.getElementById("loadedFileName").textContent = res.filename;
    document.getElementById("loadedFilePages").textContent = `(${res.pages} page${res.pages > 1 ? 's' : ''})`;
    document.getElementById("uploadStatus").classList.remove("d-none");

    // Display detected skills immediately
    renderResumeSkills(resumeSkills);
    showAlert("Resume uploaded and parsed successfully!", true);
  } catch (err) {
    showAlert(err.message || "Failed to upload resume document.");
  } finally {
    uploadText.innerHTML = originalText;
  }
}

// ----------------- Resume Skills Action Button & Renderer -----------------
function renderResumeSkills(skills) {
  const tagsContainer = document.getElementById("resumeSkillsTags");
  const skillsBlock = document.getElementById("skillsDetectedBlock");
  const countBadge = document.getElementById("skillsCountBadge");

  if (!tagsContainer || !skillsBlock) return;

  tagsContainer.innerHTML = "";
  if (skills && skills.length > 0) {
    skills.forEach(skill => {
      const tag = document.createElement("span");
      tag.className = "pill-tag";
      tag.textContent = skill;
      tagsContainer.appendChild(tag);
    });
    if (countBadge) {
      countBadge.textContent = `${skills.length}`;
      countBadge.classList.remove("d-none");
    }
    skillsBlock.classList.remove("d-none");
  } else {
    tagsContainer.innerHTML = "<span style='font-size:0.85rem;color:#6b7280;font-weight:600;'>No technical skills detected in the document text.</span>";
    skillsBlock.classList.remove("d-none");
  }
}

async function extractOrShowResumeSkills() {
  hideAlert();
  const skillsBlock = document.getElementById("skillsDetectedBlock");

  // If already displayed, inform user
  if (skillsBlock && !skillsBlock.classList.contains("d-none") && resumeSkills.length > 0) {
    showAlert(`Currently displaying ${resumeSkills.length} detected skills from your resume.`, true);
    return;
  }

  // If no resume in memory, try to load current resume from server
  if (!resumeText) {
    try {
      const res = await API.get("/api/resume/current");
      if (res && res.has_resume) {
        resumeText = res.resume_text || "";
        resumeSkills = res.resume_skills || [];
        matchingSkills = res.matching_skills || [];
        missingSkills = res.missing_skills || [];
        document.getElementById("loadedFileName").textContent = "Active Resume Document";
        document.getElementById("uploadStatus").classList.remove("d-none");
      }
    } catch(e) {}
  }

  if (!resumeText) {
    showAlert("Please upload your resume first to view or extract skills.");
    return;
  }

  // If we have resume text but skills list is empty, extract skills
  if (!resumeSkills || resumeSkills.length === 0) {
    try {
      const res = await API.post("/api/skills/match", {
        resume_text: resumeText,
        job_description: "",
        target_role: document.getElementById("targetRoleInput")?.value?.trim() || ""
      });
      resumeSkills = res.resume_skills || [];
    } catch(err) {
      console.error(err);
    }
  }

  renderResumeSkills(resumeSkills);
  showAlert(`Extracted ${resumeSkills.length} skills from your resume!`, true);
}

// ----------------- Skill Matching -----------------
async function matchSkillsWithJD() {
  hideAlert();
  if (!resumeText) {
    try {
      const cur = await API.get("/api/resume/current");
      if (cur && cur.has_resume) {
        resumeText = cur.resume_text;
      }
    } catch(e) {}
  }

  if (!resumeText) {
    showAlert("Please upload your resume first before analyzing skill match.");
    return;
  }

  const jd = document.getElementById("jdInput").value.trim();
  const targetRole = document.getElementById("targetRoleInput").value.trim();

  try {
    const res = await API.post("/api/skills/match", {
      resume_text: resumeText,
      job_description: jd,
      target_role: targetRole
    });

    matchingSkills = res.matching_skills || [];
    missingSkills = res.missing_skills || [];

    const resultsBlock = document.getElementById("skillMatchResults");
    const scoreVal = document.getElementById("matchScoreVal");
    const donutVisual = document.getElementById("donutScoreVisual");
    const matchContainer = document.getElementById("matchingSkillsTags");
    const missContainer = document.getElementById("missingSkillsTags");

    if (res.has_jd) {
      const score = res.score || 0;
      scoreVal.textContent = `${score}%`;
      if (donutVisual) {
        donutVisual.style.background = `conic-gradient(#38bdf8 ${score * 3.6}deg, #e0f2fe ${score * 3.6}deg)`;
      }

      matchContainer.innerHTML = "";
      if (matchingSkills.length > 0) {
        matchingSkills.forEach(s => {
          const t = document.createElement("span");
          t.className = "pill-tag pill-tag-matched";
          t.textContent = s;
          matchContainer.appendChild(t);
        });
      } else {
        matchContainer.innerHTML = "<span style='font-size:0.85rem;color:#6b7280;'>No direct skill matches found.</span>";
      }

      missContainer.innerHTML = "";
      if (missingSkills.length > 0) {
        missingSkills.forEach(s => {
          const t = document.createElement("span");
          t.className = "pill-tag pill-tag-missing";
          t.textContent = s;
          missContainer.appendChild(t);
        });
      } else {
        missContainer.innerHTML = "<span style='font-size:0.85rem;color:#166534;font-weight:700;'>No missing skills detected!</span>";
      }

      if (resultsBlock) resultsBlock.classList.remove("d-none");
      showAlert("Skill analysis complete! Match score: " + res.score + "%", true);
    } else {
      scoreVal.textContent = "0%";
      if (resultsBlock) resultsBlock.classList.add("d-none");
      showAlert("Job description is empty. General interview questions will be generated from your resume.", true);
    }
  } catch (err) {
    showAlert(err.message || "Failed to analyze skills.");
  }
}

// ----------------- Launch Dedicated Interview Page Instantly -----------------
function launchInterviewRoom() {
  hideAlert();
  if (!resumeText) {
    showAlert("Please upload or load a resume before entering CRUCIBLE.");
    return;
  }

  const btn = document.getElementById("startInterviewBtn");
  btn.disabled = true;
  btn.innerHTML = `Launching Interview...`;

  const jd = document.getElementById("jdInput") ? document.getElementById("jdInput").value.trim() : "";
  const targetRole = document.getElementById("targetRoleInput") ? document.getElementById("targetRoleInput").value.trim() : "";

  localStorage.setItem("interview_resume_text", resumeText || "");
  localStorage.setItem("interview_matching_skills", JSON.stringify(matchingSkills || []));
  localStorage.setItem("interview_missing_skills", JSON.stringify(missingSkills || []));
  localStorage.setItem("interview_target_role", targetRole || "");
  localStorage.setItem("interview_job_description", jd || "");

  // Instant navigation with ZERO network blocking
  window.location.href = "/interview";
}
