console.log("JS Loaded");

const toggle = document.querySelector('.nav-toggle');
const menu = document.querySelector('.nav-menu');

toggle.addEventListener('click', () => {
    menu.classList.toggle('active');
});

const header = document.querySelector('.site-header');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.classList.add('shrink');
    } else {
        header.classList.remove('shrink');
    }
});

const hero = document.querySelector('.hero');

if (hero) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    header.classList.add('hidden-nav');
                } else {
                    header.classList.remove('hidden-nav');
                }
            });
        },
        { threshold: 0.1 }
    );
    observer.observe(hero);
}
//Additional JS for hero slider

const slides = document.querySelectorAll('.hero-slide');
let currentSlide = 0;

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
    });
}

if (slides.length > 0) {
    setInterval(() => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }, 5000);
} 