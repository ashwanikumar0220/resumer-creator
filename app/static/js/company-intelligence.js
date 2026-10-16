
"use strict";

(() => {
    const $ = (selector) => document.querySelector(selector);

    const chips = $("#company-chips");
    const searchForm = $("#company-search-form");
    const searchInput = $("#company-search");
    const searchResults = $("#search-results");
    const companyName = $("#company-name");
    const companyDescription = $("#company-description");
    const companySymbol = $("#company-symbol");
    const careerLink = $("#career-link");
    const roleSelect = $("#target-role");
    const skillsBox = $("#company-skills");
    const languagesBox = $("#company-languages");
    const tipsBox = $("#company-tips");
    const jobDescription = $("#job-description");
    const analyzeButton = $("#analyze-job");
    const analysisStatus = $("#analysis-status");
    const analysisResults = $("#analysis-results");
    const useResumeButton = $("#use-for-resume");
    const applyAnalysisButton = $("#apply-analysis");

    let selectedCompany = null;
    let latestAnalysis = null;

    function safeText(value) {
        return String(value ?? "");
    }

    function renderTags(container, values) {
        container.replaceChildren();

        const items = Array.isArray(values) ? values : [];

        if (!items.length) {
            const empty = document.createElement("span");
            empty.className = "ci-tag empty";
            empty.textContent = "No information available";
            container.appendChild(empty);
            return;
        }

        items.forEach((value) => {
            const tag = document.createElement("span");
            tag.className = "ci-tag";
            tag.textContent = safeText(value);
            container.appendChild(tag);
        });
    }

    function renderList(container, values) {
        container.replaceChildren();

        (Array.isArray(values) ? values : []).forEach((value) => {
            const li = document.createElement("li");
            li.textContent = safeText(value);
            container.appendChild(li);
        });
    }

    async function requestJSON(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                Accept: "application/json",
                ...(options.headers || {})
            }
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "The request failed. Please try again.");
        }

        return data;
    }

    function setSelectedChip(name) {
        chips.querySelectorAll("button[data-company]").forEach((button) => {
            const selected = button.dataset.company === name;
            button.classList.toggle("selected", selected);
            button.setAttribute("aria-pressed", String(selected));
        });
    }

    async function loadCompany(name) {
        try {
            companyName.textContent = "Loading company...";
            searchResults.hidden = true;

            const data = await requestJSON(
                `/api/companies/${encodeURIComponent(name)}`
            );

            selectedCompany = data.company;
            latestAnalysis = null;
            analysisResults.hidden = true;
            renderCompany(selectedCompany);
            setSelectedChip(selectedCompany.name);
        } catch (error) {
            companyName.textContent = "Company not found";
            companyDescription.textContent = error.message;
        }
    }

    function renderCompany(company) {
        companyName.textContent = company.name;
        companyDescription.textContent = company.description;
        companySymbol.textContent = company.name.slice(0, 1).toUpperCase();

        careerLink.href = company.career_url;
        careerLink.textContent = "Official careers ↗";

        roleSelect.replaceChildren();

        company.roles.forEach((role) => {
            const option = document.createElement("option");
            option.value = role;
            option.textContent = role;
            roleSelect.appendChild(option);
        });

        renderTags(skillsBox, company.skills);
        renderTags(languagesBox, company.languages);
        renderList(tipsBox, company.tips);
    }

    async function searchCompanies(query) {
        const data = await requestJSON(
            `/api/companies?q=${encodeURIComponent(query)}`
        );

        searchResults.replaceChildren();

        if (!data.companies.length) {
            const empty = document.createElement("p");
            empty.textContent =
                "No saved company profile found. Try a different search or paste the actual job description below.";
            searchResults.appendChild(empty);
            searchResults.hidden = false;
            return;
        }

        data.companies.forEach((company) => {
            const button = document.createElement("button");
            button.type = "button";

            const title = document.createElement("strong");
            title.textContent = company.name;

            const detail = document.createElement("span");
            detail.textContent = ` — ${company.description}`;

            button.append(title, detail);
            button.addEventListener("click", () => {
                searchInput.value = company.name;
                loadCompany(company.name);
            });

            searchResults.appendChild(button);
        });

        searchResults.hidden = false;
    }

    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const query = searchInput.value.trim();
        if (!query) {
            searchInput.focus();
            return;
        }

        try {
            await searchCompanies(query);
        } catch (error) {
            searchResults.replaceChildren();
            const message = document.createElement("p");
            message.textContent = error.message;
            searchResults.appendChild(message);
            searchResults.hidden = false;
        }
    });

    chips.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-company]");
        if (button) loadCompany(button.dataset.company);
    });

    document.addEventListener("click", (event) => {
        if (!searchForm.contains(event.target) &&
            !searchResults.contains(event.target)) {
            searchResults.hidden = true;
        }
    });

    function showAnalysis(analysis) {
        $("#analysis-summary").textContent = analysis.role_summary || "";
        renderTags($("#required-skills"), analysis.required_skills);
        renderTags($("#preferred-skills"), analysis.preferred_skills);
        renderTags($("#job-keywords"), analysis.keywords);
        renderList($("#job-tips"), analysis.resume_tips);
        renderList($("#job-unknowns"), analysis.missing_information);

        analysisResults.hidden = false;
        analysisResults.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    analyzeButton.addEventListener("click", async () => {
        if (!selectedCompany) {
            analysisStatus.textContent = "Choose a company first.";
            return;
        }

        const description = jobDescription.value.trim();

        if (description.length < 50) {
            analysisStatus.textContent =
                "Paste a job description with at least 50 characters.";
            jobDescription.focus();
            return;
        }

        analyzeButton.disabled = true;
        analysisStatus.textContent = "Analyzing the job description...";
        analysisResults.hidden = true;

        try {
            const data = await requestJSON("/api/companies/analyze-job", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    company: selectedCompany.name,
                    role: roleSelect.value,
                    job_description: description
                })
            });

            latestAnalysis = data.analysis;
            analysisStatus.textContent =
                "Analysis ready. Review the findings before using them.";
            showAnalysis(latestAnalysis);
        } catch (error) {
            analysisStatus.textContent = error.message;
        } finally {
            analyzeButton.disabled = false;
        }
    });

    function sendToResumeBuilder() {
        if (!selectedCompany) {
            analysisStatus.textContent = "Choose a company first.";
            return;
        }

        const payload = {
            company: selectedCompany.name,
            role: roleSelect.value,
            analysis: latestAnalysis,
            createdAt: new Date().toISOString()
        };

        try {
            sessionStorage.setItem(
                "companyResumeGuidance",
                JSON.stringify(payload)
            );

            // Change this URL only if your current builder uses another route.
            window.location.href = "/create-resume/build/classic?source=company";
        } catch (error) {
            analysisStatus.textContent =
                "Could not save the guidance in this browser session.";
        }
    }

    useResumeButton.addEventListener("click", sendToResumeBuilder);
    applyAnalysisButton.addEventListener("click", sendToResumeBuilder);

    loadCompany("Google");
})();
