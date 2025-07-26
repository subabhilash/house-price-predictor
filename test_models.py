from flask import Flask
from models import db, User, Prediction
from config import DevelopmentConfig

def test_models():
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test creating a user
            test_user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            test_user.set_password('testpassword')
            
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            
            # Test creating a prediction
            test_prediction = Prediction(
                user_id=test_user.id,
                area=2000,
                bedrooms=3,
                bathrooms=2,
                stories=2,
                parking=1,
                mainroad='yes',
                guestroom='no',
                basement='no',
                hotwaterheating='no',
                airconditioning='yes',
                prefarea='yes',
                furnishingstatus='furnished',
                predicted_price=350000.0
            )
            
            db.session.add(test_prediction)
            db.session.commit()
            print("✅ Test prediction created successfully!")
            
            # Query data back
            users = User.query.all()
            predictions = Prediction.query.all()
            
            print(f"✅ Found {len(users)} users and {len(predictions)} predictions")
            print(f"✅ User: {users[0].get_full_name()} ({users[0].email})")
            print(f"✅ Prediction: ${predictions[0].predicted_price:,.2f} for {predictions[0].area} sq ft house")
            
            print("🎉 Database models are working perfectly!")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

if __name__ == "__main__":
    test_models()
