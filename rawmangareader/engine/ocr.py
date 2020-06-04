import pytesseract
from rawmangareader.engine.bubbletext import BubbleText

def extractTextFromBox(img_rgb, xmin, ymin, boxWidth, boxHeight):
    """
    Extract bubble text from an image.
    The function will crop the image according to the coordinate in
    bubbleTextBox. Then it will use that to extract a text from that box.
    The resulting string will be assigned to .text property of BubbleText class.

    Arguments:
        img_rgb {cv2.Image} -- Image in RGB format.
        xmin {int} -- Top left x coordinate of the box.
        ymin {int} -- Top left y coordinate of the box.
        boxWidth {int} -- Box width.
        boxHeight {int} -- Box height.

    Returns:
        string -- Text within that box.
    """
    # Crop the image to get text with in the box
    #
    crop_img = img_rgb[ymin:ymin+boxHeight, xmin:xmin+boxWidth]

    # Extract the text using OCR and assign to bubbleText object
    #
    output_text = pytesseract.image_to_string(crop_img, lang="jpn_vert", config="--psm 5")

    # Remove newline and space
    #
    return output_text.replace('\r\n', '').replace('\n', '').replace(' ', '')