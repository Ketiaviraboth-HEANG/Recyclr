"""
Utility functions for the Plastic Tracker application.
"""
import random
import string
import hashlib
import datetime
import re
from typing import Dict, List, Any, Optional

def generate_random_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric code of specified length.
    
    Args:
        length: Length of the code to generate (default: 6)
        
    Returns:
        A random alphanumeric code
    """
    # Use only uppercase letters and numbers for better readability
    characters = string.ascii_uppercase + string.digits
    
    # Exclude potentially confusing characters (O, 0, I, 1)
    characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    
    return ''.join(random.choice(characters) for _ in range(length))

def get_reward_tier(recycled_count: int) -> Dict[str, Any]:
    """
    Get the reward tier information based on recycled count.
    
    Args:
        recycled_count: Number of recycled items
        
    Returns:
        Dictionary with tier information
    """
    tiers = [
        {
            "name": "Beginner",
            "required": 5,
            "discount": 10,
            "icon": "🌱",
            "color": "#34D399"
        },
        {
            "name": "Enthusiast",
            "required": 10,
            "discount": 15,
            "icon": "🌿",
            "color": "#10B981"
        },
        {
            "name": "Hero",
            "required": 25,
            "discount": 25,
            "icon": "🌳",
            "color": "#059669"
        },
        {
            "name": "Planet Savior",
            "required": 50,
            "discount": 50,
            "icon": "🌎",
            "color": "#047857"
        }
    ]
    
    # Find the highest tier earned
    earned_tier = None
    for tier in tiers:
        if recycled_count >= tier["required"]:
            earned_tier = tier
        else:
            break
    
    # If no tier earned yet, return first tier as next goal
    if not earned_tier:
        return {
            "current_tier": None,
            "next_tier": tiers[0],
            "progress_percentage": (recycled_count / tiers[0]["required"]) * 100
        }
    
    # Find next tier if there is one
    current_tier_index = tiers.index(earned_tier)
    next_tier = tiers[current_tier_index + 1] if current_tier_index < len(tiers) - 1 else None
    
    # Calculate progress to next tier
    if next_tier:
        progress = (recycled_count - earned_tier["required"]) / (next_tier["required"] - earned_tier["required"]) * 100
    else:
        progress = 100
    
    return {
        "current_tier": earned_tier,
        "next_tier": next_tier,
        "progress_percentage": progress
    }

def validate_gift_card_code(code: str) -> bool:
    """
    Validate gift card code format.
    
    Args:
        code: The gift card code to validate
        
    Returns:
        True if code is valid, False otherwise
    """
    # Check length
    if len(code) != 6:
        return False
    
    # Check format (uppercase letters and numbers only)
    pattern = r'^[A-Z0-9]{6}$'
    if not re.match(pattern, code):
        return False
    
    return True

def format_discount_amount(amount: int) -> str:
    """
    Format discount amount for display.
    
    Args:
        amount: Discount amount (percentage)
        
    Returns:
        Formatted string
    """
    return f"{amount}% OFF"

def calculate_expiration_date(date_earned: str, days_valid: int = 90) -> str:
    """
    Calculate expiration date for a gift card.
    
    Args:
        date_earned: Date the gift card was earned
        days_valid: Number of days gift card is valid
        
    Returns:
        Expiration date string
    """
    earned_date = datetime.datetime.strptime(date_earned, "%Y-%m-%d")
    expiration_date = earned_date + datetime.timedelta(days=days_valid)
    return expiration_date.strftime("%Y-%m-%d")

def get_hash_for_code(code: str) -> str:
    """
    Generate a secure hash for a gift card code for verification.
    
    Args:
        code: Gift card code
        
    Returns:
        Secure hash string
    """
    # Add a secret salt (in a production environment, this would be stored securely)
    salt = "RecyclrApp2025"
    salted_code = f"{code}{salt}"
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(salted_code.encode())
    return hash_obj.hexdigest()

def get_environmental_impact(recycled_count: int) -> Dict[str, Any]:
    """
    Calculate environmental impact based on recycled items.
    
    Args:
        recycled_count: Number of recycled items
        
    Returns:
        Dictionary with environmental impact metrics
    """
    # Simplified calculations
    avg_co2_per_item = 50  # grams of CO2
    co2_saved = recycled_count * avg_co2_per_item
    
    # One tree absorbs about 25kg (25,000g) of CO2 per year
    tree_equivalent = co2_saved / 25000
    
    # One square meter of landfill can hold about 20 plastic items
    landfill_space_saved = recycled_count / 20  # square meters
    
    # Average plastic item takes 450 years to decompose
    decomposition_years_avoided = recycled_count * 450
    
    return {
        "co2_saved": co2_saved,
        "tree_equivalent": tree_equivalent,
        "landfill_space_saved": landfill_space_saved,
        "decomposition_years_avoided": decomposition_years_avoided
    }

def get_motivational_message(recycled_count: int) -> str:
    """
    Get a motivational message based on recycling activity.
    
    Args:
        recycled_count: Number of recycled items
        
    Returns:
        Motivational message
    """
    if recycled_count == 0:
        return "Start your recycling journey today and earn rewards!"
    elif recycled_count < 5:
        return "Great start! Keep recycling to earn your first reward."
    elif recycled_count < 10:
        return "You're making a difference! Keep up the good work."
    elif recycled_count < 25:
        return "You're becoming a recycling champion!"
    elif recycled_count < 50:
        return "Amazing impact! You're helping save the planet."
    else:
        return "You're a recycling superstar! Your actions are truly making a difference."