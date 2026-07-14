// script.js

const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

menuBtn.addEventListener("click", () => {
    navLinks.classList.toggle("active");
});

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
