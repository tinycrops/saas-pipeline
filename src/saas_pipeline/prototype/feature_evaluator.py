"""
Feature Evaluator

Utility for analyzing and prioritizing features based on implementation
effort and business value. Helps in decision making for MVP features.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureEvaluator:
    """
    Utility class for evaluating features based on various criteria.
    """
    
    @staticmethod
    def calculate_priority_score(feature: Dict[str, Any]) -> float:
        """
        Calculate a priority score for a feature based on complexity and importance.
        
        Args:
            feature: Feature data including complexity
            
        Returns:
            Priority score (higher is higher priority)
        """
        # Default values if not provided
        complexity = feature.get('complexity', 3)
        importance = feature.get('importance', 3)
        
        # Normalize complexity to a 1-5 scale if needed
        try:
            complexity = min(5, max(1, int(complexity)))
        except (ValueError, TypeError):
            complexity = 3
            
        # Normalize importance to a 1-5 scale if needed
        try:
            importance = min(5, max(1, int(importance)))
        except (ValueError, TypeError):
            importance = 3
        
        # Calculate score: higher importance and lower complexity = higher score
        # Importance is weighted more heavily than complexity
        return (importance * 2) - complexity
    
    @staticmethod
    def prioritize_features(features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort features by priority score.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            Sorted list of features with priority scores added
        """
        # Add priority score to each feature
        for feature in features:
            feature['priority_score'] = FeatureEvaluator.calculate_priority_score(feature)
        
        # Sort by priority score (descending)
        return sorted(features, key=lambda x: x.get('priority_score', 0), reverse=True)
    
    @staticmethod
    def categorize_by_phase(features: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize features by implementation phase based on priority score.
        
        Args:
            features: List of feature dictionaries with priority scores
            
        Returns:
            Dictionary with features grouped by phase
        """
        prioritized = FeatureEvaluator.prioritize_features(features)
        
        # Divide features into phases
        feature_count = len(prioritized)
        phase1_count = max(1, int(feature_count * 0.3))  # ~30% in phase 1
        phase2_count = max(1, int(feature_count * 0.5))  # ~50% in phase 2
        
        phases = {
            "phase_1_mvp": prioritized[:phase1_count],
            "phase_2_growth": prioritized[phase1_count:phase1_count + phase2_count],
            "phase_3_scale": prioritized[phase1_count + phase2_count:]
        }
        
        return phases
    
    @staticmethod
    def evaluate_implementation_effort(features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the implementation effort for a set of features.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            Dictionary with effort metrics
        """
        total_complexity = sum(feature.get('complexity', 3) for feature in features)
        avg_complexity = total_complexity / len(features) if features else 0
        
        # Count features by complexity level
        complexity_breakdown = {
            "trivial": len([f for f in features if f.get('complexity', 3) == 1]),
            "easy": len([f for f in features if f.get('complexity', 3) == 2]),
            "medium": len([f for f in features if f.get('complexity', 3) == 3]),
            "hard": len([f for f in features if f.get('complexity', 3) == 4]),
            "very_hard": len([f for f in features if f.get('complexity', 3) == 5])
        }
        
        # Estimate development time based on complexity
        # These are rough estimates, adjust as needed
        time_multipliers = {
            1: 1,    # 1 day for trivial
            2: 3,    # 3 days for easy
            3: 7,    # 7 days for medium
            4: 14,   # 14 days for hard
            5: 30    # 30 days for very hard
        }
        
        estimated_days = sum(time_multipliers.get(feature.get('complexity', 3), 7) for feature in features)
        
        return {
            "feature_count": len(features),
            "total_complexity": total_complexity,
            "average_complexity": round(avg_complexity, 2),
            "complexity_breakdown": complexity_breakdown,
            "estimated_development_days": estimated_days
        }
    
    @staticmethod
    def analyze_technical_dependencies(features: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Identify common technical dependencies across features.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            Dictionary mapping technical categories to required technologies
        """
        # Keywords to look for in feature descriptions
        tech_keywords = {
            "auth": ["authentication", "login", "signup", "user account", "permission", "role"],
            "database": ["database", "storage", "persist", "save", "data model", "schema"],
            "api": ["api", "integration", "endpoint", "http", "rest", "graphql"],
            "realtime": ["realtime", "real-time", "websocket", "notification", "live update"],
            "file_handling": ["file", "upload", "download", "document", "attachment", "media"],
            "payment": ["payment", "subscription", "billing", "price", "checkout"],
            "ai": ["ai", "machine learning", "ml", "prediction", "analyze", "nlp", "recommendation"]
        }
        
        # Initialize results
        dependencies = {category: [] for category in tech_keywords.keys()}
        
        # Scan each feature description for keywords
        for feature in features:
            description = (feature.get('description', '') + ' ' + feature.get('title', '')).lower()
            
            for category, keywords in tech_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in description and category not in dependencies[category]:
                        dependencies[category].append(feature.get('title', 'Unnamed feature'))
                        break
        
        # Remove empty categories
        return {k: v for k, v in dependencies.items() if v}
    
    @staticmethod
    def suggest_mvp_scope(features: List[Dict[str, Any]], max_days: int = 60) -> Dict[str, Any]:
        """
        Suggest an optimal MVP scope based on implementation effort constraints.
        
        Args:
            features: List of feature dictionaries
            max_days: Maximum development time in days
            
        Returns:
            Dictionary with suggested MVP features and metrics
        """
        prioritized = FeatureEvaluator.prioritize_features(features)
        
        # Time multipliers for complexity levels
        time_multipliers = {
            1: 1,    # 1 day for trivial
            2: 3,    # 3 days for easy
            3: 7,    # 7 days for medium
            4: 14,   # 14 days for hard
            5: 30    # 30 days for very hard
        }
        
        # Build MVP scope within time constraint
        mvp_features = []
        total_days = 0
        
        for feature in prioritized:
            feature_days = time_multipliers.get(feature.get('complexity', 3), 7)
            
            if total_days + feature_days <= max_days:
                mvp_features.append(feature)
                total_days += feature_days
            else:
                # If we can't include this feature, consider if we can include any remaining
                # low-complexity features
                if feature.get('complexity', 3) <= 2 and total_days + feature_days <= max_days * 1.1:
                    mvp_features.append(feature)
                    total_days += feature_days
        
        # Evaluate the suggested MVP
        mvp_evaluation = FeatureEvaluator.evaluate_implementation_effort(mvp_features)
        
        return {
            "mvp_features": mvp_features,
            "excluded_features": [f for f in features if f not in mvp_features],
            "feature_count": len(mvp_features),
            "estimated_days": total_days,
            "evaluation": mvp_evaluation
        } 