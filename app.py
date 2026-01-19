from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import create_map_poster
from threading import Thread
import uuid

app = Flask(__name__)

# Initial config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTERS_DIR = os.path.join(BASE_DIR, "posters")

# Global job store (In-memory for simplicity)
JOBS = {}

def create_poster_wrapper(job_id, city, country, distance, theme_config, layers, font_style):
    def progress_callback(stage, progress):
        JOBS[job_id]['stage'] = stage
        JOBS[job_id]['progress'] = progress
    
    try:
        # Generate output filename
        timestamp = create_map_poster.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        city_slug = city.lower().replace(' ', '_')
        filename = f"{city_slug}_{theme_config['name'].lower().replace(' ', '_')}_{timestamp}_{unique_id}.png"
        output_path = os.path.join(POSTERS_DIR, filename)

        # Get coordinates with callback
        progress_callback("Finding coordinates...", 2)
        coords = create_map_poster.get_coordinates(city, country)
        
        create_map_poster.create_poster(
            city, country, coords, distance, output_path, theme_config,
            progress_callback=progress_callback,
            layers=layers,
            font_style=font_style
        )
        
        JOBS[job_id]['status'] = 'completed'
        JOBS[job_id]['result'] = f'/posters/{filename}'
        JOBS[job_id]['progress'] = 100
        
    except Exception as e:
        print(f"Error in background job: {e}")
        import traceback
        traceback.print_exc()
        JOBS[job_id]['status'] = 'failed'
        JOBS[job_id]['error'] = str(e)

@app.route('/')
def index():
    themes = create_map_poster.get_available_themes()
    return render_template('index.html', themes=themes)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        city = data.get('city')
        country = data.get('country')
        theme = data.get('theme', 'feature_based')
        distance = int(data.get('distance', 29000))
        layers = data.get('layers', {'roads': True, 'water': True, 'parks': True})
        font_style = data.get('font', 'roboto')
        
        if not city or not country:
            return jsonify({'error': 'City and Country are required'}), 400
        
        # Load theme
        theme_config = create_map_poster.load_theme(theme)
        
        # Ensure posters dir exists calls
        if not os.path.exists(POSTERS_DIR):
            os.makedirs(POSTERS_DIR)

        # Create Job
        job_id = str(uuid.uuid4())
        JOBS[job_id] = {
            'status': 'running',
            'progress': 0,
            'stage': 'Initializing...',
            'result': None
        }
        
        # Start background thread
        thread = Thread(target=create_poster_wrapper, args=(job_id, city, country, distance, theme_config, layers, font_style))
        thread.start()
        
        return jsonify({
            'success': True, 
            'job_id': job_id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>')
def job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/posters/<path:filename>')
def serve_poster(filename):
    return send_from_directory(POSTERS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
