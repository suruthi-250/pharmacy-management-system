# Pharmacy Management System (PharmaCare)

A web-based Pharmacy Management System developed as a **Mini Project (24CSE48)** for the academic year **2025–26 (Even Sem)** at **New Horizon College of Engineering, Bengaluru**.

The system digitizes day-to-day pharmacy operations — replacing manual, paper-based record keeping with a secure, automated solution for managing medicines, inventory, sales/billing, users, and alerts.

---

## 👥 Authors

| Name | USN | Sem – Sec |
|------|-----|-----------|
| H Suruthi | 1NH24CS220 | 4 – D |
| Tammineedi Lakshmi Chinmayee | 1NH24CS221 | 4 – D |

**Guide / Reviewer:** Ms. Pravallika Medidi, Assistant Professor, Dept. of CSE, NHCE

---

## 🎯 Features

- **Secure Login Authentication** — SHA-256 hashed passwords with session management and role-based access (`admin` / `pharmacist`)
- **Dashboard** — live overview of total medicines, low-stock count, expired and expiring-soon items with alert notifications
- **Inventory Management** — add, edit, delete, search and filter medicines (by name and type); negative quantity/price validation; admin-only deletion
- **Sales & Billing** — record sales with automatic stock reduction, total price calculation and validation against available stock
- **Background Expiry Checker Thread** — a daemon thread scans the database every 30 seconds and raises alerts for expired / low-stock / soon-expiring medicines (also exposed via `/api/alerts` JSON endpoint)
- **User Management** — admins can add/delete staff accounts with roles
- **Audit Log** — every add, edit, delete, sale and user action is logged with timestamp and user for traceability
- **OOP Design** — an abstract `Medicine` class with `GenericMedicine`, `PrescriptionMedicine`, `HerbalMedicine` and `ControlledMedicine` subclasses (factory pattern via `create_medicine()`)

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask |
| Frontend | HTML, CSS (Jinja2 templates) |
| Database | SQLite |
| Security | SHA-256 password hashing, Flask sessions |

## 🗂️ Project Structure

```
Pharmacy-Management-System/
├── app.py               # Flask routes: auth, dashboard, medicines, sales, users, audit, alerts API
├── database.py          # SQLite connection, schema creation & seed data
├── models.py            # Abstract Medicine class + subclasses (factory pattern)
├── threads.py           # ExpiryCheckerThread (background stock/expiry monitoring)
├── pharmacy.db          # SQLite database file (auto-created on first run)
├── templates/           # Jinja2 HTML templates (login, dashboard, medicines, sales, alerts, audit, users)
├── docs/
│   └── Project_Report.pdf   # Full mini project report
├── screenshots/         # Application screenshots
├── requirements.txt
├── .gitignore
└── LICENSE
```

## ⚙️ Prerequisites

- Python 3.8+
- pip

## 🚀 Installation & Running

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/pharmacy-management-system.git
cd pharmacy-management-system

# 2. (Optional but recommended) create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

> The database tables and default users are created automatically on the first run.

## 🔑 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | admin (full access incl. user management, audit log, deletions) |
| `pharmacist` | `pharma123` | pharmacist (daily operations) |

## 📸 Screenshots

| Login | Dashboard |
|-------|-----------|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

| Inventory | Customers |
|-----------|-----------|
| ![Medicines](screenshots/medicines.png) | ![Customers](screenshots/customers.png) |

| Sales / Billing | Generated Bill |
|-----------------|----------------|
| ![Sales](screenshots/billing.png) | ![Bill](screenshots/billing_1.png) |

## 📄 Project Report

The complete project report (abstract, design, ER model, implementation, results and conclusion) is available here: [docs/Project_Report.pdf](docs/Project_Report.pdf)

## 🔮 Future Scope

- Online payment integration (UPI / cards / wallets)
- Automatic SMS/email expiry & low-stock notifications
- Barcode scanning for faster billing and stock intake
- GST-compliant invoice generation and financial reports
- Cloud database & multi-branch support
- Role-based dashboards and mobile app

## 📚 References

- [Python Documentation](https://www.python.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [SQLite Documentation](https://www.sqlite.org)
- [MDN Web Docs](https://developer.mozilla.org)

## 📜 License

This project is released under the [MIT License](LICENSE) — free to use, modify and distribute with attribution.

---

*Mini Project (24CSE48) — Department of Computer Science and Engineering, New Horizon College of Engineering, 2025–26.*
