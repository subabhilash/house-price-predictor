import os
import joblib
import pandas as pd
import numpy as np

class HousePricePredictor:
    def __init__(self, model_path='models/house_price_model.joblib'):
        """Initialize with your existing trained model"""
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_columns = None
        
        print(f"🔍 Loading your trained model from: {model_path}")
        self.load_model()
    
    def load_model(self):
        """Load your existing trained model"""
        try:
            if not os.path.exists(self.model_path):
                print(f"❌ Your model file not found: {self.model_path}")
                return False
            
            print(f"📂 Loading your trained model...")
            self.model_data = joblib.load(self.model_path)
            
            # Handle different model file structures
            if isinstance(self.model_data, dict):
                # If it's a dictionary with components
                self.model = self.model_data.get('model')
                self.scaler = self.model_data.get('scaler')
                self.label_encoders = self.model_data.get('label_encoders', {})
                self.feature_columns = self.model_data.get('feature_columns', [])
            else:
                # If it's just the model object
                self.model = self.model_data
                print("⚠️ Model file contains only the model, creating default preprocessing")
                self._create_default_preprocessing()
            
            if self.model is None:
                print("❌ Could not extract model from file")
                return False
            
            model_name = getattr(self.model, '__class__', type(self.model)).__name__
            print(f"✅ Your trained model loaded: {model_name}")
            
            if hasattr(self.model, 'feature_names_in_'):
                print(f"📊 Model expects {len(self.model.feature_names_in_)} features")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading your model: {e}")
            print(f"📋 Error details: {type(e).__name__}")
            return False
    
    def _create_default_preprocessing(self):
        """Create default preprocessing for models without explicit preprocessing"""
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        
        # Default feature order matching your Flask form
        self.feature_columns = [
            'area', 'bedrooms', 'bathrooms', 'stories', 'parking',
            'mainroad', 'guestroom', 'basement', 'hotwaterheating',
            'airconditioning', 'prefarea', 'furnishingstatus'
        ]
        
        # Create default label encoders
        self.label_encoders = {
            'mainroad': self._create_binary_encoder(),
            'guestroom': self._create_binary_encoder(),
            'basement': self._create_binary_encoder(),
            'hotwaterheating': self._create_binary_encoder(),
            'airconditioning': self._create_binary_encoder(),
            'prefarea': self._create_binary_encoder(),
            'furnishingstatus': self._create_furnishing_encoder()
        }
        
        # Create default scaler (will be fitted with dummy data)
        self.scaler = StandardScaler()
        # Fit with dummy data to avoid errors
        dummy_data = np.random.randn(10, len(self.feature_columns))
        self.scaler.fit(dummy_data)
        
        print("⚙️ Created default preprocessing components")
    
    def _create_binary_encoder(self):
        """Create encoder for yes/no features"""
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['no', 'yes'])  # Fit with expected values
        return encoder
    
    def _create_furnishing_encoder(self):
        """Create encoder for furnishing status"""
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['unfurnished', 'semi-furnished', 'furnished'])
        return encoder
    
    def preprocess_input(self, house_features):
        """Preprocess input for your trained model"""
        try:
            # Create DataFrame
            input_df = pd.DataFrame([house_features])
            print(f"🔄 Preprocessing: {house_features}")
            
            # Handle categorical encoding
            categorical_features = ['mainroad', 'guestroom', 'basement', 'hotwaterheating',
                                  'airconditioning', 'prefarea', 'furnishingstatus']
            
            for col in categorical_features:
                if col in input_df.columns and col in self.label_encoders:
                    try:
                        input_df[col] = self.label_encoders[col].transform(input_df[col])
                    except ValueError as e:
                        print(f"⚠️ Unknown category in {col}: {input_df[col].iloc[0]}")
                        # Use most common value as fallback
                        if col == 'furnishingstatus':
                            input_df[col] = 0  # unfurnished
                        else:
                            input_df[col] = 0  # no
            
            # Ensure all features exist
            for col in self.feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            # Order columns correctly
            if hasattr(self.model, 'feature_names_in_'):
                # Use model's expected feature order
                feature_order = self.model.feature_names_in_
                input_df = input_df.reindex(columns=feature_order, fill_value=0)
            else:
                # Use our default order
                input_df = input_df[self.feature_columns]
            
            print(f"✅ Preprocessed shape: {input_df.shape}")
            return input_df
            
        except Exception as e:
            print(f"❌ Preprocessing error: {e}")
            return None
    
    def predict_price(self, house_features):
        """Make prediction using your trained model"""
        if not self.model:
            return self._fallback_prediction(house_features)
        
        try:
            print(f"🤖 Using your trained model for prediction")
            
            # Preprocess input
            processed_input = self.preprocess_input(house_features)
            if processed_input is None:
                return self._fallback_prediction(house_features)
            
            # Scale if scaler exists
            if self.scaler is not None:
                try:
                    scaled_input = self.scaler.transform(processed_input)
                    print("📊 Input scaled successfully")
                except:
                    print("⚠️ Scaling failed, using raw input")
                    scaled_input = processed_input.values
            else:
                scaled_input = processed_input.values
            
            # Make prediction
            prediction = self.model.predict(scaled_input)
            
            # Handle different prediction formats
            if isinstance(prediction, np.ndarray):
                price = float(prediction[0])
            else:
                price = float(prediction)
            
            # Ensure reasonable range
            price = max(50000, min(2000000, price))
            
            print(f"✅ Your model predicted: ${price:,.2f}")
            return price, None
            
        except Exception as e:
            print(f"⚠️ Your model prediction failed: {e}")
            print(f"🔄 Falling back to formula-based prediction")
            return self._fallback_prediction(house_features)
    
    def _fallback_prediction(self, house_features):
        """Fallback prediction when your model fails"""
        try:
            area = int(house_features.get('area', 2000))
            bedrooms = int(house_features.get('bedrooms', 3))
            bathrooms = int(house_features.get('bathrooms', 2))
            
            # Smart formula based on typical house pricing
            base_price = 180000
            area_price = area * 165
            room_bonus = (bedrooms * 15000) + (bathrooms * 20000)
            
            # Feature bonuses
            bonuses = 0
            if house_features.get('prefarea') == 'yes': bonuses += 40000
            if house_features.get('airconditioning') == 'yes': bonuses += 18000
            if house_features.get('furnishingstatus') == 'furnished': bonuses += 30000
            if house_features.get('mainroad') == 'yes': bonuses += 25000
            
            total = base_price + area_price + room_bonus + bonuses
            total = max(120000, min(900000, total))
            
            print(f"🧮 Fallback prediction: ${total:,.2f}")
            return float(total), "Fallback prediction used"
            
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
            return 275000.0, "Default prediction used"

# Initialize with your trained model
try:
    predictor = HousePricePredictor()
    print("🚀 Your trained model predictor initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    
    # Minimal fallback
    class MinimalPredictor:
        def predict_price(self, house_features):
            area = house_features.get('area', 2000)
            return float(200000 + area * 140), "Minimal predictor active"
    
    predictor = MinimalPredictor()
    print("🔄 Using minimal predictor as fallback")
