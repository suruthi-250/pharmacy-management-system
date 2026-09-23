import sqlite3
import hashlib
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "pharmacy.db")
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  #stores data in a dictionary format
    return conn
def init_db():
    conn = get_db()
    cur  = conn.cursor()  #writes commands into DB
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role     TEXT NOT NULL
    )
""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        type        TEXT NOT NULL,
        quantity    INTEGER NOT NULL,
        price       REAL NOT NULL,
        expiry_date TEXT NOT NULL,
        supplier    TEXT
       
    )
""")
    cur.execute(""" 
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        medicine_name TEXT,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        total_price REAL NOT NULL,
        sold_by  TEXT NOT NULL,
        sold_at   TEXT NOT NULL,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        action    TEXT NOT NULL,
        done_by   TEXT NOT NULL,
        details   TEXT,
        timestamp TEXT NOT NULL
    )
""")
    conn.commit()
    conn.close()
    
    seed_users()     
    seed_medicines()
   
   
def seed_users():
    conn = get_db()
    cur  = conn.cursor()

    def hash_pw(pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    if not cur.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        cur.execute("INSERT INTO users VALUES (NULL, 'admin', ?, 'admin')",
                    (hash_pw("admin123"),))

    if not cur.execute("SELECT 1 FROM users WHERE username='pharmacist'").fetchone():
        cur.execute("INSERT INTO users VALUES (NULL, 'pharmacist', ?, 'pharmacist')",
                    (hash_pw("pharma123"),))

    conn.commit()
    conn.close()
def seed_medicines():
    conn = get_db()
    cur  = conn.cursor()

    if not cur.execute("SELECT 1 FROM medicines").fetchone():
        sample = [
            ("Paracetamol 500mg",  "Generic",     150, 2.50,  "2026-06-15", "MedSupply Co."),
            ("Amoxicillin 250mg",  "Prescription",  8, 12.00, "2026-12-01", "PharmaCorp"),
            ("Ibuprofen 400mg",    "Generic",        5, 5.00,  "2026-09-30", "MedSupply Co."),
            ("Tulsi Drops",        "Herbal",        60, 15.00, "2026-03-10", "HerbalLife"),
            ("Cetirizine 10mg",    "Generic",        8, 3.00,  "2026-11-22", "AllergyPlus"),
            ("Morphine 10mg",      "Controlled",    20, 45.00, "2026-08-15", "PainCare Ltd."),
        ]
        cur.executemany(
            "INSERT INTO medicines VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            sample
        )
    conn.commit()
    conn.close()