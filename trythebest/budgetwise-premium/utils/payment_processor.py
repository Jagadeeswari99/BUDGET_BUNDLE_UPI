from datetime import datetime

class PaymentProcessor:
    """Advanced payment processing and validation"""
    
    def __init__(self, budget):
        self.budget = budget
        self.transaction_history = []
    
    def validate_payment(self, amount, bundle):
        """Validate if payment can be made from bundle"""
        if bundle == 'savings':
            return {
                'valid': False,
                'error': 'Cannot spend from protected savings!',
                'error_code': 'SAVINGS_PROTECTED'
            }
        
        remaining = self.budget.get(f'{bundle}_remaining', 0)
        
        if amount > remaining:
            return {
                'valid': False,
                'error': f'Insufficient balance. Only ₹{remaining:.0f} available.',
                'error_code': 'INSUFFICIENT_BALANCE',
                'balance': remaining
            }
        
        return {'valid': True, 'balance': remaining - amount}
    
    def process_payment(self, recipient, amount, bundle, note=''):
        """Process and record payment"""
        validation = self.validate_payment(amount, bundle)
        
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error'],
                'error_code': validation.get('error_code'),
                'timestamp': datetime.now()
            }
        
        transaction = {
            'recipient': recipient,
            'amount': amount,
            'bundle': bundle,
            'note': note,
            'timestamp': datetime.now(),
            'status': 'completed',
            'remaining_after': validation['balance'],
        }
        
        self.transaction_history.append(transaction)
        
        return {
            'success': True,
            'transaction': transaction,
            'message': f'✅ Payment of ₹{amount} to {recipient} successful!',
            'new_balance': validation['balance']
        }
    
    def get_low_balance_warnings(self):
        """Get warnings for low balance bundles"""
        warnings = []
        
        for bundle in ['meals', 'groceries', 'rent']:
            allocated = self.budget.get(bundle, 0)
            remaining = self.budget.get(f'{bundle}_remaining', 0)
            
            if remaining < (allocated * 0.1):  # Less than 10%
                warnings.append({
                    'bundle': bundle,
                    'remaining': remaining,
                    'warning_level': 'critical' if remaining < (allocated * 0.05) else 'warning',
                    'message': f'Only 10% left in {bundle} bundle!'
                })
        
        return warnings
    
    def calculate_daily_budget(self, bundle):
        """Calculate daily budget for remaining days"""
        from datetime import datetime
        
        allocated = self.budget.get(bundle, 0)
        remaining = self.budget.get(f'{bundle}_remaining', 0)
        
        today = datetime.now()
        days_left = (datetime(today.year, today.month, 1).replace(month=today.month % 12 + 1) - today).days
        
        daily_budget = remaining / days_left if days_left > 0 else 0
        
        return {
            'total_remaining': remaining,
            'days_left': days_left,
            'daily_budget': daily_budget,
            'recommendation': f'You can spend ₹{daily_budget:.0f} per day safely'
        }
