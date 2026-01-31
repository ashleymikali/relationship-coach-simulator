"""Pre-generated demo users for the agentic matchmaking system."""

from typing import Dict, List, Any


def get_demo_users() -> List[Dict[str, Any]]:
    """
    Return 3 pre-generated demo users for the matchmaking simulation.
    
    Returns:
        List of user profile dictionaries
    """
    return [
        {
            "user_id": "user_001",
            "display_name": "Jordan",
            "bio": "Software engineer who values direct communication and emotional honesty. Loves hiking, board games, and deep conversations over coffee.",
            "traits": [
                "Direct communicator",
                "Values clarity and honesty",
                "Introverted but warm",
                "Analytical thinker",
                "Loyal and committed",
                "Enjoys structured plans"
            ],
            "boundaries": [
                "No public embarrassment or being put on the spot",
                "Needs alone time to recharge",
                "Prefers addressing conflicts directly rather than avoiding them"
            ],
            "notes": "Partner-inspired profile with direct conflict style and sensitivity to public embarrassment"
        },
        {
            "user_id": "user_002",
            "display_name": "Alex",
            "bio": "Creative designer who loves spontaneity and adventure. Enjoys live music, trying new restaurants, and weekend road trips.",
            "traits": [
                "Spontaneous and adventurous",
                "Emotionally expressive",
                "Extroverted and social",
                "Creative problem solver",
                "Optimistic outlook",
                "Loves surprises and novelty"
            ],
            "boundaries": [
                "Needs freedom and independence",
                "Dislikes rigid schedules",
                "Values emotional connection over logic"
            ],
            "notes": "Foil profile - surface compatible with Jordan but fails in simulation due to conflict avoidance vs. directness mismatch"
        },
        {
            "user_id": "user_003",
            "display_name": "Sam",
            "bio": "Therapist who brings empathy and patience to relationships. Enjoys reading, yoga, and meaningful one-on-one time.",
            "traits": [
                "Empathetic listener",
                "Patient and understanding",
                "Values emotional intelligence",
                "Calm under pressure",
                "Enjoys deep connections",
                "Thoughtful and reflective"
            ],
            "boundaries": [
                "No passive-aggressive behavior",
                "Needs emotional reciprocity",
                "Values vulnerability and openness"
            ],
            "notes": "Potentially strong match with Jordan - both value directness and emotional honesty"
        }
    ]


def get_user_by_id(user_id: str) -> Dict[str, Any] | None:
    """
    Retrieve a user profile by user_id.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        User profile dict or None if not found
    """
    users = get_demo_users()
    for user in users:
        if user["user_id"] == user_id:
            return user
    return None
