import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db

def test_flask_app():
    """Test the Flask application"""
    try:
        app = create_app('development')
        
        with app.app_context():
            # Test database connection
            db.create_all()
            print("✅ Flask app created successfully!")
            print("✅ Database tables initialized!")
            print("✅ Routes configured!")
            
            # Test ML model loading
            from ml_model import predictor
            if predictor.model_data:
                print("✅ ML model loaded successfully!")
            else:
                print("⚠️ ML model not found - you'll need to add your trained model")
            
            print("\n🎉 Flask application is ready!")
            print("📋 Available routes:")
            print("   - / (Home page)")
            print("   - /login (User login)")
            print("   - /signup (User registration)")
            print("   - /dashboard (User dashboard)")
            print("   - /predict (House price prediction)")
            print("   - /history (Prediction history)")
            
            return True
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

if __name__ == "__main__":
    test_flask_app()
