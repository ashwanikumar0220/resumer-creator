
(() => {
    "use strict";

    const uploadForm = document.getElementById("upload-form");
    const pdfInput = document.getElementById("pdf-input");
    const uploadButton = document.getElementById("upload-button");
    const fileName = document.getElementById("file-name");
    const message = document.getElementById("upload-message");

    if (!uploadForm || !pdfInput || !uploadButton || !message) {
        console.error("Resume import page is missing required elements.");
        return;
    }

    function showMessage(text, type = "") {
        message.textContent = text;
        message.className = "form-message";

        if (type) {
            message.classList.add(type);
        }
    }

    pdfInput.addEventListener("change", () => {
        const file = pdfInput.files?.[0];

        fileName.textContent = file
            ? file.name
            : "Choose your PDF resume";

        showMessage("");
    });

    uploadForm.addEventListener("submit", async event => {
        event.preventDefault();

        const file = pdfInput.files?.[0];

        if (!file) {
            showMessage("Please select a PDF file.", "error");
            return;
        }

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            showMessage("Please select a PDF file.", "error");
            return;
        }

        if (file.size === 0) {
            showMessage("The selected file is empty.", "error");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showMessage("The PDF must be 10 MB or smaller.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadButton.disabled = true;
        uploadButton.textContent = "Processing resume…";
        showMessage("Extracting your resume information. Please wait.");

        try {
            const response = await fetch("/upload-resume", {
                method: "POST",
                body: formData
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    result.detail ||
                    result.message ||
                    "Resume upload failed."
                );
            }

            if (!result.resume_data ||
                typeof result.resume_data !== "object") {
                throw new Error(
                    "Resume information could not be extracted. Please try another PDF."
                );
            }

            if (!Array.isArray(result.layout)) {
                throw new Error(
                    "The server did not return valid PDF layout data."
                );
            }

            // Save both values for the existing resume builder.
            // Use the same source value that the builder expects.
            try {
                sessionStorage.setItem(
                    "importedResumeData",
                    JSON.stringify(result.resume_data)
                );

                sessionStorage.setItem(
                    "importedResumeLayout",
                    JSON.stringify(result.layout)
                );

                sessionStorage.setItem(
                    "importedResumeSource",
                    "uploaded"
                );
            } catch (storageError) {
                // Avoid leaving half-written import state behind.
                sessionStorage.removeItem("importedResumeData");
                sessionStorage.removeItem("importedResumeLayout");
                sessionStorage.removeItem("importedResumeSource");

                throw new Error(
                    "The imported resume is too large to store in this browser tab. " +
                    "Try a smaller PDF."
                );
            }

            showMessage("Resume imported. Opening the builder…", "success");

            window.location.assign(
                "/create-resume/build/classic?source=uploaded"
            );
        } catch (error) {
            console.error("Resume import failed:", error);

            showMessage(
                error.message || "Something went wrong while importing your resume.",
                "error"
            );

            uploadButton.disabled = false;
            uploadButton.textContent = "Upload and continue";
        }
    });
})();
