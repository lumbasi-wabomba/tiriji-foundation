# Tiriji Foundation Platform

Tiriji Foundation is a Django-based digital platform for a regenerative NGO operating in Kenya. It presents the foundation as a living movement and operational ecosystem for children, women, volunteers, donors, partners, and local communities.

The current product direction combines cinematic storytelling, impact transparency, premium SaaS-style operational clarity, and accessible community engagement flows.

## Current Scope

### Public Website

- Cinematic homepage with hero slideshow, impact counters, storytelling sections, transparent donation allocation, community gallery, partner rail, and calls to action.
- Children page focused on education support, mentorship timelines, student stories, and child-centered impact metrics.
- Women empowerment page focused on vocational training, entrepreneurship, leadership journeys, workshop systems, and transformation stories.
- Programs listing and detail pages with search, active program cards, volunteer fee visibility, and calls to donate or volunteer.
- Blog and field-note pages for long-form editorial updates and published stories.
- Resources dropdown for Events, News, and Materials.
- About page with mission, vision, values, team profiles, and compact partner logo cards.
- Contact, gallery, team, partners, careers, blog, FAQ, and supporting content routes.

### Volunteer Experience

- Volunteer landing page with program selection, duration estimator, fee preview, and status pipeline.
- Volunteer application form.
- Application flow creates:
  - volunteer record
  - calculated fee
  - pending transaction
  - volunteer payment record
- Payment summary page for the submitted volunteer.

### Donation Experience

- Impact-based donation tiers.
- Donation form with donation type, payment method, amount, reason, and monthly sponsorship option.
- Donation submission creates:
  - transaction record
  - donation record
  - generated donation ID
  - generated merchant reference ID
- Success page after submission.

### Admin Portal

The custom admin portal is available at:

```text
/admin-portal/
```

It is protected by login and supports operational content management for:

- Programs
- Events
- News
- Blog posts
- Success stories
- Resources
- Volunteers
- Donations and finance review
- Feedback
- Admin users and role assignment

The dashboard has been restyled as an operations command center with workflow panels, metrics, quick publishing actions, finance review, and management links. Admin pages run as a separate portal shell without public site navigation or footer links. If an authenticated admin user leaves `/admin-portal/` for a public page, the session is automatically logged out.

Admin roles are powered by Django groups:

- `sys_admin`: user and role management plus full portal access
- `manager`: full operational access
- `content_manager`: programs, news, and resources
- `events_resources_manager`: events, programs, news, and resources
- `volunteer_manager`: volunteer applications and review workflow
- `finance_manager`: donation and payment review

## Tech Stack

- Python
- Django 6.0
- PostgreSQL via `DATABASE_URL`
- Cloudinary for uploaded media processing/storage integration
- WhiteNoise for static file serving
- Django REST Framework
- django-crispy-forms and crispy-bootstrap5
- Custom HTML/CSS/JavaScript frontend

## Key Files

```text
core/models.py              Data models and media upload hooks
core/forms.py               Public and admin forms
core/views.py               Public pages, submissions, and admin portal views
core/urls.py                Application routes
templates/core/             Public and admin templates
templates/registration/     Login template
static/css/style.css        Main design system and responsive UI styles
static/js/script.js         Navigation, dropdowns, counters, reveals, estimators, filters
static/images/              Local image and partner logo assets
staticfiles/                Collected static output used by WhiteNoise/dev serving
```

## Environment Variables

Create a `.env` file in the project root with the values required by `tiriji/settings.py`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@host:5432/database?sslmode=require
FIELD_ENCRYPTION_KEY=your-fernet-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Generate a local `FIELD_ENCRYPTION_KEY` with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

The project expects PostgreSQL from `DATABASE_URL`. Make sure it points to a reachable local or hosted database before starting Django. If the host is unavailable, the server will not boot and data-backed views will fail.

## Local Setup

The helper script can install dependencies, check the local environment, run migrations, collect static files, and start the Django server:

```bash
./build.sh help
./build.sh install
./build.sh check
./build.sh migrate
./build.sh runserver
```

For a full local flow:

```bash
./build.sh local
```

To run on another port:

```bash
./build.sh runserver 127.0.0.1:8001
```

For deployment-oriented validation without changing data:

```bash
./build.sh deploy-check
```

Manual setup is still available:

1. Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env` with the variables above.

4. Seed demo content if you want the site populated with sample programs, stories, and editorial content:

```bash
python manage.py seed_demo
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

If port `8000` is busy, use another port:

```bash
python manage.py runserver 127.0.0.1:8001
```

## Static Assets

Source assets live in:

```text
static/
```

The app also has a collected static directory:

```text
staticfiles/
```

When editing CSS or JavaScript locally, update the source files:

```text
static/css/style.css
static/js/script.js
```

If the running server is serving stale assets from `staticfiles/`, either run `collectstatic` or sync the changed files into `staticfiles/` during local development.

## Verification

Useful checks:

```bash
python manage.py check
python manage.py runserver 127.0.0.1:8001
```

Important routes to test:

```text
/
/about/
/children/
/women/
/programs/
/volunteer/
/volunteer/signup/
/donate/
/events/
/news/
/resources/
/admin-portal/
/admin-portal/users/
/admin-portal/donations/
```

Submission flows to verify after backend changes:

- Donation submit redirects to `/donate/success/`.
- Volunteer submit redirects to `/volunteer/payment/<email>/volunteer_payment_summary/`.
- Existing volunteer payment summaries render without server errors.

## Recent Platform Updates

- Rebuilt the frontend design system for a modern regenerative NGO platform.
- Added route-aware active navigation states.
- Restyled Resources dropdown and compact About partner cards.
- Rebuilt shared JavaScript for navigation, dropdowns, scroll reveals, counters, donation tiers, volunteer fee estimation, and program search.
- Fixed donation submission by generating donation and merchant reference IDs.
- Fixed volunteer payment summary model lookup and payment status rendering.
- Fixed broken partner image path on the About page.
- Added admin portal isolation, role-based staff users, finance review, and automatic admin logout when leaving the portal.
- Added blog post publishing and story management to the custom admin portal.
- Added seeded demo content for blog posts, stories, and expanded program pages.

## Notes

- The custom admin portal is separate from Django's built-in `/admin/`.
- Uploaded media is configured around Cloudinary support.
- The visual system is intentionally not a generic charity template; it is designed to communicate active operations, trust, transparency, and human-centered impact.
