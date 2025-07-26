from app import create_app
import os

def main():
    """Run the Flask application"""
    print("🚀 Starting House Price Predictor Application...")
    
    # Check if ML model exists
    model_path = 'models/house_price_model.joblib'
    if not os.path.exists(model_path):
        print("⚠️  ML model not found at 'models/house_price_model.joblib'")
        print("   Copy your trained model to the models/ folder to enable predictions")
        print("   The app will still run without the model for testing the interface")
    
    # Create Flask app
    app = create_app('development')
    
    print("✅ Flask application ready!")
    print("📋 Application URLs:")
    print("   - Home: http://localhost:5000/")
    print("   - Login: http://localhost:5000/login")
    print("   - Signup: http://localhost:5000/signup")
    print("   - Dashboard: http://localhost:5000/dashboard (login required)")
    print("   - Predict: http://localhost:5000/predict (login required)")
    print("   - History: http://localhost:5000/history (login required)")
    
    print("\n🎯 Next Steps:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Create a new account")
    print("   3. Test the prediction interface")
    print("   4. Copy your trained ML model to enable predictions")
    
    print("\n🔥 Starting server...")
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )

if __name__ == '__main__':
    main()
