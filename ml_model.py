import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

class HousePricePredictor:
    def __init__(self, model_path='models/house_price_model.joblib'):
        """Initialize the house price predictor"""
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_columns = None
        
        # Check if ML packages are available
        self.ml_available = self._check_ml_availability()
        
        if self.ml_available:
            self.load_model()
        else:
            print("⚠️ ML model disabled - required packages not available")
    
    def _check_ml_availability(self):
        """Check if all required ML packages are available"""
        try:
            import joblib
            import pandas as pd
            import numpy as np
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            print("✅ ML packages loaded successfully")
            return True
        except ImportError as e:
            print(f"⚠️ ML packages error: {e}")
            return False
    
    def load_model(self):
        """Load the trained model and preprocessing components"""
        if not self.ml_available:
            return False
            
        try:
            if os.path.exists(self.model_path):
                print(f"📁 Loading model from: {self.model_path}")
                self.model_data = joblib.load(self.model_path)
                
                # Extract model components
                self.model = self.model_data.get('model')
                self.scaler = self.model_data.get('scaler')
                self.label_encoders = self.model_data.get('label_encoders', {})
                self.feature_columns = self.model_data.get('feature_columns', [])
                
                # Validate that all components are loaded
                if not all([self.model, self.scaler, self.label_encoders, self.feature_columns]):
                    print("❌ Model file is missing required components")
                    return False
                
                model_name = self.model_data.get('model_name', 'Unknown Model')
                print(f"✅ Model loaded successfully: {model_name}")
                return True
            else:
                print(f"❌ Model file not found: {self.model_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_data = None
            return False
    
    def preprocess_input(self, house_features):
        """Preprocess input features for prediction"""
        if not self.ml_available or not self.model_data:
            return None
            
        try:
            # Create DataFrame from input
            input_df = pd.DataFrame([house_features])
            print(f"🔄 Preprocessing input: {house_features}")
            
            # Apply label encoding for categorical variables
            for col, encoder in self.label_encoders.items():
                if col in input_df.columns:
                    try:
                        input_df[col] = encoder.transform(input_df[col])
                    except ValueError as e:
                        print(f"⚠️ Unknown category in {col}: {input_df[col].iloc[0]}, using default value")
                        # Use the first class as default for unknown categories
                        input_df[col] = encoder.transform([encoder.classes_[0]])[0]
            
            # Handle one-hot encoded columns if they exist
            onehot_columns = [col for col in self.feature_columns if '_' in col and col not in house_features.keys()]
            if onehot_columns:
                base_categorical_columns = list(set([col.split('_')[0] for col in onehot_columns]))
                
                for base_col in base_categorical_columns:
                    if base_col in input_df.columns:
                        value = input_df[base_col].iloc[0]
                        # Create one-hot columns
                        for feature_col in self.feature_columns:
                            if feature_col.startswith(f"{base_col}_"):
                                category = feature_col.replace(f"{base_col}_", "")
                                input_df[feature_col] = 1 if str(value) == category else 0
                        # Remove original column
                        input_df = input_df.drop(base_col, axis=1)
            
            # Ensure all required columns are present
            for col in self.feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
                    print(f"⚠️ Missing column {col}, setting to 0")
            
            # Reorder columns to match training data
            input_df = input_df[self.feature_columns]
            print(f"✅ Preprocessing complete. Shape: {input_df.shape}")
            
            return input_df
            
        except Exception as e:
            print(f"❌ Error preprocessing input: {e}")
            return None
    
    def predict_price(self, house_features):
        """Predict house price"""
        if not self.ml_available:
            # Return a reasonable dummy prediction based on area
            area = house_features.get('area', 2000)
            bedrooms = house_features.get('bedrooms', 3)
            bathrooms = house_features.get('bathrooms', 2)
            
            # Simple formula for dummy prediction
            base_price = 200000
            area_price = area * 150
            room_bonus = (bedrooms + bathrooms) * 10000
            
            # Add bonuses for premium features
            if house_features.get('prefarea') == 'yes':
                area_price *= 1.2
            if house_features.get('airconditioning') == 'yes':
                area_price *= 1.1
            if house_features.get('furnishingstatus') == 'furnished':
                area_price *= 1.15
            
            dummy_price = base_price + area_price + room_bonus
            print(f"🎯 Generated dummy prediction: ${dummy_price:,.2f}")
            return float(dummy_price), "Using dummy prediction - ML model not available"
        
        if not self.model_data:
            return None, "Model not loaded"
        
        try:
            print(f"🔮 Making prediction for: {house_features}")
            
            # Preprocess input
            processed_input = self.preprocess_input(house_features)
            if processed_input is None:
                return None, "Failed to preprocess input"
            
            # Scale features
            scaled_input = self.scaler.transform(processed_input)
            print(f"📊 Input scaled successfully")
            
            # Make prediction
            prediction = self.model.predict(scaled_input)
            
            # Convert numpy data type to Python float for database compatibility
            python_float = float(prediction[0])
            print(f"✅ Prediction successful: ${python_float:,.2f}")
            
            return python_float, None
        
        except Exception as e:
            error_msg = f"Prediction failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Fallback to dummy prediction on error
            area = house_features.get('area', 2000)
            fallback_price = 200000 + (area * 150)
            print(f"🔄 Using fallback prediction: ${fallback_price:,.2f}")
            
            return float(fallback_price), error_msg
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if not self.ml_available:
            return {
                'status': 'ML packages not available',
                'ml_available': False,
                'model_loaded': False
            }
        
        if self.model_data:
            return {
                'status': 'Model loaded successfully',
                'ml_available': True,
                'model_loaded': True,
                'model_name': self.model_data.get('model_name', 'Unknown'),
                'training_date': self.model_data.get('training_date', 'Unknown'),
                'metrics': self.model_data.get('model_metrics', {}),
                'features': self.feature_columns,
                'model_path': self.model_path
            }
        else:
            return {
                'status': 'Model not loaded',
                'ml_available': True,
                'model_loaded': False,
                'model_path': self.model_path
            }

# Initialize global predictor (will be used in Flask app)
try:
    predictor = HousePricePredictor()
    print("🚀 HousePricePredictor initialized")
except Exception as e:
    print(f"❌ Failed to initialize predictor: {e}")
    # Create a minimal predictor that always returns dummy predictions
    class DummyPredictor:
        def __init__(self):
            self.ml_available = False
            self.model_data = None
        
        def predict_price(self, house_features):
            area = house_features.get('area', 2000)
            dummy_price = 200000 + (area * 150)
            return float(dummy_price), "Using dummy prediction - initialization failed"
        
        def get_model_info(self):
            return {'status': 'Dummy predictor active', 'ml_available': False}
    
    predictor = DummyPredictor()
    print("🔄 Using dummy predictor as fallback")
