"""
Report generation routes and functionality
"""

from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from database_models import db, DamageReport
from report_generator import ReportGenerator
import json
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/generate/<int:report_id>')
@login_required
def generate_report(report_id):
    """Generate PDF report for a damage assessment"""
    try:
        report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
        
        # Load image paths
        image_paths = json.loads(report.image_paths) if report.image_paths else []
        
        # Generate PDF report
        report_generator = ReportGenerator()
        pdf_data = report_generator.generate_pdf_report(report, image_paths)
        
        # Create response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=damage_report_{report_id}.pdf'
        
        return response
        
    except Exception as e:
        # Log the error
        print(f"Error generating PDF for report {report_id}: {str(e)}")
        
        # Return error response
        return jsonify({
            'error': 'Failed to generate PDF report',
            'message': str(e)
        }), 500

@reports_bp.route('/generate/<int:report_id>', methods=['POST'])
@login_required
def print_report(report_id):
    """Prepare report for printing"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    
    return jsonify({
        'success': True,
        'message': 'Report ready for printing',
        'print_url': f"/reports/view/{report_id}"
    })

@reports_bp.route('/view/<int:report_id>')
@login_required
def view_report(report_id):
    """View HTML report for a damage assessment"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    
    # Load image paths
    image_paths = json.loads(report.image_paths) if report.image_paths else []
    
    # Parse JSON fields for template
    affected_areas = json.loads(report.affected_areas) if report.affected_areas else []
    cost_breakdown = json.loads(report.cost_breakdown) if report.cost_breakdown else {}
    recommendations = json.loads(report.recommendations) if report.recommendations else []
    
    return render_template('reports/view.html', 
                         report=report, 
                         image_paths=image_paths,
                         affected_areas=affected_areas,
                         cost_breakdown=cost_breakdown,
                         recommendations=recommendations)

@reports_bp.route('/view/<int:report_id>', methods=['POST'])
@login_required
def share_report(report_id):
    """Share report and generate shareable URL"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    
    # Generate shareable URL (in a real app, this would be a unique token)
    share_url = f"{request.host_url}reports/view/{report_id}"
    
    return jsonify({
        'success': True,
        'share_url': share_url,
        'message': 'Report shared successfully'
    })

@reports_bp.route('/api/export/<int:report_id>')
@login_required
def export_report(report_id):
    """Export report data as JSON"""
    report = DamageReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    
    # Load image paths
    image_paths = json.loads(report.image_paths) if report.image_paths else []
    
    report_data = {
        'id': report.id,
        'vehicle_type': report.vehicle_type,
        'damage_type': report.damage_type,
        'severity': report.severity,
        'estimated_cost': report.estimated_cost,
        'confidence_score': report.confidence_score,
        'created_at': report.created_at.isoformat(),
        'status': report.status,
        'image_paths': image_paths
    }
    
    return jsonify(report_data)

@reports_bp.route('/api/summary')
@login_required
def get_summary():
    """Get summary statistics for user's damage reports"""
    total_reports = DamageReport.query.filter_by(user_id=current_user.id).count()
    
    # Get reports by status
    completed_reports = DamageReport.query.filter_by(user_id=current_user.id, status='completed').count()
    approved_reports = DamageReport.query.filter_by(user_id=current_user.id, status='approved').count()
    rejected_reports = DamageReport.query.filter_by(user_id=current_user.id, status='rejected').count()
    
    # Get total estimated cost
    total_cost = db.session.query(db.func.sum(DamageReport.estimated_cost))\
                          .filter_by(user_id=current_user.id).scalar() or 0
    
    # Get most common damage types
    damage_types = db.session.query(DamageReport.damage_type, db.func.count(DamageReport.id))\
                            .filter_by(user_id=current_user.id)\
                            .group_by(DamageReport.damage_type)\
                            .order_by(db.func.count(DamageReport.id).desc())\
                            .limit(5).all()
    
    summary = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'total_estimated_cost': float(total_cost),
        'common_damage_types': [{'type': dt[0], 'count': dt[1]} for dt in damage_types]
    }
    
    return jsonify(summary)
