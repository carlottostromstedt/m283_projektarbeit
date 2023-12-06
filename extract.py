import cv2
import pytesseract
from pytesseract import Output

import cv2
import pytesseract
from pytesseract import Output

# Load and preprocess the image
image = cv2.imread("card2.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

custom_config = r'-l eng+spa --psm 6'
txt = pytesseract.image_to_string(processed_image, config=custom_config)

print(txt)