# Export all models for easier initialization and map loading with Flask-Migrate
from .users import User
from .patient import Patient
from .test_catalog import TestCategory, Test
from .order import TestOrder, TestOrderItem
from .lab import Sample, TestResult, Report
from .billing import Invoice, InvoiceItem
from .referral import ReferralDoctor, ReferralCommission
from .inventory import InventoryItem, TestReagentConsumption
from .appointment import DoctorSchedule, Appointment
