"""
Admin routes and functionality
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database_models import db, User, DamageReport, RepairShop
from datetime import datetime, timedelta
import json
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            if request.path.startswith('/admin/api/'):
                return jsonify({'error': 'Admin access required'}), 403
            else:
                flash('Admin access required', 'error')
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Get statistics
    total_users = User.query.count()
    total_reports = DamageReport.query.count()
    total_shops = RepairShop.query.count()
    
    # Recent reports (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_reports = DamageReport.query.filter(DamageReport.created_at >= week_ago).count()
    
    # Reports by status
    pending_reports = DamageReport.query.filter_by(status='pending').count()
    approved_reports = DamageReport.query.filter_by(status='approved').count()
    rejected_reports = DamageReport.query.filter_by(status='rejected').count()
    
    # Reports by severity
    minor_reports = DamageReport.query.filter_by(severity='01-minor').count()
    moderate_reports = DamageReport.query.filter_by(severity='02-moderate').count()
    severe_reports = DamageReport.query.filter_by(severity='03-severe').count()
    
    # Average cost
    avg_cost = db.session.query(db.func.avg(DamageReport.estimated_cost)).scalar() or 0
    
    # Recent users (last 7 days)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    
    # Recent damage reports
    recent_damage_reports = DamageReport.query.order_by(DamageReport.created_at.desc()).limit(10).all()
    
    # Vehicle types data for chart
    vehicle_types = db.session.query(DamageReport.vehicle_type, db.func.count(DamageReport.id)).group_by(DamageReport.vehicle_type).all()
    vehicle_types_data = {vt[0]: vt[1] for vt in vehicle_types}
    
    # Damage types data for chart
    damage_types = db.session.query(DamageReport.damage_type, db.func.count(DamageReport.id)).group_by(DamageReport.damage_type).all()
    damage_types_data = {dt[0]: dt[1] for dt in damage_types}
    
    stats = {
        'total_users': total_users,
        'total_reports': total_reports,
        'total_shops': total_shops,
        'recent_reports': recent_reports,
        'recent_users': recent_users,
        'pending_reports': pending_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'minor_reports': minor_reports,
        'moderate_reports': moderate_reports,
        'severe_reports': severe_reports,
        'avg_cost': float(avg_cost)
    }
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_reports=total_reports,
                         total_shops=total_shops,
                         recent_reports=recent_reports,
                         recent_users=recent_users,
                         pending_reports=pending_reports,
                         approved_reports=approved_reports,
                         rejected_reports=rejected_reports,
                         minor_reports=minor_reports,
                         moderate_reports=moderate_reports,
                         severe_reports=severe_reports,
                         avg_cost=float(avg_cost),
                         recent_damage_reports=recent_damage_reports,
                         vehicle_types_data=vehicle_types_data,
                         damage_types_data=damage_types_data)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail page"""
    user = User.query.get_or_404(user_id)
    reports = DamageReport.query.filter_by(user_id=user_id).order_by(DamageReport.created_at.desc()).all()
    
    return render_template('admin/user_detail.html', user=user, reports=reports)

@admin_bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_admin': user.is_admin,
        'message': f'User {"promoted to" if user.is_admin else "removed from"} admin'
    })

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's damage reports and associated images
    reports = DamageReport.query.filter_by(user_id=user_id).all()
    for report in reports:
        if report.image_paths:
            try:
                image_paths = json.loads(report.image_paths)
                for image_path in image_paths:
                    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
            except:
                pass
        db.session.delete(report)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Damage reports management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', 'all')
    
    query = DamageReport.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    reports = query.order_by(DamageReport.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/reports.html', reports=reports, status_filter=status_filter)

@admin_bp.route('/reports/<int:report_id>')
@login_required
@admin_required
def report_detail(report_id):
    """Damage report detail page"""
    report = DamageReport.query.get_or_404(report_id)
    user = User.query.get(report.user_id)
    
    # Parse image paths
    image_paths = []
    if report.image_paths:
        try:
            image_paths = json.loads(report.image_paths)
        except:
            pass
    
    # Parse JSON fields for template
    affected_areas = json.loads(report.affected_areas) if report.affected_areas else []
    cost_breakdown = json.loads(report.cost_breakdown) if report.cost_breakdown else {}
    recommendations = json.loads(report.recommendations) if report.recommendations else []
    
    return render_template('admin/report_detail.html', 
                         report=report, 
                         user=user, 
                         image_paths=image_paths,
                         affected_areas=affected_areas,
                         cost_breakdown=cost_breakdown,
                         recommendations=recommendations)

@admin_bp.route('/reports/<int:report_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_report_status(report_id):
    """Update damage report status"""
    report = DamageReport.query.get_or_404(report_id)
    data = request.get_json()
    
    new_status = data.get('status')
    if new_status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    report.status = new_status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'status': new_status,
        'message': f'Report status updated to {new_status}'
    })

@admin_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    """Delete a damage report"""
    report = DamageReport.query.get_or_404(report_id)
    
    # Delete associated images
    if report.image_paths:
        try:
            image_paths = json.loads(report.image_paths)
            for image_path in image_paths:
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        except:
            pass
    
    db.session.delete(report)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Report deleted successfully'})

@admin_bp.route('/shops')
@login_required
@admin_required
def shops():
    """Repair shops management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    shops = RepairShop.query.order_by(RepairShop.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/shops.html', shops=shops)

@admin_bp.route('/shops/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_shop():
    """Add new repair shop"""
    if request.method == 'POST':
        data = request.get_json()
        
        shop = RepairShop(
            name=data['name'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode'],
            phone=data['phone'],
            email=data.get('email'),
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            services=json.dumps(data.get('services', [])),
            rating=float(data.get('rating', 0))
        )
        
        db.session.add(shop)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Shop added successfully'})
    
    return render_template('admin/add_shop.html')

@admin_bp.route('/shops/<int:shop_id>')
@login_required
@admin_required
def shop_detail(shop_id):
    """Repair shop detail page"""
    shop = RepairShop.query.get_or_404(shop_id)
    
    # Parse services
    services = []
    if shop.services:
        try:
            services = json.loads(shop.services)
        except:
            pass
    
    return render_template('admin/shop_detail.html', shop=shop, services=services)

@admin_bp.route('/shops/<int:shop_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_shop(shop_id):
    """Edit repair shop"""
    shop = RepairShop.query.get_or_404(shop_id)
    
    if request.method == 'POST':
        data = request.get_json()
        
        shop.name = data['name']
        shop.address = data['address']
        shop.city = data['city']
        shop.state = data['state']
        shop.pincode = data['pincode']
        shop.phone = data['phone']
        shop.email = data.get('email')
        shop.latitude = float(data.get('latitude', 0))
        shop.longitude = float(data.get('longitude', 0))
        shop.services = json.dumps(data.get('services', []))
        shop.rating = float(data.get('rating', 0))
        shop.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Shop updated successfully'})
    
    # Parse services for editing
    services = []
    if shop.services:
        try:
            services = json.loads(shop.services)
        except:
            pass
    
    return render_template('admin/edit_shop.html', shop=shop, services=services)

@admin_bp.route('/shops/<int:shop_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_shop_status(shop_id):
    """Toggle shop active status"""
    shop = RepairShop.query.get_or_404(shop_id)
    shop.is_active = not shop.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_active': shop.is_active,
        'message': f'Shop {"activated" if shop.is_active else "deactivated"}'
    })

@admin_bp.route('/shops/<int:shop_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_shop(shop_id):
    """Delete repair shop"""
    shop = RepairShop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Shop deleted successfully'})

@admin_bp.route('/api/debug')
@login_required
def api_debug():
    """Debug endpoint to check user status"""
    return jsonify({
        'is_authenticated': current_user.is_authenticated,
        'is_admin': getattr(current_user, 'is_admin', False),
        'email': current_user.email if current_user.is_authenticated else None,
        'user_id': current_user.id if current_user.is_authenticated else None
    })

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for admin statistics"""
    # Get statistics
    total_users = User.query.count()
    total_reports = DamageReport.query.count()
    total_shops = RepairShop.query.count()
    
    # Recent reports (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_reports = DamageReport.query.filter(DamageReport.created_at >= week_ago).count()
    
    # Reports by status
    pending_reports = DamageReport.query.filter_by(status='pending').count()
    approved_reports = DamageReport.query.filter_by(status='approved').count()
    rejected_reports = DamageReport.query.filter_by(status='rejected').count()
    
    # Reports by severity
    minor_reports = DamageReport.query.filter_by(severity='01-minor').count()
    moderate_reports = DamageReport.query.filter_by(severity='02-moderate').count()
    severe_reports = DamageReport.query.filter_by(severity='03-severe').count()
    
    # Average cost
    avg_cost = db.session.query(db.func.avg(DamageReport.estimated_cost)).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'total_reports': total_reports,
        'total_shops': total_shops,
        'recent_reports': recent_reports,
        'pending_reports': pending_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'minor_reports': minor_reports,
        'moderate_reports': moderate_reports,
        'severe_reports': severe_reports,
        'avg_cost': float(avg_cost)
    })
