"""
MVP Utilities

Utilities for MVP design guidance, technology selection, and development
strategy recommendations.
"""

from typing import Dict, Any, List, Optional, Set

# Standard technology stack recommendations by category
TECH_STACKS = {
    "frontend": {
        "react": {
            "name": "React with Next.js",
            "description": "Modern React framework with server-side rendering",
            "pros": ["Great developer experience", "Strong ecosystem", "SEO-friendly"],
            "cons": ["Learning curve for beginners", "Can be overkill for simple UIs"],
            "ideal_for": ["SaaS dashboards", "Complex UIs", "Public-facing websites"]
        },
        "vue": {
            "name": "Vue.js",
            "description": "Progressive JavaScript framework",
            "pros": ["Easier learning curve", "Great documentation", "Flexible integration"],
            "cons": ["Smaller ecosystem than React", "Fewer enterprise adoptions"],
            "ideal_for": ["Startups", "Simpler UIs", "Gradual adoption"]
        },
        "svelte": {
            "name": "Svelte",
            "description": "Compiler-based framework with minimal runtime",
            "pros": ["Excellent performance", "Less boilerplate", "Small bundle size"],
            "cons": ["Smaller community", "Fewer learning resources", "Less battle-tested"],
            "ideal_for": ["Performance-critical applications", "Small teams", "Modern startups"]
        }
    },
    "backend": {
        "node": {
            "name": "Node.js with Express",
            "description": "JavaScript runtime with popular web framework",
            "pros": ["JavaScript throughout stack", "Vast npm ecosystem", "Great for APIs"],
            "cons": ["Single-threaded", "CPU-intensive tasks can be challenging"],
            "ideal_for": ["API servers", "Real-time applications", "Microservices"]
        },
        "python": {
            "name": "Python with FastAPI/Django",
            "description": "Python web frameworks for rapid development",
            "pros": ["Rapid development", "Great for data science", "Strong typing (FastAPI)"],
            "cons": ["Slower than some alternatives", "Global interpreter lock"],
            "ideal_for": ["Data-heavy applications", "AI/ML integration", "Admin interfaces"]
        },
        "ruby": {
            "name": "Ruby on Rails",
            "description": "Convention-over-configuration web framework",
            "pros": ["Extremely rapid development", "Built-in best practices", "Mature ecosystem"],
            "cons": ["Performance overhead", "Less popular for newer projects"],
            "ideal_for": ["Rapid MVPs", "CRUD applications", "Small to medium teams"]
        }
    },
    "database": {
        "postgresql": {
            "name": "PostgreSQL",
            "description": "Robust open-source relational database",
            "pros": ["ACID compliant", "Advanced features", "Great for complex data"],
            "cons": ["Setup complexity", "Requires more resources than lighter DBs"],
            "ideal_for": ["Data reliability needs", "Complex queries", "Scaling potential"]
        },
        "mongodb": {
            "name": "MongoDB",
            "description": "Document-oriented NoSQL database",
            "pros": ["Schema flexibility", "JSON-like documents", "Easy scaling"],
            "cons": ["Less suited for relational data", "ACID guarantees limited in older versions"],
            "ideal_for": ["Rapid prototyping", "Document storage", "Flexible schema needs"]
        },
        "firebase": {
            "name": "Firebase/Firestore",
            "description": "Google's serverless database and backend",
            "pros": ["Realtime capabilities", "Minimal setup", "Built-in auth"],
            "cons": ["Vendor lock-in", "Can get expensive at scale", "Limited query capabilities"],
            "ideal_for": ["MVPs", "Realtime applications", "Mobile-first products"]
        }
    },
    "hosting": {
        "vercel": {
            "name": "Vercel",
            "description": "Platform optimized for frontend frameworks",
            "pros": ["Excellent developer experience", "Built for Next.js", "Free tier"],
            "cons": ["More expensive at scale", "Limited backend capabilities"],
            "ideal_for": ["Frontend-heavy applications", "JAMstack", "Next.js apps"]
        },
        "aws": {
            "name": "AWS (EC2/ECS/Lambda)",
            "description": "Amazon's cloud computing platform",
            "pros": ["Comprehensive services", "Extreme scalability", "Market leader"],
            "cons": ["Complex management", "Steeper learning curve", "Cost management needs"],
            "ideal_for": ["Enterprise apps", "Long-term projects", "Custom infrastructure"]
        },
        "heroku": {
            "name": "Heroku",
            "description": "Platform-as-a-Service for easy deployment",
            "pros": ["Extremely simple deployment", "Managed services", "Developer friendly"],
            "cons": ["More expensive", "Limited customization", "Sleep on free tier"],
            "ideal_for": ["MVPs", "Startups", "Teams without DevOps"]
        }
    }
}


class MVPUtils:
    """
    Utilities for MVP planning and technology selection.
    """
    
    @staticmethod
    def recommend_tech_stack(
        features: List[Dict[str, Any]],
        team_size: int = 2,
        has_devops: bool = False,
        budget_constraint: str = "medium"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Recommend technology stack based on product features and team constraints.
        
        Args:
            features: List of feature dictionaries
            team_size: Number of developers on the team
            has_devops: Whether the team has DevOps expertise
            budget_constraint: Budget level (low, medium, high)
            
        Returns:
            Dictionary with technology recommendations by category
        """
        # Default recommendations
        recommendations = {
            "frontend": TECH_STACKS["frontend"]["react"].copy(),
            "backend": TECH_STACKS["backend"]["node"].copy(),
            "database": TECH_STACKS["database"]["postgresql"].copy(),
            "hosting": TECH_STACKS["hosting"]["vercel"].copy()
        }
        
        # Extract feature keywords for analysis
        feature_text = " ".join([
            f"{feature.get('title', '')} {feature.get('description', '')}"
            for feature in features
        ]).lower()
        
        # Adjust for team size and budget
        if team_size <= 2:
            # Smaller teams benefit from simpler stacks
            if "vue" not in feature_text and "react" not in feature_text:
                recommendations["frontend"] = TECH_STACKS["frontend"]["vue"].copy()
                
            # For small teams with budget constraints, serverless is easier
            if budget_constraint == "low":
                recommendations["backend"] = TECH_STACKS["backend"]["node"].copy()
                recommendations["database"] = TECH_STACKS["database"]["firebase"].copy()
                recommendations["hosting"] = TECH_STACKS["hosting"]["vercel"].copy()
                
        # Feature-based adjustments
        if any(keyword in feature_text for keyword in ["ai", "machine learning", "data science", "analytics"]):
            recommendations["backend"] = TECH_STACKS["backend"]["python"].copy()
        
        if any(keyword in feature_text for keyword in ["realtime", "chat", "notification", "socket"]):
            if recommendations["database"]["name"] != TECH_STACKS["database"]["firebase"]["name"]:
                recommendations["database"] = TECH_STACKS["database"]["mongodb"].copy()
        
        # DevOps capabilities affect hosting
        if not has_devops and budget_constraint != "high":
            if "firebase" in recommendations["database"]["name"]:
                recommendations["hosting"] = TECH_STACKS["hosting"]["vercel"].copy()
            else:
                recommendations["hosting"] = TECH_STACKS["hosting"]["heroku"].copy()
        elif has_devops:
            recommendations["hosting"] = TECH_STACKS["hosting"]["aws"].copy()
        
        return recommendations
    
    @staticmethod
    def generate_implementation_phases(
        features: List[Dict[str, Any]],
        max_features_per_phase: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate recommended implementation phases for features.
        
        Args:
            features: List of feature dictionaries
            max_features_per_phase: Maximum features to include in each phase
            
        Returns:
            List of implementation phases with included features
        """
        # Assume features are already sorted by priority
        phases = []
        features_left = features.copy()
        
        phase_number = 1
        while features_left:
            # Take up to max_features_per_phase
            current_features = features_left[:max_features_per_phase]
            features_left = features_left[max_features_per_phase:]
            
            # Create phase info
            phase = {
                "phase": f"Phase {phase_number}",
                "description": MVPUtils._generate_phase_description(phase_number, current_features),
                "features": [f.get('title', 'Unnamed feature') for f in current_features],
                "feature_count": len(current_features)
            }
            
            phases.append(phase)
            phase_number += 1
        
        return phases
    
    @staticmethod
    def _generate_phase_description(phase_number: int, features: List[Dict[str, Any]]) -> str:
        """
        Generate a description for an implementation phase.
        
        Args:
            phase_number: Number of the implementation phase
            features: Features in this phase
            
        Returns:
            Description string
        """
        if phase_number == 1:
            return "Foundation and core functionality - establishing the key value proposition"
        elif phase_number == 2:
            return "Enhancement and expansion - adding key supporting features"
        else:
            return "Refinement and scaling - completing the feature set and optimizing"
    
    @staticmethod
    def recommend_key_metrics(
        features: List[Dict[str, Any]],
        product_type: str = "saas"
    ) -> Dict[str, List[str]]:
        """
        Recommend key metrics to track based on product features.
        
        Args:
            features: List of feature dictionaries
            product_type: Type of product (saas, marketplace, etc.)
            
        Returns:
            Dictionary with categorized metrics
        """
        # Extract feature keywords
        feature_text = " ".join([
            f"{feature.get('title', '')} {feature.get('description', '')}"
            for feature in features
        ]).lower()
        
        # Base metrics that apply to most products
        metrics = {
            "acquisition": [
                "Visitor to signup conversion rate",
                "Cost per acquisition (CPA)",
                "Traffic sources"
            ],
            "activation": [
                "Onboarding completion rate",
                "Time to first value",
                "Feature discovery rate"
            ],
            "retention": [
                "Daily/weekly active users",
                "Churn rate",
                "Session frequency"
            ],
            "revenue": [
                "Monthly recurring revenue (MRR)",
                "Average revenue per user (ARPU)",
                "Lifetime value (LTV)"
            ]
        }
        
        # Add specific metrics based on features
        if any(keyword in feature_text for keyword in ["payment", "subscription", "billing"]):
            metrics["revenue"].extend([
                "Conversion to paid",
                "Upgrade rate",
                "Payment failure rate"
            ])
        
        if any(keyword in feature_text for keyword in ["collaborate", "team", "share", "invite"]):
            metrics["growth"] = [
                "Invites sent per user",
                "Team expansion rate",
                "Viral coefficient"
            ]
        
        if any(keyword in feature_text for keyword in ["content", "create", "upload", "publish"]):
            metrics["engagement"] = [
                "Content creation rate",
                "Content consumption ratio",
                "Content sharing rate"
            ]
        
        # Product-type specific metrics
        if product_type == "marketplace":
            metrics["marketplace"] = [
                "Gross merchandise volume (GMV)",
                "Buyer to seller ratio",
                "Transaction conversion rate"
            ]
        
        return metrics
    
    @staticmethod
    def suggest_mvp_validation_approaches(
        features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest approaches for validating MVP features.
        
        Args:
            features: List of feature dictionaries
            
        Returns:
            List of validation approaches
        """
        core_features = features[:min(3, len(features))]
        feature_names = [f.get('title', 'Unnamed feature') for f in core_features]
        
        approaches = []
        
        # User testing approach
        approaches.append({
            "method": "User Testing Sessions",
            "description": "Conduct guided user testing sessions with target users",
            "target_features": feature_names,
            "metrics": ["Task completion rate", "Time on task", "User satisfaction score"],
            "estimated_time": "2-3 weeks",
            "tools": ["UserTesting.com", "Lookback", "Zoom"]
        })
        
        # A/B Testing
        approaches.append({
            "method": "Limited Release A/B Testing",
            "description": "Release MVP to limited audience with A/B variants of key features",
            "target_features": feature_names[:1] if feature_names else ["Main feature"],
            "metrics": ["Engagement rate", "Conversion diff", "Usage frequency"],
            "estimated_time": "3-4 weeks",
            "tools": ["LaunchDarkly", "Optimizely", "Split.io"]
        })
        
        # Problem interviews
        approaches.append({
            "method": "Problem/Solution Interviews",
            "description": "Structured interviews to validate problem assumptions and solution fit",
            "target_features": ["Overall product concept"],
            "metrics": ["Problem validation score", "Solution interest", "Willingness to pay"],
            "estimated_time": "2 weeks",
            "tools": ["Customer.io", "Typeform", "Calendly"]
        })
        
        return approaches 