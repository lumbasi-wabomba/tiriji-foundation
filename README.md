# Tiriji Foundation

Tiriji Foundation is a web platform designed to showcase the programs, events, news, resources, and team behind the foundation. The platform serves as a central hub for community engagement, volunteer signups, donations, and access to educational and vocational resources.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Current Progress](#current-progress)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About

Tiriji Foundation aims to provide a digital presence for initiatives, programs, and events that empower communities. The platform emphasizes accessibility, intuitive design, and informative content to connect supporters, volunteers, and beneficiaries.

## Features

The platform includes:

- **Programs** — Showcase of foundation programs with detail pages, galleries, and suggested programs
- **Events** — List of events with detail views and related events suggestions
- **News** — News grid and detailed news articles to keep visitors informed
- **Resources** — Educational and vocational resources with detail pages
- **Team & Partners** — Profiles of team members and partner organizations
- **Volunteer Sign-up** — Forms to register volunteers
- **Donations** — Structured donation options to support the foundation
- **Contact** — Contact forms and social media links
- **Responsive UI** — Mobile-friendly design with consistent styling across sections

## Current Progress

Based on the current GitHub repository (Tiriji Foundation):

### Frontend
- Fully styled pages using `style.css`
- Responsive grid layouts for programs, events, news, resources, and partners
- Interactive call-to-action buttons (`.btn-primary`, `.btn-secondary`, `.btn-outline`)
- Hover effects for cards and buttons for enhanced UX
- Dedicated sections for volunteer signup, donations, and suggested programs/resources

### Backend (Django)
- Models for Programs, Events, News, Resources, Team Members, and Partners
- Admin interface for content management (assumed from earlier work)
- Dynamic rendering of program/event/news details using templates

### Pending / Next Steps
- Integration of dynamic image uploads and media handling for program/event galleries
- Full deployment setup and hosting configuration
- SEO optimizations and accessibility enhancements

## Tech Stack

- **Frontend**: HTML, CSS (custom grid and responsive layout), JavaScript (planned enhancements)
- **Backend**: Django, Python
- **Database**: SQLite (development), PostgreSQL (planned for production)
- **Version Control**: Git, GitHub

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/tiriji-foundation.git
   cd tiriji-foundation

2. **Create a virtual environment**
   ```bash
   python3 -m venv env
   source env/bin/activate          # On Windows: env\Scripts\activate
3. **Install Dependancies**
    ```bash
    pip install -r requirements.txt
4. **Run Migrations**
    ```bash
    python manage.py migrate
5. **Start the development server**
    ```bash
    python manage.py runserver
6. **Open your browser at http://127.0.0.1:8000/**

## Usage

- Access programs, events, and resources via the navigation menu.  
- Submit volunteer applications or donations through the provided forms.  
- Administrators can log in via `staff login` at the footer of the resource page to manage content .  

## Contributing

1. Fork the repository.  
2. Create a feature branch:
    ```bash
    git checkout -b feature/new-feature
3. Commit changes:
    ```bash
    git commit -m "This is an eaxmple feature"
4. Push to your branch:
    ```bash
    git push origin feature/new-feature
5. Submit a pull request



## Contact

- **Website:** [Tiriji Foundation](https://www.tirijifoundation.com/)  
- **GitHub:** [Raibn](https://github.com/Raibn)  
- **Email:** [contact@tiriji-foundation.org](mailto:brayokara@gmail.com)
