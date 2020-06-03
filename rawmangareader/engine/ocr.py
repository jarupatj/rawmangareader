import os
import cv2
import pytesseract
from rawmangareader.engine.bubbletext import BubbleText

def extractTextFromBox(img_rgb, xmin, ymin, boxWidth, boxHeight):
    # Crop the image to get text with in the box
    #
    crop_img = img_rgb[ymin:ymin+boxHeight, xmin:xmin+boxWidth]

    # Extract the text using OCR and assign to bubbleText object
    #
    output_text = pytesseract.image_to_string(crop_img, lang="jpn_vert", config="--psm 5")

    # Remove newline and space
    #
    return output_text.replace('\r\n', '').replace('\n', '').replace(' ', '')

def extractText(image, bubbleTextBoxes):
    """Extract bubble text from an image.
    The function will crop the image according to the coordinate in
    bubbleTextBox. Then it will use that to extract a text from that box.
    The resulting string will be assigned to .text property of BubbleText class.

    Arguments:
        images {cv2.Image} -- OpenCV image
        bubbleTextBoxes {list[BubbleText]} -- List of BubbleText object
    """
    # Convert to RGB because tesserract only works with RGB format
    #
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for box in bubbleTextBoxes:
        xmin = int(box.coordinates[0])
        ymin = int(box.coordinates[1])
        xmax = int(box.coordinates[2])
        ymax = int(box.coordinates[3])
        boxWidth = xmax - xmin
        boxHeight = ymax - ymin

        output_text = extractTextFromBox(img_rgb, xmin, ymin, boxWidth, boxHeight)
        box.text = output_text.replace('\r\n', '').replace('\n', '').replace(' ', '')
