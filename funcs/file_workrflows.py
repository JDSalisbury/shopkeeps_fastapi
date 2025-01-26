
import json
import random

FILE_PATH_IMAGE_JSON = "funcs/image_urls.json"

# Load JSON data from the file


def load_image_data(file_path: str) -> dict:
    """
    Loads JSON data from the specified file path.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)  # Parse JSON into a Python dictionary
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")

# Path to the JSON file


# Load the data


def get_random_image(sex: str, character_class: str) -> str:
    """
    Returns a random image URL based on the sex and character_class.
    Falls back to the Default list if character_class isn't found.
    """
    # Try to get the list of URLs for the given sex and character_class
    image_data = load_image_data(FILE_PATH_IMAGE_JSON)

    try:
        character_images = image_data[sex].get(character_class)
        if not character_images:  # Fall back to Default if not found
            character_images = image_data[sex].get("Default")

        # Randomly select an image from the list
        return random.choice(character_images)
    except KeyError:
        raise ValueError(
            f"Invalid sex '{sex}' provided or data structure error.")
