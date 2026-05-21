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

// ===== DROPDOWN NAVIGATION =====
const dropdownToggles = document.querySelectorAll('.nav-dropdown-toggle');

dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        
        const dropdownItem = toggle.closest('.nav-dropdown');
        
        // Close other dropdowns
        document.querySelectorAll('.nav-dropdown.active').forEach(item => {
            if (item !== dropdownItem) {
                item.classList.remove('active');
            }
        });
        
        // Toggle current dropdown
        dropdownItem.classList.toggle('active');
    });
});

// Close dropdown when clicking on a link
const dropdownLinks = document.querySelectorAll('.nav-dropdown-menu a');

dropdownLinks.forEach(link => {
    link.addEventListener('click', () => {
        link.closest('.nav-dropdown').classList.remove('active');
        
        // Close mobile menu too
        if (window.innerWidth <= 768) {
            document.querySelector('.nav-menu').classList.remove('active');
        }
    });
});

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-dropdown')) {
        document.querySelectorAll('.nav-dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    }
});
