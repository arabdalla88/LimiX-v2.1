import random
import time
from datetime import datetime
from config.firebase_config import FirebaseConfig
from services.classifier import FishClassifier
from services.fish_disease import predict_fish_health

class LimixBackend:
    def __init__(self):
        self.classifier = FishClassifier()
        self.sensor_ref = FirebaseConfig.get_reference('sensor_data')
        self.recommendations_ref = FirebaseConfig.get_reference('fish_type')
        self.fish_health_ref = FirebaseConfig.get_reference('fish_health')
        print("✅ Backend initialized")
    
    def generate_data(self):
        return {
            'ph': round(7.4 + random.uniform(-0.2, 0.2), 2),          # ~7.2 - 7.6
            'temperature': round(27.5 + random.uniform(-1.0, 1.0), 2), # ~26.5 - 28.5 °C
            'turbidity': round(4.5 + random.uniform(-0.8, 0.8), 2),    # ~3.7 - 5.3 NTU
            'do': round(6.2 + random.uniform(-0.7, 0.5), 2),           # ~5.5 - 6.7 mg/L
            'ec': round(1100 + random.uniform(-150, 150), 1),          # ~950 - 1250 µS/cm
            'ammonia': round(0.012 + random.uniform(-0.005, 0.008), 3),# ~0.007 - 0.020 mg/L
            'timestamp': datetime.now().isoformat()
        }
    
    def start_simulator(self, interval=5):
        print("📡 Simulator started")
        num = 0
        try:
            while True:
                num += 1
                data = self.generate_data()
                self.sensor_ref.push(data)
                print(f"📤 #{num}: pH={data['ph']}, TEMP={data['temperature']}°C, TUR={data['turbidity']}NTU, DO={data['do']}mg/L, EC={data['ec']}µS/cm, NH3={data['ammonia']}mg/L")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("⚠️ Stopped")
    
    def on_new_data(self, event):
        if not event.data:
            return
        
        data = event.data
        print(f"🔔 New: pH={data.get('ph')}, TEMP={data.get('temperature')}°C, TUR={data.get('turbidity')}NTU, DO={data.get('do')}mg/L, EC={data.get('ec')}µS/cm, NH3={data.get('ammonia')}mg/L")
        
        result = self.classifier.classify(
            data.get('ph'),
            data.get('temperature'),
            data.get('turbidity'),
        )
        
        if 'error' not in result:
            print(f"🐟 Recommended: {result['fish_name']}")
            self.recommendations_ref.push({
                'fish_type': result['fish_type'],
                'fish_name': result['fish_name'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp']
            })
    
    def start_listener(self):
        print("👂 Listener started")
        self.sensor_ref.listen(self.on_new_data)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("⚠️ Stopped")

    def check_fish_health_from_image(self, image_path):
        """
        Check if fish is healthy or sick from an image file.
        Returns prediction result.
        """
        if predict_fish_health is None:
            return {"error": "Fish disease model not loaded. Check services/fish_disease.py"}

        try:
            # Load and predict
            result = predict_fish_health(image_path)
            
            # Save to Firebase (optional)
            self.fish_health_ref.push({
                **result,
                'timestamp': datetime.now().isoformat(),
                'image_source': image_path
            })
            
            return result

        except Exception as e:
            return {"error": str(e)}
