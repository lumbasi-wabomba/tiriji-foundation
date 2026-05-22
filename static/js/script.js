(function () {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function initNavigation() {
        const header = document.querySelector(".site-header");
        const toggle = document.querySelector(".nav-toggle");
        const menu = document.querySelector(".nav-menu");

        if (header) {
            const updateHeader = () => {
                header.classList.toggle("shrink", window.scrollY > 48);
            };

            updateHeader();
            window.addEventListener("scroll", updateHeader, { passive: true });
        }

        if (toggle && menu) {
            toggle.addEventListener("click", () => {
                const isOpen = menu.classList.toggle("active");
                toggle.setAttribute("aria-expanded", String(isOpen));
            });
        }

        document.querySelectorAll(".nav-dropdown-toggle").forEach((button) => {
            button.addEventListener("click", (event) => {
                event.preventDefault();

                const dropdown = button.closest(".nav-dropdown");
                if (!dropdown) return;

                const shouldOpen = !dropdown.classList.contains("active");
                closeDropdowns();
                dropdown.classList.toggle("active", shouldOpen);
                button.setAttribute("aria-expanded", String(shouldOpen));
            });
        });

        document.querySelectorAll(".nav-dropdown-menu a").forEach((link) => {
            link.addEventListener("click", () => {
                closeDropdowns();

                if (menu && window.innerWidth <= 768) {
                    menu.classList.remove("active");
                    if (toggle) toggle.setAttribute("aria-expanded", "false");
                }
            });
        });

        document.addEventListener("click", (event) => {
            if (!event.target.closest(".nav-dropdown")) {
                closeDropdowns();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeDropdowns();
                if (menu && toggle) {
                    menu.classList.remove("active");
                    toggle.setAttribute("aria-expanded", "false");
                }
            }
        });
    }

    function closeDropdowns() {
        document.querySelectorAll(".nav-dropdown.active").forEach((dropdown) => {
            dropdown.classList.remove("active");
            const button = dropdown.querySelector(".nav-dropdown-toggle");
            if (button) button.setAttribute("aria-expanded", "false");
        });
    }

    function initHeroSlider() {
        const slides = Array.from(document.querySelectorAll(".hero-slide"));
        if (slides.length < 2 || prefersReducedMotion) return;

        let currentSlide = Math.max(0, slides.findIndex((slide) => slide.classList.contains("active")));

        window.setInterval(() => {
            slides[currentSlide].classList.remove("active");
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add("active");
        }, 5200);
    }

    function initScrollReveals() {
        const revealItems = document.querySelectorAll(".reveal-on-scroll");

        if (!revealItems.length) return;

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            revealItems.forEach((item) => item.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;

                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
        );

        revealItems.forEach((item) => observer.observe(item));
    }

    function initCounters() {
        const counters = document.querySelectorAll("[data-count]");
        if (!counters.length) return;

        const setFinalValue = (counter) => {
            counter.textContent = `${counter.dataset.count}+`;
        };

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            counters.forEach(setFinalValue);
            return;
        }

        const animateCounter = (counter) => {
            const target = Number(counter.dataset.count);
            if (!Number.isFinite(target)) return;

            const duration = 1100;
            const startTime = performance.now();

            const tick = (now) => {
                const progress = Math.min((now - startTime) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                counter.textContent = `${Math.round(target * eased)}+`;

                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            };

            requestAnimationFrame(tick);
        };

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;

                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.5 }
        );

        counters.forEach((counter) => observer.observe(counter));
    }

    function initVolunteerEstimator() {
        const estimator = document.querySelector("[data-volunteer-estimator]");
        if (!estimator) return;

        const cards = Array.from(estimator.querySelectorAll(".selection-card"));
        const durationInput = document.querySelector("[data-duration-input]");
        const durationOutput = document.querySelector("[data-duration-output]");
        const feeOutput = document.querySelector("[data-fee-output]");
        const selectedProgram = document.querySelector("[data-selected-program]");

        if (!cards.length || !durationInput || !durationOutput || !feeOutput || !selectedProgram) return;

        const getActiveCard = () => estimator.querySelector(".selection-card.active") || cards[0];

        const calculateFee = (base, weeks) => {
            if (weeks <= 2) return base;
            return base + (weeks - 2) * 200;
        };

        const updateEstimate = () => {
            const card = getActiveCard();
            const weeks = Number(durationInput.value);
            const base = Number(card.dataset.rate);
            const fee = calculateFee(base, weeks);

            durationOutput.textContent = `${weeks} week${weeks === 1 ? "" : "s"}`;
            selectedProgram.textContent = card.dataset.program || "Selected Program";
            feeOutput.textContent = `$${fee.toLocaleString()}`;
        };

        cards.forEach((card) => {
            card.addEventListener("click", () => {
                cards.forEach((item) => {
                    item.classList.remove("active");
                    item.setAttribute("aria-pressed", "false");
                });

                card.classList.add("active");
                card.setAttribute("aria-pressed", "true");
                updateEstimate();
            });
        });

        durationInput.addEventListener("input", updateEstimate);
        updateEstimate();
    }

    function initDonationTiers() {
        const tierGroup = document.querySelector("[data-donation-tiers]");
        const amountInput = document.querySelector("[data-donation-amount]");

        if (!tierGroup || !amountInput) return;

        tierGroup.querySelectorAll(".donation-tier").forEach((tier) => {
            tier.addEventListener("click", () => {
                tierGroup.querySelectorAll(".donation-tier").forEach((item) => {
                    item.classList.remove("active");
                    item.setAttribute("aria-pressed", "false");
                });

                tier.classList.add("active");
                tier.setAttribute("aria-pressed", "true");
                amountInput.value = tier.dataset.amount || amountInput.value;
                amountInput.dispatchEvent(new Event("input", { bubbles: true }));
            });
        });
    }

    function initProgramSearch() {
        const searchInput = document.getElementById("programSearch");
        const programCards = document.querySelectorAll(".program-card");

        if (!searchInput || !programCards.length) return;

        searchInput.addEventListener("input", (event) => {
            const query = event.target.value.trim().toLowerCase();

            programCards.forEach((card) => {
                const programName = (card.getAttribute("data-program") || "").toLowerCase();
                card.hidden = query.length > 0 && !programName.includes(query);
            });
        });
    }

    function init() {
        initNavigation();
        initHeroSlider();
        initScrollReveals();
        initCounters();
        initVolunteerEstimator();
        initDonationTiers();
        initProgramSearch();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
