import threading # for thread class and thread lock
import time
from datetime import date, datetime
from database import get_db
_alerts = []
_lock   = threading.Lock()
def get_alerts():
    with _lock:
        return list(_alerts)
    
class ExpiryCheckerThread(threading.Thread):
    def __init__(self, interval=30):
        super().__init__()
        self.interval = interval
        self.daemon   = True

    def run(self):
        print("[Thread] Started! Checking every", self.interval, "seconds")
        while True:
            self._check_medicines()
            time.sleep(self.interval)
            
    def _check_medicines(self):
        today      = date.today()
        new_alerts = []

        try:
            conn      = get_db()
            medicines = conn.execute("SELECT * FROM medicines").fetchall()
            conn.close()

            for med in medicines:
                exp       = datetime.strptime(med["expiry_date"], "%Y-%m-%d").date()
                days_left = (exp - today).days

                if days_left < 0:
                    new_alerts.append({
                        "type"   : "danger",
                        "icon"   : "💀",
                        "message": f"{med['name']} has EXPIRED!",
                        "med_id" : med["id"]
                    })
                elif days_left <= 30:
                    new_alerts.append({
                        "type"   : "warning",
                        "icon"   : "⚠️",
                        "message": f"{med['name']} expires in {days_left} day(s)",
                        "med_id" : med["id"]
                    })

                if med["quantity"] <= 10:
                    new_alerts.append({
                        "type"   : "info",
                        "icon"   : "📦",
                        "message": f"{med['name']} — only {med['quantity']} left!",
                        "med_id" : med["id"]
                    })

            with _lock:
                _alerts.clear()
                _alerts.extend(new_alerts)

            print(f"[Thread] Check done — {len(new_alerts)} alert(s)")

        except Exception as e:
            print("[Thread] Error:", e)
def start_checker():
    thread = ExpiryCheckerThread(interval=30)
    thread.start()