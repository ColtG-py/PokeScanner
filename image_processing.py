import cv2
import pytesseract
from PIL import ImageGrab
import numpy as np

# OCR to extract text from an image
def extract_text_from_image(image):
    custom_config = r'--oem 3 --psm 6'
    try:
        text = pytesseract.image_to_string(image, lang='pokemon', config=custom_config)
    except pytesseract.pytesseract.TesseractNotFoundError:
        return "Tesseract is not installed or it's not in your PATH."
    return text

# Function to capture a region of the screen
def capture_region(region):
    screenshot = ImageGrab.grab(bbox=(region[0], region[1], region[2] + region[0], region[3] + region[1]))
    return screenshot

# Function to handle drawing rectangle for region selection
def draw_rectangle(event, x, y, flags, param):
    global img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        param['drawing'] = True
        param['ix'], param['iy'] = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if param['drawing']:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (param['ix'], param['iy']), (x, y), (0, 255, 0), 2)
            cv2.imshow("image", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        param['drawing'] = False
        param['fx'], param['fy'] = x, y
        param['region_selected'] = True
        cv2.rectangle(img_copy, (param['ix'], param['iy']), (param['fx'], param['fy']), (0, 255, 0), 2)
        cv2.imshow("image", img_copy)

# Function to capture region by user selection
def select_region():
    print("Please select the region and press Enter.")
    global img, img_copy
    img = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
    img_copy = img.copy()

    param = {'drawing': False, 'ix': -1, 'iy': -1, 'fx': -1, 'fy': -1, 'region_selected': False}
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", draw_rectangle, param)

    while True:
        cv2.imshow("image", img_copy)
        if param['region_selected']:
            break
        if cv2.waitKey(1) & 0xFF == 13:  # Press Enter to finalize selection
            break

    cv2.destroyAllWindows()
    return (param['ix'], param['iy'], param['fx'] - param['ix'], param['fy'] - param['iy'])

# Function to select two regions
def select_two_regions():
    print("Select the region for the Pokémon name.")
    name_region = select_region()
    print("Select the region for the level.")
    level_region = select_region()
    return name_region, level_region
