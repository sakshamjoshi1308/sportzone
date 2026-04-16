document.addEventListener("DOMContentLoaded", () => {
    const targets = document.querySelectorAll(".product-card, .sport-panel, .metric-card, .data-card");
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    targets.forEach((target, index) => {
        target.style.transition = `opacity 0.5s ease ${index * 0.03}s, transform 0.5s ease ${index * 0.03}s`;
        observer.observe(target);
    });
});
