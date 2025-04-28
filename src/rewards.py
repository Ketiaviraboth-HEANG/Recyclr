"""
Rewards system for the Plastic Tracker application.
Manages achievements, gift card generation, and reward tracking.
"""
import random
import string
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Achievement:
    """Represents a recycling achievement milestone."""
    def __init__(self, id: str, title: str, description: str, required_items: int, 
                 discount_amount: int, icon: str):
        self.id = id
        self.title = title
        self.description = description
        self.required_items = required_items
        self.discount_amount = discount_amount
        self.icon = icon
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'required_items': self.required_items,
            'discount_amount': self.discount_amount,
            'icon': self.icon
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Achievement':
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            required_items=data['required_items'],
            discount_amount=data['discount_amount'],
            icon=data['icon']
        )

class GiftCard:
    """Represents a gift card reward earned from recycling plastic items."""
    def __init__(self, code: str, discount_amount: int, achievement_id: str):
        self.code = code
        self.discount_amount = discount_amount
        self.achievement_id = achievement_id
        self.date_earned = datetime.now().strftime("%Y-%m-%d")
        self.is_redeemed = False
        self.date_redeemed = None
    
    def redeem(self):
        """Mark the gift card as redeemed."""
        self.is_redeemed = True
        self.date_redeemed = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'discount_amount': self.discount_amount,
            'achievement_id': self.achievement_id,
            'date_earned': self.date_earned,
            'is_redeemed': self.is_redeemed,
            'date_redeemed': self.date_redeemed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GiftCard':
        gift_card = cls(
            code=data['code'],
            discount_amount=data['discount_amount'],
            achievement_id=data['achievement_id']
        )
        gift_card.date_earned = data['date_earned']
        gift_card.is_redeemed = data['is_redeemed']
        gift_card.date_redeemed = data['date_redeemed']
        return gift_card

class RewardsSystem:
    """Manages the rewards system, including achievements and gift cards."""
    def __init__(self, storage_file: str = 'rewards_data.json'):
        self.storage_file = storage_file
        self.achievements: List[Achievement] = []
        self.gift_cards: List[GiftCard] = []
        self.earned_achievements: List[str] = []  # IDs of earned achievements
        
        # Define default achievements if none exist
        self._initialize_default_achievements()
        
        # Load saved data
        self.load_data()
    
    def _initialize_default_achievements(self):
        """Set up default achievement tiers."""
        default_achievements = [
            Achievement(
                id="recycling_novice",
                title="Recycling Novice",
                description="Recycle 5 plastic items",
                required_items=5,
                discount_amount=10,
                icon="🌱"
            ),
            Achievement(
                id="recycling_enthusiast",
                title="Recycling Enthusiast",
                description="Recycle 10 plastic items",
                required_items=10,
                discount_amount=15,
                icon="🌿"
            ),
            Achievement(
                id="recycling_hero",
                title="Recycling Hero",
                description="Recycle 25 plastic items",
                required_items=25,
                discount_amount=25,
                icon="🌳"
            ),
            Achievement(
                id="planet_savior",
                title="Planet Savior",
                description="Recycle 50 plastic items",
                required_items=50,
                discount_amount=50,
                icon="🌎"
            )
        ]
        
        # Only set default achievements if none exist yet
        if not self.achievements:
            self.achievements = default_achievements
    
    def load_data(self):
        """Load rewards data from storage file."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                
                # Load achievements
                self.achievements = [Achievement.from_dict(a) for a in data.get('achievements', [])]
                
                # If no achievements were loaded, initialize defaults
                if not self.achievements:
                    self._initialize_default_achievements()
                
                # Load gift cards
                self.gift_cards = [GiftCard.from_dict(g) for g in data.get('gift_cards', [])]
                
                # Load earned achievement IDs
                self.earned_achievements = data.get('earned_achievements', [])
    
    def save_data(self):
        """Save rewards data to storage file."""
        data = {
            'achievements': [a.to_dict() for a in self.achievements],
            'gift_cards': [g.to_dict() for g in self.gift_cards],
            'earned_achievements': self.earned_achievements
        }
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_gift_card_code(self) -> str:
        """Generate a random 6-digit alphanumeric gift card code."""
        # Generate code with a mix of uppercase letters and numbers
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(characters) for _ in range(6))
        
        # Make sure the code is unique
        while any(gift_card.code == code for gift_card in self.gift_cards):
            code = ''.join(random.choice(characters) for _ in range(6))
        
        return code
    
    def check_achievements(self, recycled_count: int) -> Optional[Achievement]:
        """
        Check if any new achievements were earned based on recycled count.
        Returns the new achievement if earned, otherwise None.
        """
        newly_earned = None
        
        for achievement in sorted(self.achievements, key=lambda a: a.required_items):
            if (achievement.required_items <= recycled_count and 
                achievement.id not in self.earned_achievements):
                # Mark achievement as earned
                self.earned_achievements.append(achievement.id)
                
                # Generate gift card for this achievement
                code = self.generate_gift_card_code()
                gift_card = GiftCard(
                    code=code,
                    discount_amount=achievement.discount_amount,
                    achievement_id=achievement.id
                )
                self.gift_cards.append(gift_card)
                
                # Save the changes
                self.save_data()
                
                # Return the newly earned achievement
                newly_earned = achievement
                break
        
        return newly_earned
    
    def get_active_gift_cards(self) -> List[GiftCard]:
        """Get list of gift cards that haven't been redeemed yet."""
        return [card for card in self.gift_cards if not card.is_redeemed]
    
    def get_redeemed_gift_cards(self) -> List[GiftCard]:
        """Get list of gift cards that have been redeemed."""
        return [card for card in self.gift_cards if card.is_redeemed]
    
    def redeem_gift_card(self, code: str) -> bool:
        """
        Redeem a gift card by its code.
        Returns True if successful, False if code is invalid or already redeemed.
        """
        for card in self.gift_cards:
            if card.code == code:
                if not card.is_redeemed:
                    card.redeem()
                    self.save_data()
                    return True
                break
        
        return False
    
    def get_progress_to_next_achievement(self, recycled_count: int) -> Dict:
        """
        Calculate progress towards the next achievement.
        Returns a dict with current_count, next_milestone, percentage, and achievement.
        """
        # Find the next unearned achievement
        next_achievement = None
        for achievement in sorted(self.achievements, key=lambda a: a.required_items):
            if achievement.id not in self.earned_achievements:
                next_achievement = achievement
                break
        
        # If all achievements are earned
        if not next_achievement:
            last_achievement = max(self.achievements, key=lambda a: a.required_items)
            return {
                'current_count': recycled_count,
                'next_milestone': last_achievement.required_items,
                'percentage': 100,
                'achievement': last_achievement
            }
        
        # Calculate progress percentage
        previous_milestone = 0
        for achievement in sorted(self.achievements, key=lambda a: a.required_items):
            if achievement.id in self.earned_achievements:
                previous_milestone = max(previous_milestone, achievement.required_items)
        
        # Adjusted count is how far beyond the previous milestone
        adjusted_count = recycled_count - previous_milestone
        required_for_next = next_achievement.required_items - previous_milestone
        percentage = min(100, int((adjusted_count / required_for_next) * 100))
        
        return {
            'current_count': recycled_count,
            'next_milestone': next_achievement.required_items,
            'percentage': percentage,
            'achievement': next_achievement
        }
    
    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by its ID."""
        for achievement in self.achievements:
            if achievement.id == achievement_id:
                return achievement
        return None
    
    def get_earned_achievements_list(self) -> List[Achievement]:
        """Get a list of earned achievements."""
        return [
            achievement for achievement in self.achievements
            if achievement.id in self.earned_achievements
        ]