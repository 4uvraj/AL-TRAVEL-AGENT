import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.services.image_service import get_destination_image, get_place_images

img = get_destination_image("agra")
print("DESTINATION IMAGE:", img)

places = get_place_images(["Taj Mahal", "Agra Fort", "ITC Mughal, A Luxury Collection Resort & Spa, Agra"], "agra")
print("PLACE IMAGES:", places)
