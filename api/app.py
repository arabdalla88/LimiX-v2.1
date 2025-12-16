from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from config.firebase_config import FirebaseConfig
import os

app = Flask(__name__)
CORS(app)

FirebaseConfig.initialize(
    credential_path='serviceAccountKey.json',
    database_url=os.getenv('FIREBASE_DATABASE_URL', 'https://limix-fishfarm-v2-default-rtdb.firebaseio.com/')
)

sensor_ref = FirebaseConfig.get_reference('sensor_data')
fish_type_recommendations = FirebaseConfig.get_reference('fish_type')
fish_health = FirebaseConfig.get_reference('fish_health')

@app.route('/')
def home():
    return jsonify({
        'message': '🐟 Limix API',
        'version': '1.0',
        'endpoints': {
            '/api/sensor/latest': 'Latest reading sensors',
            '/api/fish-type/latest': 'Fish-Type recommendation',
            '/api/fish-health/latest': 'AI Fish Health check (POST with image)',
            '/api/dashboard': '⭐ All data (use this)',
        }
    })

@app.route('/api/sensor/latest')
def get_latest():
    try:
        data = sensor_ref.order_by_key().limit_to_last(1).get()
        if not data:
            return jsonify({'success': False}), 404
        
        latest = list(data.values())[0]
        return jsonify({
            'success': True,
            'data': {
                'ph': latest.get('ph'),
                'temperature': latest.get('temperature'),
                'turbidity': latest.get('turbidity'),
                'ammonia': latest.get('ammonia'),
                'do': latest.get('do'),
                'ec': latest.get('ec'),
                'timestamp': latest.get('timestamp')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fish-type/latest')
def get_recommendation():
    try:
        data = fish_type_recommendations.order_by_key().limit_to_last(1).get()
        if not data:
            return jsonify({'success': False}), 404
        
        rec = list(data.values())[0]
        return jsonify({
            'success': True,
            'data': {
                'fish_name': rec.get('fish_name'),
                'timestamp': rec.get('timestamp'),
                'confidence': rec.get('confidence')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

@app.route('/api/fish-health/latest', methods=['POST'])
def ai_health_check():
    if fish_health is None:
        return jsonify({
            'success': False,
            'error': 'AI model not loaded'
        }), 500

    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        image_file = request.files['image']
        filename = image_file.filename.lower()
        if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png')):
            return jsonify({'success': False, 'error': 'Invalid image format. Use JPG or PNG.'}), 400

        # Run prediction
        result = fish_health(image_file.stream)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard')
def dashboard():
    """⭐ Main endpoint for Flutter app"""
    try:
        # Latest
        latest_data = sensor_ref.order_by_key().limit_to_last(1).get()
        latest = list(latest_data.values())[0] if latest_data else {}
        
        # History
        history_data = sensor_ref.order_by_key().limit_to_last(20).get()
        history = []
        if history_data:
            for k, v in history_data.items():
                history.append({
                    'ph': v.get('ph'),
                    'temperature': v.get('temperature'),
                    'turbidity': v.get('turbidity'),
                    'ammonia': v.get('ammonia'),
                    'do': v.get('do'),
                    'ec': v.get('ec'),
                    'timestamp': v.get('timestamp')
                })
        
        # Averages
        if history:
            avg_ph = round(sum(h['ph'] for h in history) / len(history), 2)
            avg_temp = round(sum(h['temperature'] for h in history) / len(history), 2)
            avg_turb = round(sum(h['turbidity'] for h in history) / len(history), 2)
            avg_ammonia = round(sum(h['ammonia'] for h in history) / len(history), 2)
            avg_do = round(sum(h['do'] for h in history) / len(history), 2)
            avg_ec = round(sum(h['ec'] for h in history) / len(history), 2)
        else:
            avg_ph = avg_temp = avg_turb = 0
        
        # Recommendation
        rec_data = fish_type_recommendations.order_by_key().limit_to_last(1).get()
        fish_recommendation = list(rec_data.values())[0] if rec_data else None
        
        return jsonify({
            'success': True,
            'data': {
                'current': {
                    'ph': latest.get('ph', 0),
                    'temperature': latest.get('temperature', 0),
                    'turbidity': latest.get('turbidity', 0),
                    'ammonia': latest.get('ammonia', 0),
                    'do': latest.get('do', 0),
                    'ec': latest.get('ec', 0),
                    'timestamp': latest.get('timestamp')
                },
                'averages': {
                    'ph': avg_ph,
                    'temperature': avg_temp,
                    'turbidity': avg_turb,
                    'ammonia': avg_ammonia,
                    'do': avg_do,
                    'ec': avg_ec
                },
                'history': history,
                'recommendation': {
                    'fish_name': fish_recommendation.get('fish_name') if fish_recommendation else 'N/A',
                    'confidence': fish_recommendation.get('confidence') if fish_recommendation else 0
                } if fish_recommendation else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
