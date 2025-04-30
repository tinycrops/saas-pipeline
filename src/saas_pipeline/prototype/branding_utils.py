"""
Branding Utilities

Utilities for generating and validating branding elements
including name suggestions, color palettes, and messaging themes.
"""

import re
import random
import colorsys
from typing import Dict, Any, List, Optional, Tuple

# Pre-defined color palettes that follow color theory best practices
PREMADE_PALETTES = [
    {
        "primary": "#3498db",  # Blue
        "secondary": "#2ecc71",  # Green
        "accent": "#e74c3c",  # Red
        "background": "#f5f8fa",  # Light gray
        "text": "#2c3e50"  # Dark blue
    },
    {
        "primary": "#9b59b6",  # Purple
        "secondary": "#3498db",  # Blue
        "accent": "#f1c40f",  # Yellow
        "background": "#f9f9f9",  # Off-white
        "text": "#34495e"  # Dark gray
    },
    {
        "primary": "#e67e22",  # Orange
        "secondary": "#27ae60",  # Green
        "accent": "#8e44ad",  # Purple
        "background": "#faf9f7",  # Cream
        "text": "#2c3e50"  # Dark blue
    },
    {
        "primary": "#1abc9c",  # Teal
        "secondary": "#f39c12",  # Amber
        "accent": "#e74c3c",  # Red
        "background": "#f0f3f6",  # Light blue-gray
        "text": "#34495e"  # Dark gray
    },
    {
        "primary": "#d35400",  # Dark orange
        "secondary": "#2980b9",  # Blue
        "accent": "#2ecc71",  # Green
        "background": "#ecf0f1",  # Light gray
        "text": "#2c3e50"  # Dark blue
    }
]

# Common words to avoid in SaaS names (overused or generic)
OVERUSED_WORDS = [
    'app', 'cloud', 'swift', 'quick', 'fast', 'rapid', 'smart', 'intelligent',
    'tech', 'ware', 'solutions', 'tools', 'box', 'hub', 'sync', 'connect', 'boost',
    'power', 'pro', 'plus', 'premium', 'ultra', 'max', 'elite', 'prime', 'advanced'
]


class BrandingUtils:
    """
    Utilities for branding generation and validation.
    """
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, List[str]]:
        """
        Validate a potential product name.
        
        Args:
            name: Proposed product name
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check length
        if len(name) < 3:
            issues.append("Name is too short (less than 3 characters)")
        elif len(name) > 20:
            issues.append("Name may be too long (over 20 characters)")
        
        # Check for overused words
        for word in OVERUSED_WORDS:
            if word.lower() in name.lower():
                issues.append(f"Contains overused word '{word}'")
                break
        
        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9\-\_\.]*$', name):
            issues.append("Contains special characters that may be problematic for domains")
        
        # Check for common domain patterns
        if name.lower().endswith('app'):
            issues.append("Ends with 'app' which is very common and may have domain availability issues")
        
        if name.lower().startswith('get') or name.lower().startswith('try'):
            issues.append(f"Starts with '{name.lower()[:3]}' which is very common in SaaS domains")
        
        return (len(issues) == 0, issues)
    
    @staticmethod
    def generate_color_palette(base_hue: Optional[float] = None) -> Dict[str, str]:
        """
        Generate a cohesive color palette for branding.
        
        Args:
            base_hue: Optional hue value (0-1) to base the palette on
            
        Returns:
            Dictionary with color values
        """
        # Randomly select a pre-made palette 80% of the time
        if random.random() < 0.8 or base_hue is None:
            return random.choice(PREMADE_PALETTES)
        
        # Generate a custom palette based on color theory
        # Base hue is provided (0-1)
        primary_rgb = colorsys.hls_to_rgb(base_hue, 0.5, 1.0)
        # Complementary color (opposite on color wheel)
        secondary_hue = (base_hue + 0.5) % 1.0
        secondary_rgb = colorsys.hls_to_rgb(secondary_hue, 0.5, 0.8)
        # Accent using triadic relationship
        accent_hue = (base_hue + 0.33) % 1.0
        accent_rgb = colorsys.hls_to_rgb(accent_hue, 0.5, 1.0)
        
        # Convert to hex
        primary = '#{:02x}{:02x}{:02x}'.format(
            int(primary_rgb[0] * 255), 
            int(primary_rgb[1] * 255), 
            int(primary_rgb[2] * 255)
        )
        secondary = '#{:02x}{:02x}{:02x}'.format(
            int(secondary_rgb[0] * 255), 
            int(secondary_rgb[1] * 255), 
            int(secondary_rgb[2] * 255)
        )
        accent = '#{:02x}{:02x}{:02x}'.format(
            int(accent_rgb[0] * 255), 
            int(accent_rgb[1] * 255), 
            int(accent_rgb[2] * 255)
        )
        
        return {
            "primary": primary,
            "secondary": secondary,
            "accent": accent,
            "background": "#f8f9fa",  # Light gray-white
            "text": "#212529"  # Dark gray
        }
    
    @staticmethod
    def analyze_name_suggestions(suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of name suggestions for quality.
        
        Args:
            suggestions: List of name suggestion dictionaries
            
        Returns:
            Analysis results
        """
        results = {
            "total_suggestions": len(suggestions),
            "valid_count": 0,
            "issues_by_name": {},
            "top_recommendations": []
        }
        
        valid_names = []
        
        for suggestion in suggestions:
            name = suggestion.get('name', '')
            is_valid, issues = BrandingUtils.validate_name(name)
            
            if is_valid:
                results["valid_count"] += 1
                valid_names.append(suggestion)
            else:
                results["issues_by_name"][name] = issues
        
        # Pick top 3 recommendations from valid names
        results["top_recommendations"] = valid_names[:min(3, len(valid_names))]
        
        return results
    
    @staticmethod
    def suggest_domain_variations(name: str) -> List[str]:
        """
        Suggest domain name variations for a given product name.
        
        Args:
            name: Product name
            
        Returns:
            List of domain suggestions
        """
        # Remove spaces and special characters
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name)
        
        common_tlds = ['.com', '.io', '.app', '.co', '.ai']
        prefixes = ['get', 'try', 'use', 'join', '']
        suffixes = ['app', 'hq', '', 'ai']
        
        suggestions = []
        
        # Basic name with different TLDs
        for tld in common_tlds:
            suggestions.append(f"{clean_name.lower()}{tld}")
        
        # Prefix + name variations
        for prefix in prefixes:
            if prefix:  # Skip empty prefix to avoid duplicates
                for tld in common_tlds[:2]:  # Limit to top 2 TLDs
                    suggestions.append(f"{prefix}{clean_name.lower()}{tld}")
        
        # Name + suffix variations
        for suffix in suffixes:
            if suffix:  # Skip empty suffix to avoid duplicates
                for tld in common_tlds[:2]:  # Limit to top 2 TLDs
                    suggestions.append(f"{clean_name.lower()}{suffix}{tld}")
        
        # Remove duplicates
        return list(dict.fromkeys(suggestions))
    
    @staticmethod
    def generate_message_tone_examples(tone: str, target_audience: str) -> Dict[str, str]:
        """
        Generate example messages for a specific brand tone and audience.
        
        Args:
            tone: Desired brand tone (friendly, professional, technical, etc.)
            target_audience: Description of the target audience
            
        Returns:
            Dictionary with message examples for different contexts
        """
        examples = {}
        
        # Default professional tone examples
        examples["headline"] = "Streamline Your Workflow with Our Solution"
        examples["subheading"] = "Powerful tools designed for busy professionals."
        examples["call_to_action"] = "Get Started Today"
        examples["value_proposition"] = "Save time and reduce errors with our intuitive platform."
        
        # Adjust based on tone
        if tone.lower() == "friendly":
            examples["headline"] = "Hey there! Ready to make work easier?"
            examples["subheading"] = "We've built something awesome just for you."
            examples["call_to_action"] = "Let's Go!"
            examples["value_proposition"] = "Life's too short for busywork. We help you focus on what matters."
        
        elif tone.lower() == "technical":
            examples["headline"] = "Advanced Workflow Optimization Engine"
            examples["subheading"] = "Leveraging AI and machine learning to maximize efficiency."
            examples["call_to_action"] = "Deploy Now"
            examples["value_proposition"] = "Our proprietary algorithms deliver 43% improved throughput with 99.9% reliability."
        
        elif tone.lower() == "luxurious" or tone.lower() == "premium":
            examples["headline"] = "Elevate Your Experience"
            examples["subheading"] = "Exclusive tools for discerning professionals."
            examples["call_to_action"] = "Join the Elite"
            examples["value_proposition"] = "Unparalleled quality and attention to detail in every feature."
        
        elif tone.lower() == "playful" or tone.lower() == "fun":
            examples["headline"] = "Work Doesn't Have to Be Boring!"
            examples["subheading"] = "Who said productivity can't be fun?"
            examples["call_to_action"] = "Jump Right In!"
            examples["value_proposition"] = "We put the 'wow' in workflow (and make your job a whole lot easier)."
        
        # Customize for audience if needed
        if "developer" in target_audience.lower() or "technical" in target_audience.lower():
            examples["headline"] = f"Built by developers, for {target_audience}"
            
        elif "small business" in target_audience.lower():
            examples["value_proposition"] = "Enterprise-level tools tailored for small business budgets."
            
        return examples 