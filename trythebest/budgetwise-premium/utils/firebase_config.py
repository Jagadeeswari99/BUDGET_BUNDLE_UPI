import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import os
import json

# Initialize Firebase
try:
    cred = credentials.Certificate('firebase-key.json')
except FileNotFoundError:
    firebase_json = os.getenv('FIREBASE_KEY_JSON')
    if firebase_json:
        cred = credentials.Certificate(json.loads(firebase_json))
    else:
        cred = None

if cred:
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    db = None

# ==================== USER OPERATIONS ====================

def create_user(user_id, email, name):
    """Create new user profile"""
    try:
        if not db:
            return True
        
        db.collection('users').document(user_id).set({
            'email': email,
            'name': name,
            'created_at': datetime.now(),
            'emergency_fund': 0,
            'savings_goal': 0,
            'spending_habits': {},
            'notifications_enabled': True,
        })
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user_profile(user_id):
    """Get user profile"""
    try:
        if not db:
            return {'name': 'Demo User', 'emergency_fund': 2870}
        
        doc = db.collection('users').document(user_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

# ==================== BUDGET OPERATIONS ====================

def create_budget(user_id, month, budget_data):
    """Create monthly budget"""
    try:
        if not db:
            return True
        
        db.collection('budgets').document(user_id).collection('monthly').document(month).set({
            'monthly_income': budget_data['income'],
            'meals': budget_data['meals'],
            'groceries': budget_data['groceries'],
            'rent': budget_data['rent'],
            'savings': budget_data['savings'],
            'meals_remaining': budget_data['meals'],
            'groceries_remaining': budget_data['groceries'],
            'rent_remaining': budget_data['rent'],
            'savings_remaining': budget_data['savings'],
            'created_at': datetime.now(),
            'month': month,
            'alerts_sent': 0,
        })
        return True
    except Exception as e:
        print(f"Error creating budget: {e}")
        return False

def get_budget(user_id, month):
    """Get monthly budget"""
    try:
        if not db:
            return {
                'monthly_income': 45000,
                'meals': 8000,
                'groceries': 6000,
                'rent': 25000,
                'savings': 6000,
                'meals_remaining': 7800,
                'groceries_remaining': 5920,
                'rent_remaining': 25000,
                'savings_remaining': 6000,
            }
        
        doc = db.collection('budgets').document(user_id).collection('monthly').document(month).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error fetching budget: {e}")
        return None

def update_budget_remaining(user_id, month, bundle, new_amount):
    """Update remaining amount in bundle"""
    try:
        if not db:
            return True
        
        field_name = f'{bundle}_remaining'
        db.collection('budgets').document(user_id).collection('monthly').document(month).update({
            field_name: new_amount
        })
        return True
    except Exception as e:
        print(f"Error updating budget: {e}")
        return False

# ==================== TRANSACTION OPERATIONS ====================

def record_transaction(user_id, month, transaction_data):
    """Record a transaction"""
    try:
        if not db:
            return True
        
        db.collection('transactions').document(user_id).collection('records').add({
            'recipient': transaction_data['recipient'],
            'amount': transaction_data['amount'],
            'bundle': transaction_data['bundle'],
            'note': transaction_data.get('note', ''),
            'timestamp': datetime.now(),
            'month': month,
            'status': 'completed',
            'upi_id': transaction_data.get('upi_id', ''),
            'category': transaction_data.get('category', transaction_data['bundle']),
        })
        return True
    except Exception as e:
        print(f"Error recording transaction: {e}")
        return False

def get_transactions(user_id, month):
    """Get all transactions for a month"""
    try:
        if not db:
            return [
                {'recipient': 'Starbucks', 'amount': 200, 'bundle': 'meals', 'timestamp': datetime.now() - timedelta(hours=2), 'status': 'completed'},
                {'recipient': 'DMart', 'amount': 80, 'bundle': 'groceries', 'timestamp': datetime.now() - timedelta(days=1), 'status': 'completed'},
            ]
        
        docs = db.collection('transactions').document(user_id).collection('records').where('month', '==', month).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []

def get_spending_by_category(user_id, month):
    """Get spending breakdown by category"""
    try:
        transactions = get_transactions(user_id, month)
        breakdown = {'meals': 0, 'groceries': 0, 'rent': 0}
        
        for trans in transactions:
            bundle = trans.get('bundle', '')
            if bundle in breakdown:
                breakdown[bundle] += trans.get('amount', 0)
        
        return breakdown
    except Exception as e:
        print(f"Error getting spending breakdown: {e}")
        return {'meals': 0, 'groceries': 0, 'rent': 0}

# ==================== ANALYTICS ====================

def get_monthly_stats(user_id, month):
    """Get monthly statistics"""
    try:
        budget = get_budget(user_id, month)
        transactions = get_transactions(user_id, month)
        
        if not budget:
            return None
        
        return {
            'total_income': budget['monthly_income'],
            'total_allocated': budget['meals'] + budget['groceries'] + budget['rent'] + budget['savings'],
            'total_spent': sum(t['amount'] for t in transactions),
            'total_remaining': (budget['meals_remaining'] + budget['groceries_remaining'] + 
                              budget['rent_remaining'] + budget['savings_remaining']),
            'transaction_count': len(transactions),
            'bundles_used': len([b for b in ['meals', 'groceries', 'rent'] 
                                if budget[f'{b}_remaining'] < budget[b]]),
        }
    except Exception as e:
        print(f"Error getting monthly stats: {e}")
        return None

def get_spending_trend(user_id, months=3):
    """Get spending trend over multiple months"""
    try:
        trends = []
        today = datetime.now()
        
        for i in range(months):
            month = (today - timedelta(days=30*i)).strftime('%Y-%m')
            stats = get_monthly_stats(user_id, month)
            if stats:
                trends.append({'month': month, **stats})
        
        return trends
    except Exception as e:
        print(f"Error getting spending trend: {e}")
        return []

# ==================== EMERGENCY FUND ====================

def get_emergency_fund(user_id):
    """Get emergency fund balance"""
    try:
        if not db:
            return 2870.0
        
        doc = db.collection('users').document(user_id).get()
        return doc.get('emergency_fund', 0.0) if doc.exists else 0.0
    except Exception as e:
        print(f"Error fetching emergency fund: {e}")
        return 0.0

def add_to_emergency_fund(user_id, amount):
    """Add to emergency fund"""
    try:
        if not db:
            return True
        
        current = get_emergency_fund(user_id)
        db.collection('users').document(user_id).set({
            'emergency_fund': current + amount,
            'emergency_fund_updated': datetime.now(),
        }, merge=True)
        return True
    except Exception as e:
        print(f"Error updating emergency fund: {e}")
        return False

# ==================== SAVINGS GOALS ====================

def set_savings_goal(user_id, goal_amount, goal_name):
    """Set a savings goal"""
    try:
        if not db:
            return True
        
        db.collection('users').document(user_id).collection('goals').add({
            'name': goal_name,
            'target_amount': goal_amount,
            'current_amount': 0,
            'created_at': datetime.now(),
            'status': 'active',
        })
        return True
    except Exception as e:
        print(f"Error setting goal: {e}")
        return False

def get_savings_goals(user_id):
    """Get all savings goals"""
    try:
        if not db:
            return [
                {'name': 'Vacation', 'target_amount': 50000, 'current_amount': 15000, 'id': '1', 'status': 'active'},
                {'name': 'New Laptop', 'target_amount': 100000, 'current_amount': 45000, 'id': '2', 'status': 'active'},
            ]
        
        docs = db.collection('users').document(user_id).collection('goals').where('status', '==', 'active').stream()
        goals = []
        for doc in docs:
            goal_data = doc.to_dict()
            goal_data['id'] = doc.id
            goals.append(goal_data)
        return goals
    except Exception as e:
        print(f"Error fetching goals: {e}")
        return []

def update_goal_progress(user_id, goal_id, amount):
    """Update goal progress by adding amount"""
    try:
        if not db:
            return True
        
        goal_ref = db.collection('users').document(user_id).collection('goals').document(goal_id)
        goal = goal_ref.get()
        if goal.exists:
            current = goal.get('current_amount', 0)
            goal_ref.update({'current_amount': current + amount})
            return True
        return False
    except Exception as e:
        print(f"Error updating goal progress: {e}")
        return False

def delete_savings_goal(user_id, goal_id):
    """Delete a savings goal"""
    try:
        if not db:
            return True
        
        db.collection('users').document(user_id).collection('goals').document(goal_id).update({
            'status': 'deleted',
            'deleted_at': datetime.now(),
        })
        return True
    except Exception as e:
        print(f"Error deleting goal: {e}")
        return False

def update_transaction_bundle(user_id, month, transaction_id, new_bundle):
    """Update transaction bundle after categorization"""
    try:
        if not db:
            return True
        
        db.collection('transactions').document(transaction_id).update({
            'bundle': new_bundle,
            'status': 'categorized',
            'categorized_at': datetime.now(),
        })
        return True
    except Exception as e:
        print(f"Error updating transaction: {e}")
        return False

# ==================== CUSTOM BUNDLES ====================

def get_user_bundles(user_id):
    """Get custom bundles created by user"""
    try:
        if not db:
            return []
        
        docs = db.collection('users').document(user_id).collection('custom_bundles').stream()
        bundles = []
        for doc in docs:
            bundle_data = doc.to_dict()
            bundle_data['id'] = doc.id
            bundles.append(bundle_data)
        return bundles
    except Exception as e:
        print(f"Error fetching custom bundles: {e}")
        return []

def create_custom_bundle(user_id, bundle_name, emoji='📦'):
    """Create a custom bundle"""
    try:
        if not db:
            return True
        
        db.collection('users').document(user_id).collection('custom_bundles').add({
            'name': bundle_name,
            'emoji': emoji,
            'created_at': datetime.now(),
            'active': True,
        })
        return True
    except Exception as e:
        print(f"Error creating custom bundle: {e}")
        return False
