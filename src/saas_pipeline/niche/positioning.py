"""
Positioning Statement Generator

This module provides functionality for generating compelling positioning statements
based on identified pain points and niche characteristics. It includes templates,
algorithms for matching pain points with appropriate positioning approaches, and
A/B testing capabilities.
"""

import re
import logging
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from datetime import datetime

from .models import PainPoint, PositioningStatement, Niche
from .repository import NicheRepository
from .pain_points import PainPointAnalyzer

logger = logging.getLogger(__name__)

# Positioning statement templates
POSITIONING_TEMPLATES = [
    # Value proposition format
    "For {target_audience} who {pain_point}, {product_name} is a {solution_category} that {solution_benefit}. Unlike {competitor}, {product_name} {unique_advantage}.",
    
    # Problem-solution format
    "{target_audience} struggle with {pain_point}. {product_name} solves this by {solution_benefit}, ensuring that {value_outcome}.",
    
    # Benefit-focused format
    "{product_name} helps {target_audience} {solution_benefit}, eliminating the {pain_point} that has been holding them back.",
    
    # Transformation format
    "Transform how {target_audience} {current_situation} with {product_name}. Stop {pain_point} and start {value_outcome}.",
    
    # Question-answer format
    "Are you a {target_audience} tired of {pain_point}? {product_name} {solution_benefit}, so you can finally {value_outcome}."
]

# Tone options for positioning statements
TONE_OPTIONS = {
    "professional": {
        "adjectives": ["effective", "reliable", "proven", "advanced", "sophisticated", "robust", "comprehensive"],
        "verbs": ["enables", "provides", "delivers", "offers", "enhances", "optimizes", "streamlines"]
    },
    "friendly": {
        "adjectives": ["easy", "simple", "helpful", "handy", "straightforward", "intuitive", "delightful"],
        "verbs": ["helps", "lets you", "makes it easy to", "saves you", "frees you to", "gives you", "takes care of"]
    },
    "technical": {
        "adjectives": ["powerful", "efficient", "precise", "cutting-edge", "high-performance", "innovative", "scalable"],
        "verbs": ["processes", "analyzes", "integrates", "calculates", "automates", "accelerates", "optimizes"]
    },
    "bold": {
        "adjectives": ["revolutionary", "game-changing", "groundbreaking", "disruptive", "unparalleled", "exceptional", "extraordinary"],
        "verbs": ["transforms", "revolutionizes", "disrupts", "redefines", "elevates", "dominates", "outperforms"]
    },
    "empathetic": {
        "adjectives": ["thoughtful", "supportive", "understanding", "caring", "considerate", "responsive", "attentive"],
        "verbs": ["understands", "addresses", "solves", "reduces", "alleviates", "eases", "removes"]
    }
}


class PositioningGenerator:
    """Generate positioning statements based on pain points and niche characteristics."""
    
    def __init__(self, repository: Optional[NicheRepository] = None,
                 custom_templates: Optional[List[str]] = None):
        """
        Initialize the positioning generator.
        
        Args:
            repository: Repository for data persistence
            custom_templates: Additional positioning statement templates
        """
        self.repository = repository or NicheRepository()
        self.templates = custom_templates or POSITIONING_TEMPLATES
        self.pain_point_analyzer = PainPointAnalyzer(self.repository)
    
    def generate_positioning_for_niche(self, niche_id: str, product_name: str,
                                      tone: str = "professional",
                                      competitor: Optional[str] = None,
                                      num_variations: int = 3) -> List[Dict[str, Any]]:
        """
        Generate positioning statements for a niche.
        
        Args:
            niche_id: ID of the niche
            product_name: Name of the product or service
            tone: Tone for the positioning statement
            competitor: Main competitor name (if applicable)
            num_variations: Number of variations to generate
            
        Returns:
            List of positioning statement dictionaries
        """
        # Get the niche and its pain points
        niche = self.repository.get_niche(niche_id)
        if not niche:
            logger.warning(f"Niche {niche_id} not found")
            return []
        
        pain_points = self.repository.get_pain_points_by_niche(niche_id)
        if not pain_points:
            logger.warning(f"No pain points found for niche {niche_id}")
            return []
        
        # Sort pain points by impact score (severity * frequency * impact)
        sorted_points = sorted(
            pain_points, 
            key=lambda p: p.severity * p.frequency * p.impact,
            reverse=True
        )
        
        # Generate positioning variations
        variations = []
        for i in range(min(num_variations, len(self.templates))):
            # Pick different templates for variations
            template_index = i % len(self.templates)
            template = self.templates[template_index]
            
            # Pick a top pain point (with some randomness)
            # First variation uses top pain point, others may use different ones
            pain_point_index = 0 if i == 0 else min(i, len(sorted_points) - 1)
            pain_point = sorted_points[pain_point_index]
            
            # Generate the positioning statement
            positioning = self._generate_positioning(
                niche, pain_point, product_name, template, tone, competitor
            )
            
            if positioning:
                variations.append(positioning)
        
        return variations
    
    def _generate_positioning(self, niche: Niche, pain_point: PainPoint,
                             product_name: str, template: str, tone: str,
                             competitor: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a positioning statement using the provided template and data.
        
        Args:
            niche: Niche object
            pain_point: Pain point object
            product_name: Name of the product
            template: Positioning statement template
            tone: Tone for the statement
            competitor: Main competitor name
            
        Returns:
            Dictionary with positioning data
        """
        try:
            # Determine the target audience
            target_audience = niche.target_audience or f"{niche.name} users"
            
            # Get the category of the pain point
            category, _ = self.pain_point_analyzer._categorize_text(pain_point.description)
            
            # Determine solution category based on pain point category
            solution_category = self._get_solution_category(category)
            
            # Generate solution benefit based on pain point
            solution_benefit = self._generate_solution_benefit(pain_point.description, tone)
            
            # Generate unique advantage
            unique_advantage = self._generate_unique_advantage(tone)
            
            # Generate value outcome
            value_outcome = self._generate_value_outcome(pain_point.description, tone)
            
            # Current situation (for transformation format)
            current_situation = self._extract_current_situation(pain_point.description)
            
            # Format the pain point description for use in templates
            pain_point_desc = self._format_pain_point_for_template(pain_point.description)
            
            # Use a generic competitor if none specified
            competitor_name = competitor or "existing solutions"
            
            # Fill in the template
            statement = template.format(
                target_audience=target_audience,
                pain_point=pain_point_desc,
                product_name=product_name,
                solution_category=solution_category,
                solution_benefit=solution_benefit,
                competitor=competitor_name,
                unique_advantage=unique_advantage,
                value_outcome=value_outcome,
                current_situation=current_situation
            )
            
            # Create a positioning statement object
            positioning = PositioningStatement(
                statement=statement,
                target_audience=target_audience,
                niche_id=niche.id
            )
            positioning.add_pain_point(pain_point.id)
            
            # Save the positioning statement
            success = self.repository.save_positioning_statement(positioning)
            if not success:
                logger.error(f"Failed to save positioning statement")
                return None
            
            return {
                "id": positioning.id,
                "statement": statement,
                "target_audience": target_audience,
                "pain_point_id": pain_point.id,
                "template_type": self._identify_template_type(template),
                "tone": tone
            }
            
        except KeyError as e:
            logger.error(f"Missing placeholder in template: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating positioning statement: {str(e)}")
            return None
    
    def _get_solution_category(self, pain_category: str) -> str:
        """Map pain point category to solution category."""
        category_map = {
            "time": "time-saving solution",
            "cost": "cost-effective solution",
            "usability": "user-friendly platform",
            "reliability": "reliable service",
            "support": "supportive system",
            "integration": "seamless integration platform",
            "performance": "high-performance tool",
            "security": "secure solution",
            "feature": "feature-rich platform",
            "uncategorized": "comprehensive solution"
        }
        return category_map.get(pain_category, "innovative solution")
    
    def _generate_solution_benefit(self, pain_point_desc: str, tone: str) -> str:
        """Generate a solution benefit based on pain point."""
        # Get adjectives and verbs for the selected tone
        adjectives = TONE_OPTIONS.get(tone, TONE_OPTIONS["professional"])["adjectives"]
        verbs = TONE_OPTIONS.get(tone, TONE_OPTIONS["professional"])["verbs"]
        
        # Pick random adjective and verb
        adjective = random.choice(adjectives)
        verb = random.choice(verbs)
        
        # Generate solution benefit based on pain point
        if "time" in pain_point_desc.lower() or "slow" in pain_point_desc.lower():
            return f"{verb} an {adjective} way to save time and increase productivity"
        elif "expensive" in pain_point_desc.lower() or "cost" in pain_point_desc.lower():
            return f"{verb} an {adjective} solution to reduce costs and maximize value"
        elif "confusing" in pain_point_desc.lower() or "complicated" in pain_point_desc.lower():
            return f"{verb} an {adjective} interface that simplifies complex processes"
        elif "integrat" in pain_point_desc.lower() or "connect" in pain_point_desc.lower():
            return f"{verb} {adjective} integration with your existing tools and workflows"
        else:
            return f"{verb} an {adjective} solution to address your specific needs"
    
    def _generate_unique_advantage(self, tone: str) -> str:
        """Generate a unique advantage statement."""
        advantages = {
            "professional": [
                "offers comprehensive capabilities designed specifically for your industry",
                "provides enterprise-grade reliability with intuitive usability",
                "delivers measurable results through proven methodologies",
                "combines powerful analytics with actionable insights"
            ],
            "friendly": [
                "makes the whole process enjoyable and stress-free",
                "feels like it was designed specifically for you",
                "fits perfectly into your daily workflow",
                "takes the frustration out of the equation"
            ],
            "technical": [
                "leverages advanced algorithms to maximize efficiency",
                "utilizes cutting-edge technology for superior results",
                "employs distributed architecture for unmatched performance",
                "features proprietary optimization techniques"
            ],
            "bold": [
                "completely reimagines what's possible in this space",
                "shatters industry limitations with breakthrough technology",
                "delivers results that competitors can't even approach",
                "represents a quantum leap in capability"
            ],
            "empathetic": [
                "is designed with a deep understanding of your challenges",
                "focuses on what truly matters to you and your team",
                "adapts to your unique situation and needs",
                "provides the support you've been looking for"
            ]
        }
        
        tone_advantages = advantages.get(tone, advantages["professional"])
        return random.choice(tone_advantages)
    
    def _generate_value_outcome(self, pain_point_desc: str, tone: str) -> str:
        """Generate a value outcome based on pain point."""
        # Common positive outcomes based on tone
        outcomes = {
            "professional": [
                "achieve your objectives more efficiently",
                "optimize your resources effectively",
                "increase productivity and performance",
                "realize measurable improvements"
            ],
            "friendly": [
                "enjoy a stress-free experience",
                "love the results you see",
                "smile at how easy everything becomes",
                "feel confident and in control"
            ],
            "technical": [
                "leverage maximum performance from your systems",
                "achieve optimal efficiency in all operations",
                "utilize resources with precision",
                "implement technical solutions seamlessly"
            ],
            "bold": [
                "revolutionize your entire approach",
                "leapfrog the competition",
                "achieve unprecedented results",
                "transform your capabilities overnight"
            ],
            "empathetic": [
                "find the relief you've been seeking",
                "finally overcome the challenges you've faced",
                "experience the support you deserve",
                "feel understood and valued"
            ]
        }
        
        tone_outcomes = outcomes.get(tone, outcomes["professional"])
        return random.choice(tone_outcomes)
    
    def _extract_current_situation(self, pain_point_desc: str) -> str:
        """Extract current situation from pain point description."""
        # Convert pain point into a current situation
        pain_point_lower = pain_point_desc.lower()
        
        if "time" in pain_point_lower or "slow" in pain_point_lower:
            return "manage their time"
        elif "cost" in pain_point_lower or "expensive" in pain_point_lower:
            return "handle their budget"
        elif "confus" in pain_point_lower or "difficult" in pain_point_lower:
            return "navigate complex processes"
        elif "integrat" in pain_point_lower or "connect" in pain_point_lower:
            return "connect their tools and systems"
        elif "support" in pain_point_lower or "help" in pain_point_lower:
            return "get the help they need"
        else:
            # Extract verbs and objects from the pain point for a more specific current situation
            # This is a simplistic approach - in a real system, NLP processing would be better
            words = pain_point_desc.split()
            if len(words) >= 3:
                # Take key parts of the pain point to form a general action
                return " ".join(words[1:min(4, len(words))])
            else:
                return "deal with daily challenges"
    
    def _format_pain_point_for_template(self, pain_point_desc: str) -> str:
        """Format pain point description for use in templates."""
        # Remove any periods at the end
        desc = pain_point_desc.rstrip('.')
        
        # Convert to lowercase if the entire string is uppercase
        if desc.isupper():
            desc = desc.lower()
        
        # Ensure it starts with lowercase for integration into sentences
        if desc and desc[0].isupper():
            desc = desc[0].lower() + desc[1:]
        
        # If it's a complete sentence, extract the key pain point
        if len(desc.split()) > 8 and any(s in desc.lower() for s in ["is", "are", "be", "have"]):
            # Find main phrases with pain indicators
            pain_indicators = ["frustrated", "annoyed", "hate", "dislike", "struggle", 
                             "difficult", "challenging", "time-consuming", "expensive", 
                             "waste", "inefficient", "confusing", "complicated", "problem"]
            
            for indicator in pain_indicators:
                if indicator in desc.lower():
                    # Find the context around the indicator
                    parts = desc.lower().split(indicator)
                    if len(parts) > 1:
                        # Take words around the indicator
                        context = indicator + parts[1].split('.')[0]
                        if len(context.split()) > 2:
                            return context.strip()
        
        return desc
    
    def _identify_template_type(self, template: str) -> str:
        """Identify the type of template used."""
        if "who {pain_point}" in template and "Unlike {competitor}" in template:
            return "value_proposition"
        elif "struggle with {pain_point}" in template:
            return "problem_solution"
        elif "eliminating the {pain_point}" in template:
            return "benefit_focused"
        elif "Transform how" in template:
            return "transformation"
        elif "tired of {pain_point}?" in template:
            return "question_answer"
        else:
            return "custom"
    
    def create_ab_test(self, niche_id: str, product_name: str, 
                       num_variations: int = 2) -> Dict[str, Any]:
        """
        Create an A/B test with multiple positioning statement variations.
        
        Args:
            niche_id: ID of the niche
            product_name: Name of the product or service
            num_variations: Number of variations to test
            
        Returns:
            Dictionary with A/B test data
        """
        # Generate variations with different tones and templates
        variations = []
        
        # Use different tones for variations
        tones = list(TONE_OPTIONS.keys())
        
        for i in range(min(num_variations, len(tones))):
            tone = tones[i]
            tone_variations = self.generate_positioning_for_niche(
                niche_id, product_name, tone=tone, num_variations=1
            )
            variations.extend(tone_variations)
        
        if not variations:
            logger.warning(f"Could not generate any positioning variations")
            return {"success": False, "error": "No positioning variations generated"}
        
        # Create an A/B test record
        ab_test = {
            "id": str(random.randint(100000, 999999)),  # Simple ID generation
            "niche_id": niche_id,
            "product_name": product_name,
            "created_at": datetime.now().isoformat(),
            "variations": variations,
            "results": {var["id"]: {"impressions": 0, "conversions": 0} for var in variations}
        }
        
        # In a real system, we would save this to a database
        # For now, just return the test data
        return {
            "success": True,
            "test": ab_test
        }
    
    def refine_positioning(self, positioning_id: str, feedback: str) -> Optional[Dict[str, Any]]:
        """
        Refine a positioning statement based on feedback.
        
        Args:
            positioning_id: ID of the positioning statement to refine
            feedback: Feedback to incorporate
            
        Returns:
            Dictionary with the refined positioning data
        """
        # Get the existing positioning statement
        positioning = self.repository.get_positioning_statement(positioning_id)
        if not positioning:
            logger.warning(f"Positioning statement {positioning_id} not found")
            return None
        
        # Get associated pain point and niche
        if not positioning.pain_point_ids:
            logger.warning(f"Positioning statement {positioning_id} has no associated pain points")
            return None
        
        pain_point = self.repository.get_pain_point(positioning.pain_point_ids[0])
        niche = self.repository.get_niche(positioning.niche_id)
        
        if not pain_point or not niche:
            logger.warning(f"Associated pain point or niche not found")
            return None
        
        # Analyze feedback for refinement direction
        refined_statement = self._refine_statement_with_feedback(
            positioning.statement, feedback
        )
        
        # Create a new refined positioning statement
        refined = PositioningStatement(
            statement=refined_statement,
            target_audience=positioning.target_audience,
            niche_id=positioning.niche_id
        )
        
        # Copy associated pain points
        for pain_point_id in positioning.pain_point_ids:
            refined.add_pain_point(pain_point_id)
        
        # Save the refined positioning statement
        success = self.repository.save_positioning_statement(refined)
        if not success:
            logger.error(f"Failed to save refined positioning statement")
            return None
        
        return {
            "id": refined.id,
            "statement": refined_statement,
            "target_audience": refined.target_audience,
            "original_id": positioning_id,
            "feedback": feedback
        }
    
    def _refine_statement_with_feedback(self, original: str, feedback: str) -> str:
        """
        Refine a positioning statement based on specific feedback.
        
        Args:
            original: Original positioning statement
            feedback: Feedback to incorporate
            
        Returns:
            Refined positioning statement
        """
        refined = original
        
        # Check for common feedback patterns and apply appropriate refinements
        feedback_lower = feedback.lower()
        
        if "shorter" in feedback_lower or "concise" in feedback_lower:
            # Make the statement more concise
            refined = self._make_more_concise(original)
        
        elif "specific" in feedback_lower or "details" in feedback_lower:
            # Make the statement more specific
            refined = self._make_more_specific(original)
        
        elif "simpler" in feedback_lower or "clearer" in feedback_lower:
            # Simplify the language
            refined = self._simplify_language(original)
        
        elif "stronger" in feedback_lower or "compelling" in feedback_lower:
            # Make the statement more compelling
            refined = self._make_more_compelling(original)
        
        elif "benefit" in feedback_lower or "value" in feedback_lower:
            # Emphasize benefits more
            refined = self._emphasize_benefits(original)
        
        # Implement other refinement strategies based on feedback...
        
        return refined
    
    def _make_more_concise(self, statement: str) -> str:
        """Make a positioning statement more concise."""
        # Remove unnecessary adjectives
        for filler in ["very", "really", "quite", "extremely", "that is", "which is"]:
            statement = statement.replace(f" {filler} ", " ")
        
        # Split into sentences and keep only the essential ones
        sentences = [s.strip() for s in re.split(r'[.!?]', statement) if s.strip()]
        if len(sentences) > 1:
            # Keep only the first 1-2 most important sentences
            important_sentences = [sentences[0]]
            if len(sentences) > 2 and len(sentences[1]) < len(sentences[0]):
                important_sentences.append(sentences[1])
            
            statement = ". ".join(important_sentences) + "."
        
        return statement
    
    def _make_more_specific(self, statement: str) -> str:
        """Make a positioning statement more specific."""
        # Replace generic terms with more specific ones
        replacements = {
            "solution": ["platform", "system", "toolkit", "framework", "service"],
            "good": ["effective", "reliable", "high-quality", "superior"],
            "better": ["faster", "more reliable", "more intuitive", "more powerful"],
            "helps": ["enables", "empowers", "facilitates", "accelerates"],
            "great": ["exceptional", "outstanding", "excellent", "premium"]
        }
        
        for generic, specifics in replacements.items():
            if f" {generic} " in statement.lower():
                statement = statement.replace(
                    f" {generic} ", 
                    f" {random.choice(specifics)} ", 
                    1  # Replace only the first occurrence
                )
        
        return statement
    
    def _simplify_language(self, statement: str) -> str:
        """Simplify the language of a positioning statement."""
        # Replace complex words with simpler alternatives
        complex_words = {
            "utilize": "use",
            "implementation": "setup",
            "functionality": "features",
            "methodology": "method",
            "leverage": "use",
            "facilitate": "help",
            "endeavor": "try",
            "commence": "start",
            "terminate": "end",
            "subsequent": "later",
            "ascertain": "find out",
            "in order to": "to"
        }
        
        for complex_word, simple_word in complex_words.items():
            statement = re.sub(
                r'\b' + re.escape(complex_word) + r'\b', 
                simple_word, 
                statement, 
                flags=re.IGNORECASE
            )
        
        return statement
    
    def _make_more_compelling(self, statement: str) -> str:
        """Make a positioning statement more compelling."""
        # Replace weak verbs with stronger ones
        weak_to_strong = {
            "helps": ["transforms", "revolutionizes", "supercharges"],
            "improves": ["maximizes", "elevates", "amplifies"],
            "makes": ["ensures", "guarantees", "delivers"],
            "good": ["exceptional", "outstanding", "remarkable"],
            "better": ["superior", "unmatched", "best-in-class"]
        }
        
        for weak, strong_options in weak_to_strong.items():
            if f" {weak} " in statement.lower():
                statement = statement.replace(
                    f" {weak} ", 
                    f" {random.choice(strong_options)} ", 
                    1  # Replace only the first occurrence
                )
        
        return statement
    
    def _emphasize_benefits(self, statement: str) -> str:
        """Emphasize the benefits in a positioning statement."""
        # Add a benefit-focused appendix if not already present
        if "so you can" not in statement.lower() and "enabling you to" not in statement.lower():
            benefit_phrases = [
                "so you can focus on what matters most",
                "enabling you to achieve better results in less time",
                "helping you stay ahead of the competition",
                "allowing you to maximize your potential",
                "freeing you from unnecessary constraints"
            ]
            
            # Add the benefit at the end of the first sentence
            sentences = [s.strip() for s in re.split(r'[.!?]', statement) if s.strip()]
            if sentences:
                first_sentence = sentences[0]
                other_sentences = sentences[1:] if len(sentences) > 1 else []
                
                benefit = random.choice(benefit_phrases)
                statement = f"{first_sentence}, {benefit}."
                
                if other_sentences:
                    statement += " " + " ".join(other_sentences) + "."
        
        return statement


def generate_positioning_statement(niche_id: str, product_name: str, 
                                  tone: str = "professional") -> Optional[Dict[str, Any]]:
    """
    Utility function to generate a positioning statement for a niche.
    
    Args:
        niche_id: ID of the niche
        product_name: Name of the product or service
        tone: Tone for the statement
        
    Returns:
        Positioning statement dictionary
    """
    generator = PositioningGenerator()
    variations = generator.generate_positioning_for_niche(
        niche_id, product_name, tone=tone, num_variations=1
    )
    
    if variations:
        return variations[0]
    else:
        return None


def create_ab_test_for_niche(niche_id: str, product_name: str, 
                            num_variations: int = 3) -> Dict[str, Any]:
    """
    Utility function to create an A/B test for positioning statements.
    
    Args:
        niche_id: ID of the niche
        product_name: Name of the product or service
        num_variations: Number of variations to test
        
    Returns:
        A/B test data dictionary
    """
    generator = PositioningGenerator()
    return generator.create_ab_test(niche_id, product_name, num_variations=num_variations) 