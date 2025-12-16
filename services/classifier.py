import joblib
import pandas as pd
from datetime import datetime

class FishClassifier:
    def __init__(self, model_path='models/best_dt_model.joblib', 
                 scaler_path='models/scaler_model.joblib'):
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print("✅ ML Model loaded")
        except Exception as e:
            print(f"❌ Model error: {e}")
            raise
    
    def classify(self, ph, temperature, turbidity):
        try:
            if not self._validate(ph, temperature, turbidity):
                return {'error': 'Invalid values'}
            
            X = pd.DataFrame([{
                'ph': float(ph),
                'temperature': float(temperature),
                'turbidity': float(turbidity)
            }])
            
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            fish_name = prediction.replace('fish_', '').title()
            
            return {
                'fish_type': prediction,
                'fish_name': fish_name,
                'ph': ph,
                'temperature': temperature,
                'turbidity': turbidity,
                'confidence': 85.0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _validate(self, ph, temp, turb):
        return (5.0 <= ph <= 9.5 and 0 <= temp <= 40 and 0 <= turb <= 20)
