import cv2 as cv
import pytesseract
from PIL import Image
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class PlasticItem:
    def __init__(self, name: str, category: str, receipt_id: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.category = category
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.receipt_id = receipt_id
        self.carbon_footprint = self._calculate_carbon_footprint()
        self.recycled = False

    def _calculate_carbon_footprint(self) -> float:
        # Simplified carbon footprint calculation based on category
        footprints = {
            'bottle': 82.8,
            'container': 55.2,
            'bag': 33.0,
            'cup': 28.5,
            'utensil': 18.3
        }
        return footprints.get(self.category, 40.0)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'date': self.date,
            'receipt_id': self.receipt_id,
            'carbon_footprint': self.carbon_footprint,
            'recycled': self.recycled
        }

class PlasticTracker:
    def __init__(self, storage_file: str = 'plastic_items.json'):
        self.storage_file = storage_file
        self.items: List[PlasticItem] = []
        self.load_items()

        # Keywords for plastic detection
        self.plastic_keywords = {
            'bottle': ['BOTTLE', 'WATER', 'SODA', 'BEVERAGE'],
            'container': ['CONTAINER', 'YOGURT', 'SALAD', 'TAKEOUT'],
            'bag': ['BAG', 'PLASTIC BAG', 'SHOPPING BAG'],
            'cup': ['CUP', 'COFFEE', 'DRINK'],
            'utensil': ['UTENSIL', 'FORK', 'SPOON', 'KNIFE', 'CUTLERY']
        }

    def load_items(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                items_data = json.load(f)
                for item_data in items_data:
                    item = PlasticItem(
                        item_data['name'],
                        item_data['category'],
                        item_data['receipt_id']
                    )
                    item.id = item_data['id']
                    item.date = item_data['date']
                    item.carbon_footprint = item_data['carbon_footprint']
                    item.recycled = item_data['recycled']
                    self.items.append(item)

    def save_items(self):
        with open(self.storage_file, 'w') as f:
            json.dump([item.to_dict() for item in self.items], f, indent=2)

    def preprocess_image(self, image_path: str) -> np.ndarray:
        image = cv.imread(image_path)
        
        # Resize image
        scale_percent = 150
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        image = cv.resize(image, (width, height), interpolation=cv.INTER_LINEAR)
        
        # Convert to grayscale
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        
        # Apply bilateral filter
        gray = cv.bilateralFilter(gray, 11, 17, 17)
        
        # Apply adaptive threshold
        thresh = cv.adaptiveThreshold(
            gray, 255,
            cv.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv.THRESH_BINARY_INV,
            25, 15
        )
        
        # Morphological operations
        kernel = np.ones((1, 1), np.uint8)
        processed = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
        
        return processed

    def extract_text(self, image: np.ndarray) -> str:
        custom_config = r'--oem 3 --psm 4'
        return pytesseract.image_to_string(image, config=custom_config)

    def get_items_from_text(self, text: str) -> List[str]:
        excluded_keywords = [
            'SUBTOTAL', 'TOTAL', 'TAX', 'CHANGE', 'PAY', 'PURCHASE',
            'ITEMS SOLD', 'DEBIT', 'EFT', 'REF', 'AID', 'NETWORK',
            'TERMINAL', 'ID', 'LOW PRICES', 'GIVE US FEEDBACK',
            'WALMART', 'MGR:', 'ELIZABETH', 'STR', 'TR#', 'THANK',
            'DATE', 'TIME', 'APPROVAL', 'ACCOUNT', 'CASHIER'
        ]

        items = []
        for line in text.splitlines():
            clean_line = line.strip().upper()
            if any(keyword in clean_line for keyword in excluded_keywords):
                continue
            if clean_line == '':
                continue
            if any(char.isdigit() for char in clean_line) and any(char.isalpha() for char in clean_line):
                items.append(clean_line)
        return items

    def detect_plastic_items(self, items: List[str], receipt_id: str) -> List[PlasticItem]:
        plastic_items = []
        
        for item in items:
            item_upper = item.upper()
            for category, keywords in self.plastic_keywords.items():
                if any(keyword in item_upper for keyword in keywords):
                    plastic_item = PlasticItem(item, category, receipt_id)
                    plastic_items.append(plastic_item)
                    self.items.append(plastic_item)
                    break
        
        self.save_items()
        return plastic_items

    def process_receipt(self, image_path: str) -> List[PlasticItem]:
        receipt_id = f"receipt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Process image
        processed_image = self.preprocess_image(image_path)
        
        # Extract text
        text = self.extract_text(processed_image)
        
        # Get items
        items = self.get_items_from_text(text)
        
        # Detect plastic items
        plastic_items = self.detect_plastic_items(items, receipt_id)
        
        return plastic_items

    def mark_as_recycled(self, item_id: str):
        for item in self.items:
            if item.id == item_id:
                item.recycled = True
                break
        self.save_items()

    def get_stats(self) -> Dict:
        total_plastics = len(self.items)
        recycled_plastics = sum(1 for item in self.items if item.recycled)
        carbon_saved = sum(item.carbon_footprint * 0.5 for item in self.items if item.recycled)
        tree_equivalent = carbon_saved / 23000  # Average tree absorbs 23kg CO2 per year

        return {
            'total_plastics': total_plastics,
            'recycled_plastics': recycled_plastics,
            'carbon_saved': carbon_saved,
            'tree_equivalent': tree_equivalent
        }

def main():
    tracker = PlasticTracker()
    
    while True:
        print("\n=== Plastic Tracking System ===")
        print("1. Process new receipt")
        print("2. View all items")
        print("3. Mark item as recycled")
        print("4. View statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            image_path = input("Enter the path to the receipt image: ")
            if os.path.exists(image_path):
                plastic_items = tracker.process_receipt(image_path)
                print(f"\nDetected {len(plastic_items)} plastic items:")
                for item in plastic_items:
                    print(f"- {item.name} ({item.category})")
            else:
                print("Error: File not found")

        elif choice == '2':
            print("\nAll plastic items:")
            for item in tracker.items:
                status = "✓" if item.recycled else "✗"
                print(f"[{status}] {item.name} ({item.category}) - {item.date}")

        elif choice == '3':
            print("\nSelect item to mark as recycled:")
            for i, item in enumerate(tracker.items):
                if not item.recycled:
                    print(f"{i+1}. {item.name} ({item.category})")
            
            try:
                idx = int(input("Enter item number: ")) - 1
                if 0 <= idx < len(tracker.items):
                    tracker.mark_as_recycled(tracker.items[idx].id)
                    print("Item marked as recycled!")
                else:
                    print("Invalid item number")
            except ValueError:
                print("Invalid input")

        elif choice == '4':
            stats = tracker.get_stats()
            print("\nStatistics:")
            print(f"Total plastic items: {stats['total_plastics']}")
            print(f"Recycled items: {stats['recycled_plastics']}")
            print(f"Carbon saved: {stats['carbon_saved']:.1f}g CO2")
            print(f"Tree equivalent: {stats['tree_equivalent']:.3f} trees")

        elif choice == '5':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()