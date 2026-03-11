from flask import Blueprint

bp = Blueprint('frontend', __name__)

from app.frontend import routes, patient_routes, test_routes, order_routes, billing_routes, lab_routes, referral_routes, inventory_routes
