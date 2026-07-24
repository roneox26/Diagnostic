from app import create_app
from app.extensions import db
from app.models.cms import SiteSetting, Testimonial, Partner

app = create_app()

with app.app_context():
    # Settings
    if not SiteSetting.query.filter_by(key='contact_phone').first():
        db.session.add(SiteSetting(key='contact_phone', value='+880-1234-567890'))
    if not SiteSetting.query.filter_by(key='contact_email').first():
        db.session.add(SiteSetting(key='contact_email', value='info@medcare.com'))
    if not SiteSetting.query.filter_by(key='address').first():
        db.session.add(SiteSetting(key='address', value='123 Medical Plaza, Healthcare District\nDhaka - 1205, Bangladesh'))
    if not SiteSetting.query.filter_by(key='years_experience').first():
        db.session.add(SiteSetting(key='years_experience', value='15+'))
    
    # Testimonials
    if Testimonial.query.count() == 0:
        db.session.add_all([
            Testimonial(name='Dr. Rahman', role='Cardiologist', content='Excellent service and accurate results. The online report system is very convenient and the staff is professional.', rating=5),
            Testimonial(name='Sarah Ahmed', role='Patient', content='Fast and reliable service. Home collection facility is amazing. Got my reports within 24 hours.', rating=5),
            Testimonial(name='Hospital Admin', role='Healthcare Partner', content='Professional team and state-of-the-art equipment. Their quality control is excellent.', rating=5)
        ])
    
    # Partners
    if Partner.query.count() == 0:
        db.session.add_all([
            Partner(name='City Hospital', icon_class='fas fa-hospital text-primary', partner_type='corporate'),
            Partner(name='Health Clinic', icon_class='fas fa-clinic-medical text-success', partner_type='corporate'),
            Partner(name='Medical Center', icon_class='fas fa-user-md text-info', partner_type='corporate'),
            Partner(name='Care Plus', icon_class='fas fa-heartbeat text-danger', partner_type='corporate'),
            Partner(name='Emergency Care', icon_class='fas fa-ambulance text-warning', partner_type='corporate'),
            
            Partner(name='Logistics Partners', icon_class='fas fa-shipping-fast text-primary', description='Fast & reliable sample transportation', partner_type='service'),
            Partner(name='Technology Partners', icon_class='fas fa-laptop-medical text-success', description='Advanced diagnostic equipment', partner_type='service'),
            Partner(name='Pharma Partners', icon_class='fas fa-pills text-info', description='Quality reagents & supplies', partner_type='service'),
            Partner(name='Academic Partners', icon_class='fas fa-graduation-cap text-warning', description='Research & development collaboration', partner_type='service')
        ])
        
    db.session.commit()
    print("CMS data seeded successfully!")
