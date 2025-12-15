"""
API routes for external integrations and mobile app
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from database_models import db, DamageReport
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from repair_shop_finder import RepairShopFinder
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Vehicle Damage Assessment API is running'})

@api_bp.route('/user/profile')
@login_required
def get_user_profile():
    """Get current user profile"""
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'phone': current_user.phone,
        'created_at': current_user.created_at.isoformat()
    })

@api_bp.route('/reports')
@login_required
def get_reports():
    """Get user's damage reports with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reports = DamageReport.query.filter_by(user_id=current_user.id)\
                              .order_by(DamageReport.created_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'vehicle_type': report.vehicle_type,
            'damage_type': report.damage_type,
            'severity': report.severity,
            'estimated_cost': report.estimated_cost,
            'confidence_score': report.confidence_score,
            'created_at': report.created_at.isoformat(),
            'status': report.status
        } for report in reports.items],
        'pagination': {
            'page': reports.page,
            'pages': reports.pages,
            'per_page': reports.per_page,
            'total': reports.total,
            'has_next': reports.has_next,
            'has_prev': reports.has_prev
        }
    })

@api_bp.route('/reports/<int:report_id>')
@login_required
def get_report(report_id):
    """Get specific damage report"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first()
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    image_paths = json.loads(report.image_paths) if report.image_paths else []
    
    return jsonify({
        'id': report.id,
        'vehicle_type': report.vehicle_type,
        'damage_type': report.damage_type,
        'severity': report.severity,
        'estimated_cost': report.estimated_cost,
        'confidence_score': report.confidence_score,
        'image_paths': image_paths,
        'created_at': report.created_at.isoformat(),
        'status': report.status
    })

@api_bp.route('/reports/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    """Delete a damage report"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first()
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        # Delete associated images if they exist
        if report.image_paths:
            image_paths = json.loads(report.image_paths)
            for image_path in image_paths:
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        
        # Delete the report from database
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to delete report: {str(e)}'
        }), 500

@api_bp.route('/statistics')
@login_required
def get_statistics():
    """Get user statistics"""
    total_reports = DamageReport.query.filter_by(user_id=current_user.id).count()
    
    # Average cost
    avg_cost = db.session.query(db.func.avg(DamageReport.estimated_cost))\
                        .filter_by(user_id=current_user.id).scalar() or 0
    
    # Most common vehicle type
    common_vehicle = db.session.query(DamageReport.vehicle_type, db.func.count(DamageReport.id))\
                              .filter_by(user_id=current_user.id)\
                              .group_by(DamageReport.vehicle_type)\
                              .order_by(db.func.count(DamageReport.id).desc())\
                              .first()
    
    return jsonify({
        'total_reports': total_reports,
        'average_cost': float(avg_cost),
        'most_common_vehicle': common_vehicle[0] if common_vehicle else None
    })

@api_bp.route('/test/nearby-shops')
def get_nearby_shops():
    """Get nearby repair shops based on location"""
    try:
        # Get parameters from request
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 10.0, type=float)
        vehicle_type = request.args.get('vehicle_type', 'Car')
        damage_type = request.args.get('damage_type')
        
        # Validate required parameters
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude are required'
            }), 400
        
        # Initialize repair shop finder
        shop_finder = RepairShopFinder()
        
        # Find nearby shops
        nearby_shops = shop_finder.find_nearby_shops(
            latitude=lat,
            longitude=lon,
            radius_km=radius,
            vehicle_type=vehicle_type,
            damage_type=damage_type
        )
        
        return jsonify({
            'success': True,
            'shops': nearby_shops,
            'count': len(nearby_shops),
            'location': {
                'latitude': lat,
                'longitude': lon,
                'radius_km': radius
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to find nearby shops: {str(e)}'
        }), 500
