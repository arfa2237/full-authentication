# TIG - Trace and Immunize Gujranwala

A web application that digitizes child vaccination management in Gujranwala, Pakistan. It replaces paper registers with online appointment booking, digital vaccination records, and automatic email reminders, so children don't miss their doses.

🌐 **Live website:** https://tig-gujranwala.com

> Final Year Project, BSIT 2022–2026, Govt. Graduate College for Women, Gujranwala
> **Team:** Arfa Imran, Zartab, Uqba Nisar | **Team Leader:** Arfa Imran

---

## The Problem

- Vaccination records are kept on paper and are easily lost.
- There is no appointment system, which means long queues.
- Parents forget doses because there are no reminders.
- Health authorities have no easy way to see vaccination coverage.

## The Solution

TIG gives patients, healthcare staff, and administrators one platform to book, manage, and track vaccinations. It follows Pakistan's EPI schedule (6 vaccination visits: At Birth, 6 weeks, 10 weeks, 14 weeks, 9 months, 15 months).

---

## Features

**Patients**
- Register and log in, with a unique PIN generated for each patient (e.g. `TIG-4829-GRW`)
- 3 step appointment booking (vaccine, child details, date and time)
- View and cancel appointments
- Digital vaccine card, downloadable as PDF
- Personal records dashboard with a status chart
- Password reset by email (link expires in 10 minutes)

**Healthcare Staff**
- Confirm pending appointments
- Mark appointments as completed
- Patients are emailed automatically at each step

**Administrators**
- Approve or reject staff registrations
- Manage vaccination centers (add, activate, deactivate)
- Set default opening and closing hours for each center
- Calendar-based schedule: mark holidays or set custom hours for any date
- View all patients and appointments
- Statistics dashboard

**Public Website**
- Vaccine information, health blogs, and FAQs
- Interactive map of vaccination centers
- AI chatbot for vaccination questions
- English / Urdu language switch and dark mode

**Automatic Emails**
- Appointment confirmed
- Appointment completed, with the next dose details
- Reminder about 30 minutes before the appointment
- Password reset

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Django, Python |
| Database | PostgreSQL (production), SQLite3 (development) |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Charts and maps | Chart.js, Leaflet.js |
| PDF | ReportLab |
| Email | SendGrid API (production), Gmail SMTP (local) |
| Hosting | Railway, Gunicorn, WhiteNoise |
| Scheduling | Railway Cron Job (`send_reminders` command) |

---

## Project Structure

```
full-authentication/
├── AuthenticationProject/   # Settings and main URLs
├── Core/                    # Patient side, models, reminders command
├── Staff/                   # Healthcare staff portal
├── AdminPanel/              # Admin panel
├── publicsite/              # Public-facing website
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── locale/                  # Urdu translations
```

--- 
