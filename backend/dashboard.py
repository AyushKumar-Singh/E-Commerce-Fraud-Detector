"""
Admin Dashboard - Real-time fraud monitoring and labeling interface
"""

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from db.models import Review, Transaction, Label, User
from utils.auth import require_token

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
@require_token
def get_stats():
    """Get real-time fraud statistics"""
    from app import get_db
    db = get_db()
    
    now = datetime.utcnow()
    
    # Time ranges
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Review stats
    review_stats = {
        "today": {
            "total": db.query(func.count(Review.id)).filter(
                func.date(Review.created_at) == today
            ).scalar() or 0,
            "flagged": db.query(func.count(Review.id)).filter(
                func.date(Review.created_at) == today,
                Review.is_fake_pred == True
            ).scalar() or 0
        },
        "week": {
            "total": db.query(func.count(Review.id)).filter(
                Review.created_at >= week_ago
            ).scalar() or 0,
            "flagged": db.query(func.count(Review.id)).filter(
                Review.created_at >= week_ago,
                Review.is_fake_pred == True
            ).scalar() or 0
        },
        "month": {
            "total": db.query(func.count(Review.id)).filter(
                Review.created_at >= month_ago
            ).scalar() or 0,
            "flagged": db.query(func.count(Review.id)).filter(
                Review.created_at >= month_ago,
                Review.is_fake_pred == True
            ).scalar() or 0
        }
    }
    
    # Transaction stats
    tx_stats = {
        "today": {
            "total": db.query(func.count(Transaction.id)).filter(
                func.date(Transaction.created_at) == today
            ).scalar() or 0,
            "flagged": db.query(func.count(Transaction.id)).filter(
                func.date(Transaction.created_at) == today,
                Transaction.is_fraud_pred == True
            ).scalar() or 0,
            "total_amount": float(db.query(func.sum(Transaction.amount)).filter(
                func.date(Transaction.created_at) == today
            ).scalar() or 0),
            "flagged_amount": float(db.query(func.sum(Transaction.amount)).filter(
                func.date(Transaction.created_at) == today,
                Transaction.is_fraud_pred == True
            ).scalar() or 0)
        },
        "week": {
            "total": db.query(func.count(Transaction.id)).filter(
                Transaction.created_at >= week_ago
            ).scalar() or 0,
            "flagged": db.query(func.count(Transaction.id)).filter(
                Transaction.created_at >= week_ago,
                Transaction.is_fraud_pred == True
            ).scalar() or 0
        },
        "month": {
            "total": db.query(func.count(Transaction.id)).filter(
                Transaction.created_at >= month_ago
            ).scalar() or 0,
            "flagged": db.query(func.count(Transaction.id)).filter(
                Transaction.created_at >= month_ago,
                Transaction.is_fraud_pred == True
            ).scalar() or 0
        }
    }
    
    return jsonify({
        "reviews": review_stats,
        "transactions": tx_stats,
        "timestamp": now.isoformat()
    })

@dashboard_bp.route('/api/trends')
@require_token
def get_trends():
    """Get daily fraud trends for charts"""
    from app import get_db
    db = get_db()
    
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Review trends
    review_trends = db.query(
        func.date(Review.created_at).label('date'),
        func.count(Review.id).label('total'),
        func.sum(func.cast(Review.is_fake_pred, db.Integer)).label('flagged'),
        func.avg(Review.fake_score).label('avg_score')
    ).filter(
        Review.created_at >= start_date
    ).group_by(
        func.date(Review.created_at)
    ).order_by('date').all()
    
    # Transaction trends
    tx_trends = db.query(
        func.date(Transaction.created_at).label('date'),
        func.count(Transaction.id).label('total'),
        func.sum(func.cast(Transaction.is_fraud_pred, db.Integer)).label('flagged'),
        func.avg(Transaction.fraud_score).label('avg_score'),
        func.sum(Transaction.amount).label('total_amount')
    ).filter(
        Transaction.created_at >= start_date
    ).group_by(
        func.date(Transaction.created_at)
    ).order_by('date').all()
    
    return jsonify({
        "reviews": [
            {
                "date": str(r.date),
                "total": r.total,
                "flagged": r.flagged or 0,
                "avg_score": round(float(r.avg_score or 0), 3),
                "flag_rate": round((r.flagged or 0) / r.total * 100, 1) if r.total > 0 else 0
            }
            for r in review_trends
        ],
        "transactions": [
            {
                "date": str(t.date),
                "total": t.total,
                "flagged": t.flagged or 0,
                "avg_score": round(float(t.avg_score or 0), 3),
                "flag_rate": round((t.flagged or 0) / t.total * 100, 1) if t.total > 0 else 0,
                "total_amount": float(t.total_amount or 0)
            }
            for t in tx_trends
        ]
    })

@dashboard_bp.route('/api/top-offenders')
@require_token
def get_top_offenders():
    """Get top flagged IPs, devices, and users"""
    from app import get_db
    db = get_db()
    
    limit = int(request.args.get('limit', 10))
    
    # Top flagged IPs (reviews)
    top_ips = db.query(
        Review.ip_address,
        func.count(Review.id).label('total'),
        func.sum(func.cast(Review.is_fake_pred, db.Integer)).label('flagged')
    ).filter(
        Review.ip_address.isnot(None),
        Review.created_at >= datetime.utcnow() - timedelta(days=7)
    ).group_by(
        Review.ip_address
    ).order_by(
        desc('flagged')
    ).limit(limit).all()
    
    # Top flagged devices
    top_devices = db.query(
        Review.device_fingerprint,
        func.count(Review.id).label('total'),
        func.sum(func.cast(Review.is_fake_pred, db.Integer)).label('flagged')
    ).filter(
        Review.device_fingerprint.isnot(None),
        Review.created_at >= datetime.utcnow() - timedelta(days=7)
    ).group_by(
        Review.device_fingerprint
    ).order_by(
        desc('flagged')
    ).limit(limit).all()
    
    # Top flagged users (transactions)
    top_users = db.query(
        Transaction.user_id,
        User.email,
        func.count(Transaction.id).label('total'),
        func.sum(func.cast(Transaction.is_fraud_pred, db.Integer)).label('flagged'),
        func.sum(Transaction.amount).label('total_amount')
    ).join(
        User, Transaction.user_id == User.id
    ).filter(
        Transaction.created_at >= datetime.utcnow() - timedelta(days=7)
    ).group_by(
        Transaction.user_id, User.email
    ).order_by(
        desc('flagged')
    ).limit(limit).all()
    
    return jsonify({
        "ips": [
            {
                "ip": str(ip.ip_address),
                "total": ip.total,
                "flagged": ip.flagged or 0,
                "flag_rate": round((ip.flagged or 0) / ip.total * 100, 1)
            }
            for ip in top_ips
        ],
        "devices": [
            {
                "device": d.device_fingerprint[:16] + "...",
                "total": d.total,
                "flagged": d.flagged or 0,
                "flag_rate": round((d.flagged or 0) / d.total * 100, 1)
            }
            for d in top_devices
        ],
        "users": [
            {
                "user_id": u.user_id,
                "email": u.email,
                "total": u.total,
                "flagged": u.flagged or 0,
                "total_amount": float(u.total_amount or 0),
                "flag_rate": round((u.flagged or 0) / u.total * 100, 1)
            }
            for u in top_users
        ]
    })

@dashboard_bp.route('/api/recent-flags')
@require_token
def get_recent_flags():
    """Get recently flagged items for review"""
    from app import get_db
    db = get_db()
    
    entity_type = request.args.get('type', 'review')
    limit = int(request.args.get('limit', 20))
    
    if entity_type == 'review':
        items = db.query(Review).filter(
            Review.is_fake_pred == True
        ).order_by(
            desc(Review.created_at)
        ).limit(limit).all()
        
        return jsonify({
            "items": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "product_id": r.product_id,
                    "text": r.review_text[:200] + "..." if len(r.review_text) > 200 else r.review_text,
                    "rating": float(r.rating),
                    "score": float(r.fake_score),
                    "reasons": r.decision_json.get('reasons', []) if r.decision_json else [],
                    "created_at": r.created_at.isoformat(),
                    "ip": str(r.ip_address) if r.ip_address else None
                }
                for r in items
            ]
        })
    else:
        items = db.query(Transaction).filter(
            Transaction.is_fraud_pred == True
        ).order_by(
            desc(Transaction.created_at)
        ).limit(limit).all()
        
        return jsonify({
            "items": [
                {
                    "id": t.id,
                    "user_id": t.user_id,
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "score": float(t.fraud_score),
                    "reasons": t.decision_json.get('reasons', []) if t.decision_json else [],
                    "created_at": t.created_at.isoformat(),
                    "ip": str(t.ip_address) if t.ip_address else None,
                    "channel": t.channel
                }
                for t in items
            ]
        })

@dashboard_bp.route('/api/label', methods=['POST'])
@require_token
def add_label():
    """Add human label for feedback loop"""
    from app import get_db
    db = get_db()
    
    data = request.get_json()
    
    label = Label(
        entity_type=data['entity_type'],
        entity_id=data['entity_id'],
        is_fraud=data['is_fraud'],
        notes=data.get('notes'),
        labeled_by=data.get('labeled_by', 'admin')
    )
    
    db.add(label)
    db.commit()
    
    return jsonify({"success": True, "label_id": label.id})