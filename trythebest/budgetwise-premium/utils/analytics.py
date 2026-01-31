import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedAnalytics:
    """Advanced analytics for spending patterns"""
    
    def __init__(self, transactions, budget):
        self.transactions = transactions
        self.budget = budget
    
    def get_spending_insights(self):
        """Get intelligent spending insights"""
        insights = []
        
        # Insight 1: Overspending alert
        for bundle in ['meals', 'groceries', 'rent']:
            allocated = self.budget.get(bundle, 0)
            remaining = self.budget.get(f'{bundle}_remaining', 0)
            spent = allocated - remaining
            percentage = (spent / allocated * 100) if allocated > 0 else 0
            
            if percentage > 90:
                insights.append({
                    'type': 'warning',
                    'bundle': bundle,
                    'message': f'⚠️ {bundle.title()} is 90%+ spent!',
                    'action': 'Reduce spending or adjust budget'
                })
        
        # Insight 2: Savings progress
        savings_remaining = self.budget.get('savings_remaining', 0)
        savings_allocated = self.budget.get('savings', 0)
        if savings_remaining == savings_allocated:
            insights.append({
                'type': 'success',
                'message': '💚 Great! You haven\'t touched savings this month!',
                'action': 'Keep protecting your emergency fund'
            })
        
        # Insight 3: Spending pattern
        if len(self.transactions) > 0:
            avg_transaction = sum(t['amount'] for t in self.transactions) / len(self.transactions)
            insights.append({
                'type': 'info',
                'message': f'📊 Average transaction: ₹{avg_transaction:.0f}',
                'action': f'You made {len(self.transactions)} transactions this month'
            })
        
        return insights
    
    def predict_savings(self):
        """Predict potential savings"""
        total_remaining = (self.budget.get('meals_remaining', 0) +
                          self.budget.get('groceries_remaining', 0) +
                          self.budget.get('rent_remaining', 0))
        
        return {
            'current_remaining': total_remaining,
            'potential_emergency_fund': total_remaining,
            'savings_percentage': (total_remaining / self.budget.get('monthly_income', 1) * 100)
        }
    
    def get_budget_health_score(self):
        """Calculate budget health score (0-100)"""
        score = 100
        
        # Deduct for overspending
        for bundle in ['meals', 'groceries', 'rent']:
            allocated = self.budget.get(bundle, 0)
            remaining = self.budget.get(f'{bundle}_remaining', 0)
            spent = allocated - remaining
            percentage = (spent / allocated * 100) if allocated > 0 else 0
            
            if percentage > 100:
                score -= 10
            elif percentage > 90:
                score -= 5
        
        # Add points for savings protection
        if self.budget.get('savings_remaining') == self.budget.get('savings'):
            score += 10
        
        return max(0, min(100, score))
    
    def get_recommendations(self):
        """Get AI-like recommendations"""
        recommendations = []
        
        health_score = self.get_budget_health_score()
        
        if health_score < 50:
            recommendations.append("🔴 Your budget health is low. Consider reducing spending.")
        elif health_score < 75:
            recommendations.append("🟡 Your budget could be better. Focus on one category.")
        else:
            recommendations.append("🟢 Excellent budget management! Keep it up!")
        
        # Check for specific issues
        meals_spent = self.budget.get('meals', 0) - self.budget.get('meals_remaining', 0)
        if meals_spent > 0:
            avg_meal = meals_spent / len([t for t in self.transactions if t['bundle'] == 'meals']) if any(t['bundle'] == 'meals' for t in self.transactions) else 0
            if avg_meal > 300:
                recommendations.append("💡 Your average meal cost is high. Try cooking at home?")
        
        return recommendations
