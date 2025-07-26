import joblib
import pandas as pd
import numpy as np
import os

class HousePricePredictor:
    def __init__(self, model_path='models/house_price_model.joblib'):
        """Initialize the house price predictor"""
        self.model_path = model_path
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessing components"""
        try:
            if os.path.exists(self.model_path):
                self.model_data = joblib.load(self.model_path)
                self.model = self.model_data['model']
                self.scaler = self.model_data['scaler']
                self.label_encoders = self.model_data['label_encoders']
                self.feature_columns = self.model_data['feature_columns']
                print(f"✅ Model loaded successfully: {self.model_data['model_name']}")
                return True
            else:
                print(f"❌ Model file not found: {self.model_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def preprocess_input(self, house_features):
        """Preprocess input features for prediction"""
        # Create DataFrame from input
        input_df = pd.DataFrame([house_features])
        
        # Apply label encoding for categorical variables
        for col, encoder in self.label_encoders.items():
            if col in input_df.columns:
                try:
                    input_df[col] = encoder.transform(input_df[col])
                except ValueError:
                    print(f"⚠️ Unknown category in {col}, using default value")
                    input_df[col] = 0
        
        # Handle one-hot encoded columns
        onehot_columns = [col for col in self.feature_columns if '_' in col]
        base_categorical_columns = list(set([col.split('_')[0] for col in onehot_columns]))
        
        for base_col in base_categorical_columns:
            if base_col in input_df.columns:
                value = input_df[base_col].iloc[0]
                # Create one-hot columns
                for feature_col in self.feature_columns:
                    if feature_col.startswith(f"{base_col}_"):
                        category = feature_col.replace(f"{base_col}_", "")
                        input_df[feature_col] = 1 if value == category else 0
                # Remove original column
                input_df = input_df.drop(base_col, axis=1)
        
        # Ensure all required columns are present
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        # Reorder columns to match training data
        input_df = input_df[self.feature_columns]
        return input_df
    
    def predict_price(self, house_features):
        """Predict house price"""
        try:
            if not self.model_data:
                return None, "Model not loaded"
            
            # Preprocess input
            processed_input = self.preprocess_input(house_features)
            
            # Scale features
            scaled_input = self.scaler.transform(processed_input)
            
            # Make prediction
            prediction = self.model.predict(scaled_input)
            
            # Convert numpy data type to Python float for database compatibility
            python_float = float(prediction[0])
            
            return python_float, None
        
        except Exception as e:
            return None, str(e)
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.model_data:
            return {
                'model_name': self.model_data['model_name'],
                'training_date': self.model_data['training_date'],
                'metrics': self.model_data['model_metrics'],
                'features': self.feature_columns
            }
        return None

# Initialize global predictor (will be used in Flask app)
predictor = HousePricePredictor()
