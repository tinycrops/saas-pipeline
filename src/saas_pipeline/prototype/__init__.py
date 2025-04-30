"""
Prototype Builder Module

This module provides functionality for feature selection, MVP design guidance,
and branding inspiration based on niche research data.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

from ..utils import read_json, write_json, ensure_directory
from ..api_client import OpenAIClient

# Import utilities
from .feature_evaluator import FeatureEvaluator
from .branding_utils import BrandingUtils
from .mvp_utils import MVPUtils

logger = logging.getLogger(__name__)


class PrototypeBuilderModule:
    """
    Module for SaaS prototype design, including feature selection,
    MVP guidance, and branding inspiration.
    """
    
    def __init__(self, openai_client: OpenAIClient):
        """
        Initialize the prototype builder module.
        
        Args:
            openai_client: OpenAI client for AI-powered analysis
        """
        self.openai_client = openai_client
        self.data_dir = "data/prototypes"
        ensure_directory(self.data_dir)
    
    def design_prototype(self, 
                        idea: str, 
                        niche_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete prototype design including features, MVP guidance, and branding.
        
        Args:
            idea: Brief description of the SaaS idea
            niche_data: Optional niche research data to inform the design
            
        Returns:
            Dictionary with complete prototype design
        """
        # Generate unique ID for the prototype
        prototype_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # If no niche data is provided, create a basic structure
        if niche_data is None:
            niche_data = {
                "name": "Generic SaaS",
                "pain_points": []
            }
            
        # Generate each component of the prototype
        features = self.select_features(idea, niche_data)
        mvp_guidance = self.generate_mvp_guidance(idea, features, niche_data)
        branding = self.generate_branding_inspiration(idea, niche_data)
        first_use = self.generate_first_use_experience(idea, features)
        
        # Additional analysis using utilities
        feature_analysis = self._analyze_features(features)
        tech_recommendations = MVPUtils.recommend_tech_stack(features)
        implementation_phases = MVPUtils.generate_implementation_phases(features)
        key_metrics = MVPUtils.recommend_key_metrics(features)
        
        # Assemble the complete prototype
        prototype = {
            "id": prototype_id,
            "idea": idea,
            "niche": niche_data.get("name", "Generic SaaS"),
            "created_at": created_at,
            "features": features,
            "feature_analysis": feature_analysis,
            "mvp_guidance": mvp_guidance,
            "implementation_phases": implementation_phases,
            "tech_recommendations": tech_recommendations,
            "key_metrics": key_metrics,
            "branding": branding,
            "first_use_experience": first_use
        }
        
        # Save the prototype
        self._save_prototype(prototype)
        
        return prototype
    
    def _analyze_features(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze features using the FeatureEvaluator.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            Analysis results
        """
        prioritized = FeatureEvaluator.prioritize_features(features)
        phased_features = FeatureEvaluator.categorize_by_phase(features)
        effort_analysis = FeatureEvaluator.evaluate_implementation_effort(features)
        mvp_scope = FeatureEvaluator.suggest_mvp_scope(features)
        technical_dependencies = FeatureEvaluator.analyze_technical_dependencies(features)
        
        return {
            "prioritized_features": prioritized,
            "phased_features": phased_features,
            "effort_analysis": effort_analysis,
            "suggested_mvp_scope": mvp_scope,
            "technical_dependencies": technical_dependencies
        }
    
    def select_features(self, idea: str, niche_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate feature recommendations based on the idea and niche research.
        
        Args:
            idea: Brief description of the SaaS idea
            niche_data: Niche research data
            
        Returns:
            List of feature recommendations with rationale
        """
        # Extract pain points from niche data if available
        pain_points = []
        if "pain_points" in niche_data and niche_data["pain_points"]:
            pain_points = [p.get("description", "") for p in niche_data["pain_points"]]
        
        # Prepare prompt for API
        prompt = [
            {"role": "system", "content": """You are a SaaS product strategist specialized in feature selection.
Given a SaaS idea and niche information, recommend the core features for an MVP.
Focus on features that directly address the main pain points and provide a clear value proposition.
Prioritize features based on implementation effort and impact.
For each feature, provide a title, description, implementation complexity (1-5), and rationale.
Return 5-8 features in JSON format."""},
            {"role": "user", "content": f"""
SaaS Idea: {idea}

Niche Information:
Name: {niche_data.get('name', 'Generic SaaS')}
Pain Points: {', '.join(pain_points) if pain_points else 'Not specified'}

Please recommend features for this SaaS product, prioritized by importance."""}
        ]
        
        # Call OpenAI API
        response = self.openai_client.chat_completion(
            messages=prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        features_data = response.parse_json()
        
        # Ensure proper structure or create default
        if not features_data or "features" not in features_data:
            logger.warning("Failed to generate valid feature recommendations, using defaults")
            return self._default_features(idea)
        
        # Add feature IDs
        for i, feature in enumerate(features_data["features"]):
            feature["id"] = f"f{i+1}"
            # Ensure complexity is an integer between 1-5
            if "complexity" in feature:
                try:
                    feature["complexity"] = min(5, max(1, int(feature["complexity"])))
                except (ValueError, TypeError):
                    feature["complexity"] = 3
        
        return features_data["features"]
    
    def generate_mvp_guidance(self, 
                            idea: str, 
                            features: List[Dict[str, Any]], 
                            niche_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MVP design guidance based on selected features.
        
        Args:
            idea: Brief description of the SaaS idea
            features: List of selected features
            niche_data: Niche research data
            
        Returns:
            Dictionary with MVP design guidance
        """
        # Extract feature titles for prompt
        feature_titles = [f["title"] for f in features if "title" in f]
        
        # Extract positioning statements if available
        positioning = ""
        if "positioning_statements" in niche_data and niche_data["positioning_statements"]:
            statements = [s.get("content", "") for s in niche_data["positioning_statements"]]
            positioning = "Positioning Statements:\n" + "\n".join(statements)
        
        # Prepare prompt for API
        prompt = [
            {"role": "system", "content": """You are a SaaS MVP strategist.
Given a SaaS idea and selected features, provide actionable MVP development guidance.
Include recommended technology stack, implementation phases, key metrics to track,
deployment strategy, and user feedback collection approach.
Focus on practical advice that balances speed to market with quality.
Return the guidance in JSON format."""},
            {"role": "user", "content": f"""
SaaS Idea: {idea}

Selected Features:
{', '.join(feature_titles)}

{positioning}

Please provide MVP development guidance."""}
        ]
        
        # Call OpenAI API
        response = self.openai_client.chat_completion(
            messages=prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        guidance_data = response.parse_json()
        
        # Ensure proper structure or create default
        if not guidance_data:
            logger.warning("Failed to generate valid MVP guidance, using defaults")
            return self._default_mvp_guidance()
        
        return guidance_data
    
    def generate_branding_inspiration(self, idea: str, niche_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate branding inspiration including name suggestions, colors, and messaging.
        
        Args:
            idea: Brief description of the SaaS idea
            niche_data: Niche research data
            
        Returns:
            Dictionary with branding inspiration
        """
        # Extract positioning statements if available
        positioning = ""
        if "positioning_statements" in niche_data and niche_data["positioning_statements"]:
            statements = [s.get("content", "") for s in niche_data["positioning_statements"]]
            positioning = "Positioning Statements:\n" + "\n".join(statements)
        
        # Prepare prompt for API
        prompt = [
            {"role": "system", "content": """You are a SaaS branding expert.
Given a SaaS idea, provide branding inspiration including name suggestions, color palette,
logo concepts, messaging themes, and visual style guidelines.
Focus on creating a cohesive brand identity that appeals to the target market.
Suggest modern, memorable names that are likely to have available domains.
Return the branding suggestions in JSON format."""},
            {"role": "user", "content": f"""
SaaS Idea: {idea}

Niche: {niche_data.get('name', 'Generic SaaS')}

{positioning}

Please provide branding inspiration."""}
        ]
        
        # Call OpenAI API
        response = self.openai_client.chat_completion(
            messages=prompt,
            temperature=0.9,  # Higher temperature for creative naming
            response_format={"type": "json_object"}
        )
        
        branding_data = response.parse_json()
        
        # Ensure proper structure or create default
        if not branding_data:
            logger.warning("Failed to generate valid branding inspiration, using defaults")
            return self._default_branding()
        
        # Enhance with branding utilities
        if "name_suggestions" in branding_data:
            # Analyze name suggestions for quality
            name_analysis = BrandingUtils.analyze_name_suggestions(branding_data["name_suggestions"])
            branding_data["name_analysis"] = name_analysis
            
            # Add domain suggestions for top names
            if name_analysis["top_recommendations"]:
                top_name = name_analysis["top_recommendations"][0]["name"]
                branding_data["domain_suggestions"] = BrandingUtils.suggest_domain_variations(top_name)
        
        # Generate tone examples if tone is specified
        if "tone" in branding_data and "target_audience" in branding_data:
            branding_data["message_examples"] = BrandingUtils.generate_message_tone_examples(
                branding_data["tone"],
                branding_data["target_audience"]
            )
        
        return branding_data
    
    def generate_first_use_experience(self, idea: str, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate first-use experience recommendations.
        
        Args:
            idea: Brief description of the SaaS idea
            features: List of selected features
            
        Returns:
            Dictionary with first-use experience recommendations
        """
        # Extract feature titles for prompt
        feature_titles = [f["title"] for f in features if "title" in f]
        
        # Prepare prompt for API
        prompt = [
            {"role": "system", "content": """You are a UX expert specialized in SaaS onboarding.
Given a SaaS idea and its features, recommend an effective first-use experience.
Include onboarding flow, user education, key activation steps, and wow moments.
Focus on reducing friction and quickly demonstrating value to new users.
Return the recommendations in JSON format."""},
            {"role": "user", "content": f"""
SaaS Idea: {idea}

Features:
{', '.join(feature_titles)}

Please provide first-use experience recommendations."""}
        ]
        
        # Call OpenAI API
        response = self.openai_client.chat_completion(
            messages=prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        first_use_data = response.parse_json()
        
        # Ensure proper structure or create default
        if not first_use_data:
            logger.warning("Failed to generate valid first-use recommendations, using defaults")
            return self._default_first_use()
        
        # Add validation approaches using MVPUtils
        first_use_data["validation_approaches"] = MVPUtils.suggest_mvp_validation_approaches(features)
        
        return first_use_data
    
    def _save_prototype(self, prototype: Dict[str, Any]) -> bool:
        """
        Save the prototype to a file.
        
        Args:
            prototype: The prototype data to save
            
        Returns:
            True if saved successfully
        """
        filepath = f"{self.data_dir}/{prototype['id']}.json"
        return write_json(filepath, prototype)
    
    def get_prototype(self, prototype_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a saved prototype by ID.
        
        Args:
            prototype_id: ID of the prototype to retrieve
            
        Returns:
            Prototype data or None if not found
        """
        filepath = f"{self.data_dir}/{prototype_id}.json"
        return read_json(filepath)
    
    def list_prototypes(self) -> List[Dict[str, Any]]:
        """
        List all saved prototypes with basic metadata.
        
        Returns:
            List of prototype metadata
        """
        import os
        import glob
        
        prototypes = []
        prototype_files = glob.glob(f"{self.data_dir}/*.json")
        
        for file_path in prototype_files:
            prototype = read_json(file_path)
            if prototype:
                prototypes.append({
                    "id": prototype.get("id"),
                    "idea": prototype.get("idea"),
                    "niche": prototype.get("niche"),
                    "created_at": prototype.get("created_at"),
                    "feature_count": len(prototype.get("features", []))
                })
        
        return prototypes
    
    def _default_features(self, idea: str) -> List[Dict[str, Any]]:
        """
        Create default features when API fails.
        
        Args:
            idea: Brief description of the SaaS idea
            
        Returns:
            List of default features
        """
        return [
            {
                "id": "f1",
                "title": "User Authentication",
                "description": "Secure login and registration system with role-based access control",
                "complexity": 3,
                "rationale": "Essential for user identity and personalization"
            },
            {
                "id": "f2",
                "title": "Dashboard",
                "description": "Personalized dashboard showing key metrics and activity",
                "complexity": 2,
                "rationale": "Provides users with at-a-glance information and quick access to core functionality"
            },
            {
                "id": "f3",
                "title": "Basic Reporting",
                "description": "Simple reports and analytics on user activity and key metrics",
                "complexity": 3,
                "rationale": "Delivers immediate value and insights to users"
            }
        ]
    
    def _default_mvp_guidance(self) -> Dict[str, Any]:
        """
        Create default MVP guidance when API fails.
        
        Returns:
            Dictionary with default MVP guidance
        """
        return {
            "technology_stack": {
                "frontend": "React with Next.js",
                "backend": "Node.js with Express",
                "database": "MongoDB",
                "hosting": "Vercel or AWS"
            },
            "implementation_phases": [
                {
                    "phase": "Foundation",
                    "description": "Set up project structure, authentication, and database"
                },
                {
                    "phase": "Core Features",
                    "description": "Implement essential features identified as high priority"
                },
                {
                    "phase": "Polish & Launch",
                    "description": "Add final UI polish, testing, and deploy to production"
                }
            ],
            "key_metrics": [
                "User Sign-ups",
                "Feature Engagement",
                "Time-to-Value",
                "Retention Rate"
            ],
            "feedback_collection": {
                "methods": [
                    "In-app feedback widget",
                    "Automated email after key actions",
                    "One-on-one interviews with early users"
                ]
            }
        }
    
    def _default_branding(self) -> Dict[str, Any]:
        """
        Create default branding when API fails.
        
        Returns:
            Dictionary with default branding
        """
        return {
            "name_suggestions": [
                {"name": "NimbleSaaS", "reason": "Suggests agility and software-as-a-service"},
                {"name": "FlexCore", "reason": "Implies flexibility and essential functionality"},
                {"name": "ZenithApp", "reason": "Suggests peak performance and excellence"}
            ],
            "color_palette": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#9b59b6",
                "background": "#f5f8fa",
                "text": "#2c3e50"
            },
            "messaging_themes": [
                "Simplicity and ease of use",
                "Time-saving automation",
                "Reliable performance"
            ],
            "visual_style": {
                "description": "Clean, minimalist design with ample whitespace and subtle rounded corners. Use simple icons and clear typography."
            }
        }
    
    def _default_first_use(self) -> Dict[str, Any]:
        """
        Create default first-use experience when API fails.
        
        Returns:
            Dictionary with default first-use experience
        """
        return {
            "onboarding_flow": [
                {
                    "step": "Welcome",
                    "description": "Brief introduction to the product and its value proposition"
                },
                {
                    "step": "Account Setup",
                    "description": "Quick profile creation with minimal required fields"
                },
                {
                    "step": "Feature Tour",
                    "description": "Interactive walkthrough of core features"
                },
                {
                    "step": "First Action",
                    "description": "Guide user to complete their first meaningful action"
                }
            ],
            "wow_moments": [
                "Show immediate value through a pre-populated dashboard",
                "Provide an early win by automating a previously manual task",
                "Surprise with unexpected helpful feature"
            ],
            "user_education": {
                "methods": [
                    "Contextual tooltips",
                    "Brief video tutorials",
                    "Interactive guided tasks"
                ]
            },
            "activation_checklist": [
                "Complete profile",
                "Connect first integration",
                "Create first project",
                "Invite team member"
            ]
        } 