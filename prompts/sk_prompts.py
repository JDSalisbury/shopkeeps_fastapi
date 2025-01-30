

def GENERATE_SHOPKEEP(location, shopkeeps):
    shop_types_in_location = []
    for shopkeep in shopkeeps['shopkeeps']:
        if shopkeep['location'] == location:
            shop_types_in_location.append(shopkeep['shop_type'])

    print(shop_types_in_location)
    prompt = {
        "model": "gpt-3.5-turbo",
        "store": True,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a world-class NPC generator for Dungeons and Dragons. "
                    "Generate a random shopkeeper as a structured JSON object. "
                    "The shopkeeper should have the following fields: "
                    "name (string), age (integer), sex (string), shop_name (string), description (string), "
                    "character_class (string, e.g., Wizard, Rogue, Fighter), voice (string), "
                    "gold (integer), personality (string), shop_type (string, e.g., Blacksmith, Apothecary, Armorer), "
                    f"friendship_level (integer, between 0 and 10) and location which the value will be {location}. "  # noqa
                    "Do not copy any the examples below, and do not have duplicate shop_types in the same given location. "
                    f"{shopkeeps}"
                    "do not use any of the following shop_types: "
                    f"{shop_types_in_location}"
                    "Locations should have a few different shop types, but should always have at least a two classic ones. If the location is missing a classic shop please add one. example: A blacksmith, a general store, a magic shop, a tavern, etc. "
                    "Only return a JSON object without any additional explanation."
                    "Example response format: "
                    '{"name": "Eldon Ironheart","age": 54, "sex": "Male", "shop_name": "The Enchanted Anvil","description": "A skilled blacksmith known for crafting magical weapons and armor.","character_class": "Fighter","voice": "Gruff", "gold": 500,"personality": "Grumpy but loyal","shop_type": "Blacksmith","friendship_level": 6, "location": "Glimmerhold"}'

                ),
            },
            {"role": "user", "content": "Generate a random shopkeeper."},
        ],
    }
    return prompt


def GENERATE_INVENTORY_FOR_SHOPKEEP(shopkeep, inventory):
    prompt = {
        "model": "gpt-3.5-turbo",
        "store": True,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a world-class Dungeons and Dragons item generator. "
                    "Generate a list of 5-10 items in JSON-structured format for a shop. Each item should have the following fields: "
                    "name (string), description (string), price (integer, in gold, between 10 and 500), "
                    "quantity (integer, between 1 and 20), damage (string or 'N/A'), and armor_class (string or 'N/A'). "
                    f"The shop is called '{shopkeep.shop_name}' the shop type is '{shopkeep.shop_type}', and its description is: '{shopkeep.description}'. "  # noqa
                    f"The shopkeeper is a {shopkeep.character_class} named {shopkeep.name} who is {shopkeep.age} years old. "  # noqa
                    "Base the items on the theme of the shop and ensure they follow D&D 5e rules. "
                    "Please provide a lengtheir response to ensure a variety of items. "
                    "Make sure the description is unique for each item and the details are coherent and clear. "
                    "The description should also explain the item's effects or usage in the game via the games 5e mechanics. "
                    "The description should be at least 30 words long. "
                    "The inventory can include basic items and should if the shop type is a general store, trading post, or similar. "
                    "Do not copy any the examples below, as it is inventory the shopkeep already has. "
                    f"inventory: {inventory}"
                    "Example response format: "
                    '{ "inventory": [ { "name": "Sword of Flames", "description": "A magical sword that ignites enemies. The sword does 1d8 Fire Damge, then they must succeed a constitution save of 10, if they dont, they are on fire for the next 1d4 rounds and will take 1d6 fire damge per round. They may be extinguished with water or the classic stop drop and roll technique.", "price": 250, "quantity": 5, "damage": "1d8 fire", "armor_class": "N/A" } ] }'
                ),
            },
            {"role": "user", "content": "Generate inventory for the shop."},
        ],
    }
    return prompt
