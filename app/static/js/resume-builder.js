
(() => {
  "use strict";

  const initialElement = document.getElementById("initial-resume");
  if (!initialElement) {
    console.error("Resume builder: initial resume data was not found.");
    return;
  }

  let initial;
  try {
    initial = JSON.parse(initialElement.textContent || "{}");
  } catch (error) {
    console.error("Could not parse initial resume data:", error);
    return;
  }

  // Load resume data imported from an uploaded PDF, if available.
  let importedResume = null;

  try {
    const saved = sessionStorage.getItem("importedResumeData");
    if (saved) {
      importedResume = JSON.parse(saved);
      sessionStorage.removeItem("importedResumeData");
    }
  } catch (error) {
    console.error("Could not read imported resume:", error);
  }

  function normalizeImportedResume(data) {
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      return null;
    }

    const personal = data.personal || {};

    return {
      personal: {
        full_name: personal.full_name ?? data.full_name ?? "",
        job_title: personal.job_title ?? data.job_title ?? "",
        email: personal.email ?? data.email ?? "",
        phone: personal.phone ?? data.phone ?? "",
        location: personal.location ?? data.location ?? "",
        website: personal.website ?? data.website ?? "",
        linkedin: personal.linkedin ?? data.linkedin ?? "",
        summary: personal.summary ?? data.summary ?? ""
      },
      education: Array.isArray(data.education) ? data.education : [],
      experience: Array.isArray(data.experience) ? data.experience : [],
      projects: Array.isArray(data.projects) ? data.projects : [],
      certifications: Array.isArray(data.certifications)
        ? data.certifications.map(item =>
          typeof item === "string"
            ? { name: item, issuer: "", date: "" }
            : item
        )
        : [],
      skills: Array.isArray(data.skills) ? data.skills : [],
      languages: Array.isArray(data.languages) ? data.languages : [],
      achievements: Array.isArray(data.achievements) ? data.achievements : [],
      custom_sections: Array.isArray(data.custom_sections)
        ? data.custom_sections
        : []
    };
  }

  const resume = structuredClone(
    normalizeImportedResume(importedResume) || initial
  );

  // Ensure every expected section exists.
  resume.personal ||= {};
  resume.education ||= [];
  resume.experience ||= [];
  resume.projects ||= [];
  resume.certifications ||= [];
  resume.skills ||= [];
  resume.languages ||= [];
  resume.achievements ||= [];
  resume.custom_sections ||= [];

  const templateId = document.body.dataset.templateId || "classic";
  const form = document.getElementById("resume-form");
  const preview = document.getElementById("resume-preview");
  const stage = document.querySelector(".preview-stage");
  const status = document.getElementById("save-status");
  const previewState = document.getElementById("preview-state");
  const errorBox = document.getElementById("form-error");
  const steps = [...document.querySelectorAll(".wizard-step")];
  const nextButton = document.getElementById("next-button");
  const backButton = document.getElementById("back-button");
  const progressBar = document.getElementById("progress-bar");
  const progressPercent = document.getElementById("progress-percent");
  const stepLabel = document.getElementById("step-label");
  const stepDots = [...document.querySelectorAll("#step-dots span")];
  const printButton = document.getElementById("print-button");

  if (
    !form ||
    !preview ||
    !status ||
    !previewState ||
    !errorBox ||
    !nextButton ||
    !backButton ||
    !progressBar ||
    !progressPercent ||
    !stepLabel ||
    !printButton ||
    steps.length === 0
  ) {
    console.error("Resume builder: one or more required HTML elements are missing.");
    return;
  }

  let currentStep = 0;
  let previewTimer;
  let previewRequest = 0;

  const definitions = {
    education: [
      ["institution", "Institution", "input", "wide", "e.g. University name"],
      ["degree", "Degree", "input", "", "e.g. B.Tech"],
      ["field_of_study", "Field of study", "input", "", "e.g. Computer Science"],
      ["start_date", "Start date", "input", "", "2023"],
      ["end_date", "End date", "input", "", "2027 or Present"],
      ["grade", "Grade / GPA", "input", "", "Optional"],
      ["description", "Details", "textarea", "wide", "Relevant coursework, honors, or details"]
    ],

    experience: [
      ["position", "Position", "input", "wide", "e.g. Software Intern"],
      ["company", "Company", "input", "", "Company name"],
      ["location", "Location", "input", "", "City or Remote"],
      ["start_date", "Start date", "input", "", "Jun 2025"],
      ["end_date", "End date", "input", "", "Present"],
      ["description", "Responsibilities and impact", "textarea", "wide", "Describe your work and achievements"]
    ],

    projects: [
      ["name", "Project name", "input", "wide", "Project title"],
      ["technologies", "Technologies", "input", "wide", "Python, FastAPI, HTML..."],
      ["link", "Project link", "input", "wide", "https://... (optional)"],
      ["description", "Description", "textarea", "wide", "What did you build or improve?"]
    ],

    certifications: [
      ["name", "Certification", "input", "wide", "Certification name"],
      ["issuer", "Issuer", "input", "", "Organization"],
      ["date", "Date", "input", "", "Year or date"]
    ],

    custom_sections: [
      ["title", "Section title", "input", "wide", "e.g. Volunteering"],
      ["content", "Content", "textarea", "wide", "Add any extra information"]
    ]
  };

  function makeId() {
    return window.crypto?.randomUUID
      ? window.crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  const blank = {
    education: () => ({
      id: makeId(),
      institution: "",
      degree: "",
      field_of_study: "",
      start_date: "",
      end_date: "",
      grade: "",
      description: ""
    }),

    experience: () => ({
      id: makeId(),
      company: "",
      position: "",
      location: "",
      start_date: "",
      end_date: "",
      description: ""
    }),

    projects: () => ({
      id: makeId(),
      name: "",
      technologies: "",
      link: "",
      description: ""
    }),

    certifications: () => ({
      id: makeId(),
      name: "",
      issuer: "",
      date: ""
    }),

    custom_sections: () => ({
      id: makeId(),
      title: "",
      content: ""
    })
  };

  function normalizeRepeatableItems(section) {
    if (!Array.isArray(resume[section])) {
      resume[section] = [];
    }

    resume[section] = resume[section].map(item => {
      const normalized = {
        ...blank[section](),
        ...(item || {})
      };

      if (section === "projects" && Array.isArray(normalized.technologies)) {
        normalized.technologies = normalized.technologies.join(", ");
      }

      return normalized;
    });
  }

  Object.keys(definitions).forEach(normalizeRepeatableItems);

  function setPath(object, path, value) {
    const keys = path.split(".");
    let node = object;

    while (keys.length > 1) {
      const key = keys.shift();

      if (!node[key] || typeof node[key] !== "object") {
        node[key] = {};
      }

      node = node[key];
    }

    node[keys[0]] = value;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll("'", "&#39;");
  }

  function renderRepeatable(section) {
    const list = document.getElementById(`${section}-list`);
    if (!list) return;

    list.replaceChildren();

    resume[section].forEach((item, index) => {
      const card = document.createElement("article");
      card.className = "repeat-card";

      const title = section === "custom_sections"
        ? "Custom section"
        : {
          education: "Education",
          experience: "Experience",
          projects: "Project",
          certifications: "Certification"
        }[section];

      const fields = definitions[section]
        .map(([key, label, type, wide, placeholder]) => {
          const value = escapeHtml(item[key] || "");

          const control = type === "textarea"
            ? `<textarea data-repeat-section="${section}" data-item-id="${escapeHtml(item.id)}" data-key="${key}" rows="3" maxlength="6000" placeholder="${escapeHtml(placeholder)}">${value}</textarea>`
            : `<input data-repeat-section="${section}" data-item-id="${escapeHtml(item.id)}" data-key="${key}" maxlength="500" value="${value}" placeholder="${escapeHtml(placeholder)}">`;

          return `<label class="${wide}">${label}${control}</label>`;
        })
        .join("");

      card.innerHTML = `
        <div class="repeat-card-head">
          <strong>${title} ${index + 1}</strong>
          <button
            class="remove-entry"
            type="button"
            data-remove="${section}"
            data-item-id="${escapeHtml(item.id)}"
          >Remove</button>
        </div>
        <div class="repeat-fields">${fields}</div>
      `;

      list.appendChild(card);
    });
  }

  function renderAllRepeatables() {
    Object.keys(definitions).forEach(renderRepeatable);
  }

  function populateImportedFields() {
    // Populate personal details and any other scalar fields.
    form.querySelectorAll("[data-path]").forEach(input => {
      const value = input.dataset.path
        .split(".")
        .reduce((object, key) => object?.[key], resume);

      input.value = value ?? "";
    });

    // Populate comma-separated fields.
    const commaSeparatedFields = {
      "skills-input": resume.skills,
      "languages-input": resume.languages,
      "achievements-input": resume.achievements
    };

    Object.entries(commaSeparatedFields).forEach(([id, values]) => {
      const input = document.getElementById(id);

      if (input) {
        input.value = Array.isArray(values) ? values.join(", ") : "";
      }
    });

    // Populate education, experience, projects, certifications and custom sections.
    renderAllRepeatables();
  }

  function updateProgress() {
    const percentage = Math.round(
      ((currentStep + 1) / steps.length) * 100
    );

    stepLabel.textContent = `Step ${currentStep + 1} of ${steps.length}`;
    progressPercent.textContent = `${percentage}%`;
    progressBar.style.width = `${percentage}%`;

    stepDots.forEach((dot, index) => {
      dot.classList.toggle("active", index <= currentStep);
    });

    backButton.disabled = currentStep === 0;

    nextButton.textContent = currentStep === steps.length - 1
      ? "Finish & review ✓"
      : "Next step →";
  }

  function showStep(index) {
    currentStep = Math.max(0, Math.min(index, steps.length - 1));

    steps.forEach((step, index) => {
      const isCurrent = index === currentStep;
      step.hidden = !isCurrent;
      step.classList.toggle("active", isCurrent);
    });

    errorBox.textContent = "";
    updateProgress();

    if (window.matchMedia("(max-width: 760px)").matches) {
      document.querySelector(".form-panel")?.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  }

  async function refreshPreview() {
    const requestId = ++previewRequest;

    status.textContent = "Updating preview…";
    previewState.textContent = "Updating";

    try {
      const response = await fetch("/api/resume-preview", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          template_id: templateId,
          resume
        })
      });

      if (!response.ok) {
        throw new Error(`Preview request failed (${response.status})`);
      }

      const html = await response.text();

      if (requestId !== previewRequest) return;

      preview.innerHTML = html;
      status.textContent = "Preview updated";
      previewState.textContent = "Live";

      updatePreviewScale();
    } catch (error) {
      console.error("Resume preview error:", error);
      status.textContent = "Preview error";
      previewState.textContent = "Could not update";
    }
  }

  function schedulePreview() {
    clearTimeout(previewTimer);
    status.textContent = "Changes detected…";
    previewTimer = setTimeout(refreshPreview, 180);
  }


  function updatePreviewScale() {
    if (!stage || !preview) return;
    if (window.matchMedia("print").matches) return;

    const availableWidth = Math.max(1, stage.clientWidth - 16);
    const pageWidth = 794;

    const scale = Math.min(1, availableWidth / pageWidth);

    preview.style.transformOrigin = "top center";
    preview.style.transform = `scale(${scale})`;

    // Do not set stage height from the resume's content.
    // The preview panel now owns its height and scroll behavior.
  }


  // Update resume data when form fields change.
  form.addEventListener("input", event => {
    const target = event.target;

    if (target.dataset.path) {
      setPath(resume, target.dataset.path, target.value);
      schedulePreview();
      return;
    }

    if (target.dataset.repeatSection) {
      const section = target.dataset.repeatSection;
      const item = resume[section]?.find(
        entry => entry.id === target.dataset.itemId
      );

      if (item) {
        item[target.dataset.key] = target.value;
        schedulePreview();
      }

      return;
    }

    const listFields = {
      "skills-input": "skills",
      "languages-input": "languages",
      "achievements-input": "achievements"
    };

    const fieldName = listFields[target.id];

    if (fieldName) {
      resume[fieldName] = target.value
        .split(",")
        .map(value => value.trim())
        .filter(Boolean);

      schedulePreview();
    }
  });

  // Add and remove repeatable entries.
  document.addEventListener("click", event => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const addButton = target.closest("[data-add]");

    if (addButton) {
      const section = addButton.dataset.add;

      if (!blank[section] || !Array.isArray(resume[section])) return;

      if (resume[section].length >= 30) {
        errorBox.textContent =
          "This section has reached the current item limit.";
        return;
      }

      resume[section].push(blank[section]());
      renderRepeatable(section);
      schedulePreview();
      return;
    }

    const removeButton = target.closest("[data-remove]");

    if (removeButton) {
      const section = removeButton.dataset.remove;

      if (!Array.isArray(resume[section])) return;

      const itemId = removeButton.dataset.itemId;

      // Remove only the selected item.
      const index = resume[section].findIndex(
        item => item.id === itemId
      );

      if (index === -1) return;

      resume[section].splice(index, 1);

      // Re-render only this section.
      renderRepeatable(section);

      // Refresh the preview after the deletion.
      schedulePreview();
    }
  });

  nextButton.addEventListener("click", () => {
    if (currentStep === 0) {
      const name = String(resume.personal.full_name || "").trim();

      if (!name) {
        errorBox.textContent =
          "Please enter your full name to continue.";

        form.querySelector('[data-path="personal.full_name"]')?.focus();
        return;
      }
    }

    if (currentStep < steps.length - 1) {
      showStep(currentStep + 1);
    } else {
      errorBox.textContent =
        "Your resume is ready to review. Use Print / Save PDF to export it, or go back to make changes.";

      errorBox.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
      });
    }
  });

  backButton.addEventListener("click", () => {
    showStep(currentStep - 1);
  });

  printButton.addEventListener("click", () => {
    window.print();
  });

  window.addEventListener("resize", updatePreviewScale);


  // AI writing assistant: improve the professional summary.
  const improveSummaryButton = document.getElementById("ai-improve-summary");
  const aiAssistantStatus = document.getElementById("ai-assistant-status");

  if (improveSummaryButton && aiAssistantStatus) {
    improveSummaryButton.addEventListener("click", async () => {
      const summaryInput = form.querySelector(
        '[data-path="personal.summary"]'
      );

      const summary = summaryInput?.value.trim();

      if (!summary) {
        aiAssistantStatus.textContent =
          "Write a summary first so AI can improve it.";
        return;
      }

      improveSummaryButton.disabled = true;
      improveSummaryButton.textContent = "Improving…";
      aiAssistantStatus.textContent = "AI is reviewing your summary.";

      try {
        const response = await fetch("/api/ai/assist", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            task: "improve_summary",
            text: summary,
            job_description: ""
          })
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            result.detail || "AI could not improve the summary."
          );
        }

        if (!result.result || typeof result.result !== "string") {
          throw new Error("AI returned an invalid response.");
        }

        // Update both the visible field and the builder's resume data.
        summaryInput.value = result.result;
        setPath(resume, "personal.summary", result.result);

        // Refresh the resume preview.
        schedulePreview();

        aiAssistantStatus.textContent =
          "Summary improved. Review it before using it.";
      } catch (error) {
        console.error("AI summary improvement failed:", error);
        aiAssistantStatus.textContent =
          error.message || "AI request failed. Please try again.";
      } finally {
        improveSummaryButton.disabled = false;
        improveSummaryButton.textContent = "✨ Improve with AI";
      }
    });
  }


  const companyGuidanceBanner = document.getElementById("company-guidance-banner");
  const companyGuidanceTitle = document.getElementById("company-guidance-title");
  const companyGuidanceDescription = document.getElementById("company-guidance-description");
  const dismissCompanyGuidance = document.getElementById("dismiss-company-guidance");

  if (companyGuidanceBanner) {
    try {
      const raw = sessionStorage.getItem("companyResumeGuidance");
      const guidance = raw ? JSON.parse(raw) : null;

      if (
        guidance &&
        typeof guidance.company === "string" &&
        typeof guidance.role === "string"
      ) {
        companyGuidanceTitle.textContent =
          `Resume target: ${guidance.company} · ${guidance.role}`;

        companyGuidanceDescription.textContent = guidance.analysis
          ? "Job analysis is available. Review the requirements and use them to tailor your resume honestly."
          : "Use the selected role as your target while editing your resume.";

        companyGuidanceBanner.hidden = false;

        // Prefill the target job title only when the current field is blank.
        // Never overwrite an existing user-entered title.
        const jobTitleInput = document.querySelector(
          '[data-path="personal.job_title"]'
        );

        if (
          jobTitleInput &&
          !jobTitleInput.value.trim() &&
          typeof setPath === "function" &&
          typeof resume === "object"
        ) {
          jobTitleInput.value = guidance.role;
          setPath(resume, "personal.job_title", guidance.role);
        }
      }
    } catch (error) {
      console.warn("Company guidance could not be loaded.", error);
    }
  }

  dismissCompanyGuidance?.addEventListener("click", () => {
    companyGuidanceBanner.hidden = true;
  });


  // Initialize the builder once.
  populateImportedFields();
  showStep(0);
  refreshPreview();
})();
