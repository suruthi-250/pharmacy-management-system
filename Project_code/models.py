from abc import ABC, abstractmethod
from datetime import date, datetime
from math import exp
class Medicine(ABC):
    def __init__(self, name, quantity,price,expiry_date,supplier):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.expiry_date = expiry_date
        self.supplier = supplier
    @abstractmethod
    def get_type(self):
        pass
    @abstractmethod
    def get_info(self):
        pass
    @abstractmethod
    def is_restricted(self):
        pass
    def is_expired(self):
        exp = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return exp < date.today()

    def days_until_expiry(self):
        exp = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return (exp - date.today()).days

class GenericMedicine(Medicine):
    def get_type(self):
        return "Generic"
    def get_info(self):
        return "Available without prescription"
    def is_restricted(self):
        return False

class PrescriptionMedicine(Medicine):
    def get_type(self):
        return "Prescription"
    def get_info(self):
        return "Requires a doctor's prescription"
    def is_restricted(self):
        return False

class HerbalMedicine(Medicine):
    def get_type(self):
        return "Herbal"
    def get_info(self):
        return "Natural remedy with minimal side effects"
    def is_restricted(self):
        return False

class ControlledMedicine(Medicine):
    def get_type(self):
        return "Controlled"
    def get_info(self):
        return "Subject to strict regulations and monitoring"
    def is_restricted(self):
        return True
    
def create_medicine(med_type, name, quantity, price, expiry_date, supplier):
    classes = {
        "Generic"      : GenericMedicine,
        "Prescription" : PrescriptionMedicine,
        "Herbal"       : HerbalMedicine,
        "Controlled"   : ControlledMedicine,
    }
    MedicineClass = classes.get(med_type, GenericMedicine)
    return MedicineClass(name, quantity, price, expiry_date, supplier)