import os
from app import create_app
from app.extensions import db

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    from flask_migrate import upgrade
    try:
        # Create instance folder if it doesn't exist
        os.makedirs(app.instance_path, exist_ok=True)
        # Run database migrations
        upgrade()
        print("Database upgraded successfully on startup.")
    except Exception as e:
        print(f"Failed to upgrade database: {e}")
        # Fallback to create_all
        db.create_all()
        print("Fallback: Created tables using db.create_all().")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
