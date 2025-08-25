from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("✅ Database created successfully!")
        print(f"📁 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    app.run(debug=True)
