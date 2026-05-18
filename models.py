from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional

@dataclass
class Client:
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""

@dataclass
class Person:
    role: str = "Witness"
    name: str = ""
    dob: str = ""
    phone: str = ""
    address: str = ""
    vehicle: str = ""
    notes: str = ""

@dataclass
class Task:
    task: str
    done: bool = False

@dataclass
class CourtDate:
    reason: str
    date: str
    time: str = ""
    location: str = ""

@dataclass
class DiscoveryLink:
    title: str
    url: str

@dataclass
class ServiceFee:
    date: str
    activity: str
    hours: float
    rate: float
    amount: float

@dataclass
class OtherExpense:
    date: str
    expense: str
    qty: float
    rate: float
    amount: float

@dataclass
class TravelMileage:
    date: str
    expense: str
    qty: float
    rate: float
    amount: float

@dataclass
class CaseFile:
    filename: str
    category: str
    upload_date: str
    size: str
    path: str

@dataclass
class CaseDetail:
    case_id: str
    client: Client = field(default_factory=Client)
    people: List[Person] = field(default_factory=list)
    statements: List[Dict] = field(default_factory=list)
    taskings: List[Task] = field(default_factory=list)
    discovery: List[DiscoveryLink] = field(default_factory=list)
    trial_info: Dict = field(default_factory=lambda: {"case_number": "", "court_dates": []})
    case_notes: str = ""
    billing: Dict = field(default_factory=lambda: {
        "service_fees": [],
        "other_expenses": [],
        "travel_mileage": []
    })
    files: List[CaseFile] = field(default_factory=list)
    invoice_number: str = ""
    invoice_period: str = ""
