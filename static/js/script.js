// script.js

const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", () => {
        navLinks.classList.toggle("active");
    });
}

const analyzerRevealItems = document.querySelectorAll(
    ".resume-analyzer .analyzer-heading, .resume-analyzer .analyzer-dashboard, .resume-analyzer .analyzer-score-block, .resume-analyzer .skill-tags, .resume-analyzer .analyzer-suggestions"
);

if ("IntersectionObserver" in window) {
    const analyzerRevealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("analyzer-reveal-visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold:0.15 });

    analyzerRevealItems.forEach((item) => analyzerRevealObserver.observe(item));
} else {
    analyzerRevealItems.forEach((item) => item.classList.add("analyzer-reveal-visible"));
}
const resumeInput = document.getElementById("resume");
const fileUploadArea = document.querySelector(".file-upload-area");
const fileUploadTitle = document.querySelector(".file-upload-title");
const fileUploadNote = document.querySelector(".file-upload-note");

if (
    resumeInput
    && fileUploadArea
    && fileUploadTitle
    && fileUploadNote
) {
    resumeInput.addEventListener("change", () => {
        const selectedFile = resumeInput.files[0];

        if (selectedFile) {
            fileUploadTitle.textContent = selectedFile.name;
            fileUploadNote.textContent =
                "File selected — ready to analyze";

            fileUploadArea.classList.add("file-selected");
        }
    });
}
