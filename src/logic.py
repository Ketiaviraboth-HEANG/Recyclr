from typing import List
import cv2 as cv
from cv2.typing import MatLike
import pytesseract
from PIL import Image
import numpy as np
from io import BytesIO


# preprocessing -- this function converts stuff to grayscale first then to binary
def preprocess_image(image_bytes: bytes):

    # reads from bytes, convert to grayscale then to nparray
    image = np.array(Image.open(BytesIO(image_bytes)).convert("L"))

    scale_percent = 150
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv.resize(image, dim, interpolation=cv.INTER_LINEAR)

    filtered = cv.bilateralFilter(image, 11, 17, 17)

    thresh = cv.adaptiveThreshold(
        filtered, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 25, 15
    )

    kernel = np.ones((1, 1), np.uint8)
    processed = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)

    return processed


# text extraction
def extract_text(image: MatLike) -> str:
    custom_config = r"--oem 3 --psm 4"
    text = pytesseract.image_to_string(image, config=custom_config)
    return text


# excluding keywords, so we only take the item bought
def get_items_only(text: str):
    excluded_keywords = [
        "SUBTOTAL",
        "TOTAL",
        "TAX",
        "CHANGE",
        "PAY",
        "PURCHASE",
        "ITEMS SOLD",
        "DEBIT",
        "EFT",
        "REF",
        "AID",
        "NETWORK",
        "TERMINAL",
        "ID",
        "LOW PRICES",
        "GIVE US FEEDBACK",
        "WALMART",
        "MGR:",
        "ELIZABETH",
        "STR",
        "TR#",
        "THANK",
        "DATE",
        "TIME",
        "APPROVAL",
        "ACCOUNT",
        "CASHIER",
    ]

    lines = text.splitlines()
    items: List[str] = []

    for line in lines:
        clean_line = line.strip().upper()
        if (
            any(keyword in clean_line for keyword in excluded_keywords)
            or clean_line == ""
        ):
            continue
        if any(char.isdigit() for char in clean_line) and any(
            char.isalpha() for char in clean_line
        ):
            items.append(clean_line)
    return items


def analyze_receipt(image_bytes: bytes):
    processed_image = preprocess_image(image_bytes)
    text_result = extract_text(processed_image)

    print("📝 OCR Result:")
    print(text_result)

    items_purchased = get_items_only(text_result)

    print("\n🛒 Items Purchased:")
    for item in items_purchased:
        print(item)

    data = {
        "items": items_purchased,
        "text": text_result,
    }

    return data


# if __name__ == "__main__":
#     main()
