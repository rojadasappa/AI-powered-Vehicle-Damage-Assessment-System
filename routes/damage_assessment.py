"""
Damage assessment routes and functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from database_models import db, DamageReport
from models.hybrid_damage_detector import detect_damage_hybrid
from cost_estimator_enhanced import estimate_repair_cost
from models.severity_inference import ImprovedSeverityModel
import json

damage_bp = Blueprint('damage', __name__)

# Initialize best model (severity_best - 57.04% accuracy)
best_severity_model = ImprovedSeverityModel('models/saved_models/severity_best')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@damage_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_images():
    if request.method == 'POST':
        if 'images' not in request.files:
            return jsonify({'error': 'No images uploaded'}), 400
        
        files = request.files.getlist('images')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No images selected'}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        saved_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                saved_files.append(file_path)
        
        if not saved_files:
            return jsonify({'error': 'No valid images uploaded'}), 400
        
        # Process images for damage detection
        try:
            # Use best severity model (57.04% accuracy)
            severity_results = best_severity_model.predict_severity(saved_files)
            
            # Get damage analysis from Gemini
            results = detect_damage_hybrid(saved_files)
            
            # Update results with best severity
            results['severity'] = severity_results['severity']
            results['confidence'] = severity_results['confidence']
            
        # Damage type is already set by OpenAI analysis in hybrid detector
            
            # Estimate costs using enhanced estimator
            cost_estimate = estimate_repair_cost(results)
            
            # Save damage report with all available data
            damage_report = DamageReport(
                user_id=current_user.id,
                vehicle_type=results.get('vehicle_type', 'Unknown'),
                damage_type=results.get('damage_type', 'Unknown'),
                severity=results.get('severity', 'Unknown'),
                estimated_cost=cost_estimate.get('total_cost', 0),
                confidence_score=results.get('confidence', 0),
                image_paths=json.dumps(saved_files),
                status='completed',
                # Additional fields
                damage_description=results.get('damage_description'),
                affected_areas=json.dumps(results.get('affected_areas', [])),
                repair_urgency=results.get('repair_urgency'),
                estimated_repair_complexity=results.get('estimated_repair_complexity'),
                safety_concerns=results.get('safety_concerns'),
                repair_time_days=cost_estimate.get('repair_time_days'),
                cost_breakdown=json.dumps(cost_estimate.get('cost_breakdown', {})),
                recommendations=json.dumps(cost_estimate.get('recommendations', []))
            )
            
            db.session.add(damage_report)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'report_id': damage_report.id,
                'results': results,
                'cost_estimate': cost_estimate,
                'redirect': url_for('damage.results', report_id=damage_report.id)
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing images: {str(e)}'}), 500
    
    return render_template('damage/upload.html')

@damage_bp.route('/results/<int:report_id>')
@login_required
def results(report_id):
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    
    # Load image paths
    image_paths = json.loads(report.image_paths) if report.image_paths else []
    
    return render_template('damage/results.html', 
                         report=report, 
                         image_paths=image_paths)

@damage_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    reports = DamageReport.query.filter_by(user_id=current_user.id)\
                              .order_by(DamageReport.created_at.desc())\
                              .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('damage/history.html', reports=reports)

@damage_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """API endpoint for real-time damage analysis"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid image file'}), 400
    
    # Save temporary file
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_filename)
    file.save(temp_path)
    
    try:
        # Analyze single image with best model
        severity_results = best_severity_model.predict_severity([temp_path])
        results = detect_damage_hybrid([temp_path])
        
        # Update results with best severity
        results['severity'] = severity_results['severity']
        results['confidence'] = severity_results['confidence']
        
        # Damage type is already set by OpenAI analysis in hybrid detector
        
        cost_estimate = estimate_repair_cost(results)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'results': results,
            'cost_estimate': cost_estimate
        })
        
    except Exception as e:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@damage_bp.route('/api/vehicle_types')
def get_vehicle_types():
    """Get available vehicle types for classification - only supports cars"""
    vehicle_types = ['Car']  # Only support cars
    return jsonify({'vehicle_types': vehicle_types})

@damage_bp.route('/api/damage_types')
def get_damage_types():
    """Get available damage types for classification"""
    damage_types = [
        'Dent', 'Scratch', 'Broken Part', 'Crack', 'Rust', 'Paint Damage',
        'Structural Damage', 'Glass Damage', 'Light Damage', 'Bumper Damage'
    ]
    return jsonify({'damage_types': damage_types})
