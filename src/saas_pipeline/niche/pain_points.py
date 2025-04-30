"""
Pain Point Identification and Analysis

This module provides functionality for extracting, categorizing, and analyzing pain points 
from niche research interview responses. It includes algorithms for identifying 
potential pain points in text, assessing their severity and impact, and visualizing
the results.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import math
from datetime import datetime

from .models import Response, PainPoint, Interview, Niche
from .repository import NicheRepository

logger = logging.getLogger(__name__)

# Common pain indicator phrases
PAIN_INDICATORS = [
    "frustrated with", "annoyed by", "hate", "dislike", "struggle with",
    "difficult to", "challenging", "time-consuming", "expensive", "waste",
    "inefficient", "confusing", "complicated", "problem with", "issue with",
    "hard to", "can't", "cannot", "wish", "if only", "tired of", "fed up",
    "painful", "annoying", "disappointing", "unreliable", "poor", "bad",
    "worried about", "concerned about", "fear", "afraid", "anxious about"
]

# Categories for pain point classification
DEFAULT_CATEGORIES = {
    "time": ["time", "slow", "wait", "delay", "hours", "days", "minutes", "wasted", "long", "quick", "fast"],
    "cost": ["money", "expensive", "price", "cost", "afford", "budget", "spend", "cheap", "pricing", "fee", "subscription"],
    "usability": ["confusing", "hard", "difficult", "complex", "understand", "learn", "interface", "user", "intuitive", "simple", "complicated"],
    "reliability": ["crash", "bug", "error", "fail", "downtime", "outage", "reliable", "stable", "consistent", "breaks", "broken"],
    "support": ["help", "support", "service", "customer", "response", "ticket", "chat", "contact", "email", "call", "documentation"],
    "integration": ["connect", "integrate", "sync", "api", "compatible", "work with", "import", "export", "third-party", "platform"],
    "performance": ["slow", "fast", "speed", "performance", "lag", "bandwidth", "resource", "memory", "cpu", "efficient"],
    "security": ["secure", "privacy", "data", "breach", "hack", "safe", "protect", "compliance", "sensitive", "security", "encryption"],
    "feature": ["missing", "feature", "function", "capability", "able to", "option", "setting", "control", "customize", "functionality"]
}


class PainPointAnalyzer:
    """Analyzes interview responses to identify and categorize pain points."""
    
    def __init__(self, repository: Optional[NicheRepository] = None, 
                 custom_indicators: Optional[List[str]] = None,
                 custom_categories: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the pain point analyzer.
        
        Args:
            repository: Repository for data persistence
            custom_indicators: Additional pain indicator phrases
            custom_categories: Custom pain point categories with keywords
        """
        self.repository = repository or NicheRepository()
        self.pain_indicators = PAIN_INDICATORS + (custom_indicators or [])
        self.categories = custom_categories or DEFAULT_CATEGORIES
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for pain indicators."""
        self.pain_patterns = [
            re.compile(r'\b' + re.escape(indicator) + r'\b', re.IGNORECASE)
            for indicator in self.pain_indicators
        ]
        
        self.category_patterns = {
            category: [
                re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                for keyword in keywords
            ]
            for category, keywords in self.categories.items()
        }
    
    def extract_pain_points_from_interview(self, interview_id: str) -> List[Dict[str, Any]]:
        """
        Extract potential pain points from an interview.
        
        Args:
            interview_id: ID of the interview to analyze
            
        Returns:
            List of potential pain points with metadata
        """
        interview = self.repository.get_interview(interview_id)
        if not interview:
            logger.warning(f"Interview {interview_id} not found")
            return []
        
        responses = self.repository.get_responses_by_interview(interview_id)
        
        pain_points = []
        for question_id, response in responses.items():
            points = self._extract_from_text(response.answer)
            for point in points:
                point["response_id"] = response.id
                point["question_id"] = question_id
                pain_points.append(point)
        
        return pain_points
    
    def _extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract potential pain points from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of potential pain points with metadata
        """
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        pain_points = []
        
        for sentence in sentences:
            # Check if sentence contains pain indicators
            pain_matches = [
                pattern.search(sentence) is not None
                for pattern in self.pain_patterns
            ]
            
            if any(pain_matches):
                # Analyze sentence for category and intensity
                category, confidence = self._categorize_text(sentence)
                severity, frequency, impact = self._estimate_metrics(sentence)
                
                pain_points.append({
                    "description": sentence,
                    "category": category,
                    "category_confidence": confidence,
                    "severity": severity,
                    "frequency": frequency,
                    "impact": impact,
                    "score": (severity + frequency + impact) / 3
                })
        
        return pain_points
    
    def _categorize_text(self, text: str) -> Tuple[str, float]:
        """
        Categorize pain point text into predefined categories.
        
        Args:
            text: Text to categorize
            
        Returns:
            Tuple of (category_name, confidence_score)
        """
        scores = {}
        
        for category, patterns in self.category_patterns.items():
            matches = [
                len(pattern.findall(text))
                for pattern in patterns
            ]
            score = sum(matches)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return "uncategorized", 0.0
        
        total = sum(scores.values())
        best_category = max(scores.items(), key=lambda x: x[1])
        confidence = best_category[1] / total if total > 0 else 0
        
        return best_category[0], min(confidence, 1.0)
    
    def _estimate_metrics(self, text: str) -> Tuple[int, int, int]:
        """
        Estimate severity, frequency, and impact from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (severity, frequency, impact) scores (1-5 scale)
        """
        # Severity indicators (words that suggest high severity)
        severity_indicators = {
            "very": 1, "extremely": 2, "always": 1, "constantly": 1, 
            "significant": 1, "major": 1, "critical": 2, "serious": 1,
            "huge": 1, "severe": 2, "terrible": 1, "awful": 1,
            "worst": 2, "impossible": 1, "unacceptable": 1
        }
        
        # Frequency indicators
        frequency_indicators = {
            "always": 2, "constantly": 2, "every time": 2, "daily": 1,
            "repeatedly": 1, "frequently": 1, "often": 1, "regularly": 1,
            "never": -1, "rarely": -1, "occasionally": -1, "sometimes": -1
        }
        
        # Impact indicators
        impact_indicators = {
            "wasting": 1, "lost": 1, "missing": 1, "costs": 1, "expensive": 1,
            "time": 1, "money": 1, "revenue": 2, "profit": 2, "customer": 1,
            "critical": 2, "essential": 1, "core": 1, "business": 1,
            "huge": 1, "significant": 1, "important": 1
        }
        
        # Calculate base scores
        severity_base = 3
        frequency_base = 3
        impact_base = 3
        
        text_lower = text.lower()
        
        # Adjust scores based on indicators
        for word, value in severity_indicators.items():
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                severity_base += value
        
        for word, value in frequency_indicators.items():
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                frequency_base += value
        
        for word, value in impact_indicators.items():
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                impact_base += value
        
        # Ensure scores are within 1-5 range
        severity = max(1, min(5, severity_base))
        frequency = max(1, min(5, frequency_base))
        impact = max(1, min(5, impact_base))
        
        return severity, frequency, impact
    
    def create_pain_points_for_niche(self, niche_id: str, threshold: float = 0.0) -> List[str]:
        """
        Analyze all interviews for a niche and create pain points.
        
        Args:
            niche_id: ID of the niche to analyze
            threshold: Minimum score threshold for pain points (0.0-5.0)
            
        Returns:
            List of created pain point IDs
        """
        niche = self.repository.get_niche(niche_id)
        if not niche:
            logger.warning(f"Niche {niche_id} not found")
            return []
        
        # Get all interviews for the niche
        interviews = self.repository.get_interviews_by_niche(niche_id)
        if not interviews:
            logger.warning(f"No interviews found for niche {niche_id}")
            return []
        
        # Extract pain points from all interviews
        all_points = []
        for interview in interviews:
            points = self.extract_pain_points_from_interview(interview.id)
            all_points.extend(points)
        
        # Filter by threshold and deduplicate
        filtered_points = [p for p in all_points if p["score"] >= threshold]
        if not filtered_points:
            logger.info(f"No pain points found above threshold {threshold}")
            return []
        
        # Group similar pain points
        grouped_points = self._group_similar_pain_points(filtered_points)
        
        # Create pain point objects and save to repository
        created_ids = []
        for group in grouped_points:
            # Use most representative pain point from group
            best_point = max(group, key=lambda x: x["score"])
            
            pain_point = PainPoint(
                description=best_point["description"],
                niche_id=niche_id,
                severity=best_point["severity"],
                frequency=best_point["frequency"],
                impact=best_point["impact"]
            )
            
            success = self.repository.save_pain_point(pain_point)
            if success:
                created_ids.append(pain_point.id)
        
        return created_ids
    
    def _group_similar_pain_points(self, points: List[Dict[str, Any]], 
                                   similarity_threshold: float = 0.7) -> List[List[Dict[str, Any]]]:
        """
        Group similar pain points together.
        
        Args:
            points: List of pain points to group
            similarity_threshold: Threshold for considering points similar (0.0-1.0)
            
        Returns:
            List of grouped pain points
        """
        if not points:
            return []
        
        # Simple implementation using text similarity
        groups = []
        remaining = points.copy()
        
        while remaining:
            current = remaining.pop(0)
            group = [current]
            
            i = 0
            while i < len(remaining):
                if self._calculate_similarity(current["description"], 
                                            remaining[i]["description"]) >= similarity_threshold:
                    group.append(remaining.pop(i))
                else:
                    i += 1
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple Jaccard similarity for tokens
        tokens1 = set(re.findall(r'\b\w+\b', text1.lower()))
        tokens2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    def analyze_pain_points(self, niche_id: str) -> Dict[str, Any]:
        """
        Analyze pain points for a niche and generate insights.
        
        Args:
            niche_id: ID of the niche to analyze
            
        Returns:
            Dictionary of analysis results
        """
        pain_points = self.repository.get_pain_points_by_niche(niche_id)
        if not pain_points:
            logger.warning(f"No pain points found for niche {niche_id}")
            return {"count": 0, "categories": {}, "severity": {}, "top": []}
        
        # Category distribution
        categories = Counter()
        for point in pain_points:
            category, _ = self._categorize_text(point.description)
            categories[category] += 1
        
        # Severity distribution
        severity_counts = Counter()
        for point in pain_points:
            severity_counts[point.severity] += 1
        
        # Calculate impact scores
        for point in pain_points:
            point.impact_score = (point.severity + point.frequency + point.impact) / 3
        
        # Sort by impact score
        sorted_points = sorted(pain_points, key=lambda p: p.severity * p.frequency * p.impact, reverse=True)
        
        # Top pain points
        top_points = [
            {
                "id": p.id,
                "description": p.description,
                "severity": p.severity,
                "frequency": p.frequency,
                "impact": p.impact,
                "score": p.severity * p.frequency * p.impact
            }
            for p in sorted_points[:5]  # Top 5
        ]
        
        return {
            "count": len(pain_points),
            "categories": dict(categories),
            "severity": {str(k): v for k, v in severity_counts.items()},
            "top": top_points
        }


class PainPointVisualizer:
    """Generate visualizations of pain point data."""
    
    def __init__(self, repository: Optional[NicheRepository] = None):
        """
        Initialize the pain point visualizer.
        
        Args:
            repository: Repository for data access
        """
        self.repository = repository or NicheRepository()
    
    def generate_heatmap_data(self, niche_id: str) -> Dict[str, Any]:
        """
        Generate data for a pain point heatmap.
        
        Args:
            niche_id: ID of the niche to visualize
            
        Returns:
            Dictionary of heatmap data
        """
        pain_points = self.repository.get_pain_points_by_niche(niche_id)
        if not pain_points:
            return {"points": []}
        
        analyzer = PainPointAnalyzer(self.repository)
        
        points = []
        for pain_point in pain_points:
            category, _ = analyzer._categorize_text(pain_point.description)
            points.append({
                "id": pain_point.id,
                "x": pain_point.frequency,  # x-axis: frequency
                "y": pain_point.severity,   # y-axis: severity
                "value": pain_point.impact, # intensity
                "category": category,
                "description": pain_point.description
            })
        
        return {
            "points": points,
            "x_axis": {"label": "Frequency", "min": 1, "max": 5},
            "y_axis": {"label": "Severity", "min": 1, "max": 5}
        }
    
    def generate_category_chart_data(self, niche_id: str) -> Dict[str, Any]:
        """
        Generate data for a pain point category chart.
        
        Args:
            niche_id: ID of the niche to visualize
            
        Returns:
            Dictionary of category chart data
        """
        pain_points = self.repository.get_pain_points_by_niche(niche_id)
        if not pain_points:
            return {"categories": []}
        
        analyzer = PainPointAnalyzer(self.repository)
        
        categories = defaultdict(list)
        for pain_point in pain_points:
            category, confidence = analyzer._categorize_text(pain_point.description)
            categories[category].append({
                "id": pain_point.id,
                "description": pain_point.description,
                "score": pain_point.severity * pain_point.frequency * pain_point.impact,
                "confidence": confidence
            })
        
        chart_data = []
        for category, points in categories.items():
            avg_score = sum(p["score"] for p in points) / len(points)
            chart_data.append({
                "category": category,
                "count": len(points),
                "average_score": avg_score,
                "items": points
            })
        
        return {
            "categories": sorted(chart_data, key=lambda x: x["count"], reverse=True)
        }
    
    def export_pain_point_report(self, niche_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive pain point report.
        
        Args:
            niche_id: ID of the niche to report on
            
        Returns:
            Dictionary with report data
        """
        niche = self.repository.get_niche(niche_id)
        if not niche:
            return {"error": f"Niche {niche_id} not found"}
        
        analyzer = PainPointAnalyzer(self.repository)
        analysis = analyzer.analyze_pain_points(niche_id)
        
        heatmap = self.generate_heatmap_data(niche_id)
        categories = self.generate_category_chart_data(niche_id)
        
        return {
            "niche": {
                "id": niche.id,
                "name": niche.name,
                "description": niche.description
            },
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_pain_points": analysis["count"],
                "categories": analysis["categories"],
                "severity_distribution": analysis["severity"]
            },
            "top_pain_points": analysis["top"],
            "visualizations": {
                "heatmap": heatmap,
                "categories": categories
            }
        }


def extract_pain_points_from_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Utility function to extract pain points from a single response text.
    
    Args:
        response_text: Text to analyze
        
    Returns:
        List of potential pain points with metadata
    """
    analyzer = PainPointAnalyzer()
    return analyzer._extract_from_text(response_text)


def analyze_niche_pain_points(niche_id: str) -> Dict[str, Any]:
    """
    Utility function to analyze pain points for a niche.
    
    Args:
        niche_id: ID of the niche to analyze
        
    Returns:
        Dictionary of analysis results
    """
    analyzer = PainPointAnalyzer()
    return analyzer.analyze_pain_points(niche_id) 