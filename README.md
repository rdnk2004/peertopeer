# 🎓 PeerTutor - Peer-to-Peer Micro-Tutoring Marketplace

**PeerTutor** is a Full Stack Django web application built to connect students with verified peer tutors for micro-tutoring sessions. It incorporates role-based authentication, tutor verification workflows, an escrow-style test payment gateway, concurrency protection against double-booking, and mutual ratings/reviews.

---

## 🚀 Key Accomplishments & SRS Compliance (R1 – R26)

All **26 requirements** specified in the Software Requirements Specification (`PeerTutor_SRS.pdf`) have been fully implemented and verified:

### 🔐 1. Authentication & Role-Based Access Control (R1, R2, R3, R22)
- Custom Django `User` model with mandatory roles: `Student`, `Tutor`, `Admin`.
- Secure email authentication with `PBKDF2PasswordHasher` SHA-256 password encryption.
- View authorization & role-tailored dashboard components.

### 📜 2. Tutor Application & Verification Workflow (R4, R5, R6, R7)
- Tutors submit credentials: taught subjects, hourly rate, GitHub profile link, project showcase description, and document marksheet upload.
- Submitted tutor profiles start in `Pending` state.
- Superuser Admin dashboard to review marksheets/GitHub links and **Approve/Reject** applications.
- Unverified tutors are restricted from publishing sessions or listing on search results.

### 🔍 3. Advanced Discovery & Dedicated Tutor Profiles (R8, R9, R19, R24)
- **Multi-Parameter Search Engine**: Filter tutors by subject keywords, maximum hourly rate ($/hr), and minimum star rating (⭐ 4.5+, 4.0+, 3.0+).
- **Dedicated Tutor Profile Page (`tutor_detail.html`)**: View tutor credentials, project showcase, verified marksheet preview, average star rating (`⭐ X.X / 5.0`), total completed sessions count, open time slots, and past student reviews.
- **Database Query Indexing (R24)**: Indexed fields (`hourly_rate`, `status`, `subject`, `is_booked`) to guarantee sub-2.0 second query execution times.

### 💳 4. Test-Mode Payment Gateway & Escrow Safeguards (R11, R12, R13, R14, R26)
- **Isolated Payment Module (`payments.py`)**: Centralized escrow fee calculation, test-mode payment gateway verification, and tutor payout release.
- **Simulated Payment Gateway Checkout (`checkout.html`)**: 2-step checkout accepting test cards (`4242-4242-4242-4242`), logging transaction references (`TXN-ESCROW-...`), and calculating a 10% platform commission.
- **Atomic Double-Booking Guard (R14)**: Uses `@transaction.atomic` and `TimeSlot.objects.select_for_update()` to prevent race conditions during slot bookings.
- **Escrow Hold**: Student payments are held in pending status until the session is marked completed, at which point net funds are released to the tutor.

### ⭐ 5. Mutual Ratings & Reviews System (R16)
- Bidirectional review system allowing **Students to review Tutors** and **Tutors to review Students** after session completion.

### 💻 6. MVT Architecture & Desktop UI Optimization (R23, R25)
- Desktop-first responsive user interface (optimized for ≥1024px screen widths).
- Built strictly following Django's Model-View-Template (MVT) design pattern.

---

## 📊 Status Summary & Next Steps

### ✅ Completed
- [x] All 26 SRS Requirements (R1 to R26) fully implemented.
- [x] Database schema migrations created and applied.
- [x] 100% test pass rate across automated test suite (`python manage.py test core`).
- [x] Demo dataset populated for live faculty presentation.
- [x] Detailed technical documentation & walkthrough artifacts created.

### 📋 Remaining Optional Extensions (If desired by Faculty)
- Live WebSocket / WebRTC video chat link integration for virtual sessions.
- In-app notification bell / email notification dispatching for booking status updates.
- Exportable PDF earning statements for tutors and platform commission analytics for admins.

---

## 🛠️ Project Setup & Execution Guide

### Prerequisites
- Python 3.10+
- Virtual environment (`venv`)

### 1. Environment Setup & Migration
```bash
# Navigate to the Django project directory
cd peertutor

# Apply database migrations
python manage.py migrate
```

### 2. Seed Demo Data (Optional)
To populate the database with realistic demo accounts (tutors, students, slots, bookings, reviews):
```bash
python "..\scratch\seed_demo_data.py"
```

### 3. Run Automated Tests
```bash
python manage.py test core
```

### 4. Start Development Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`.

---

## 🔑 Faculty Demo Credentials

| Role | Username / Email | Password | Pre-loaded Data |
|---|---|---|---|
| **Superuser Admin** | `admin@peertutor.com` | `Admin123!` | Oversee pending tutor applications & commission earnings. |
| **Verified Tutor 1** | `alex@peertutor.com` | `Password123!` | Python/Django tutor with completed session & open slots. |
| **Verified Tutor 2** | `sarah@peertutor.com` | `Password123!` | Data Structures tutor with 5.0 star rating & reviews. |
| **Student 1** | `john@peertutor.com` | `Password123!` | Student account with booking history & review capability. |
| **Student 2** | `emma@peertutor.com` | `Password123!` | Student account with active escrow bookings. |
