import re
from faker import Faker
from typing import Dict, Tuple

# Maps entity types to colors for highlighting
color_map: Dict[str, str] = {
    'first_name': '#1E90FF',  # Dodger Blue
    'last_name': '#00CED1',  # Dark Turquoise
    'middle_name': '#6A5ACD',  # Slate Blue
    'phone': '#FF69B4',  # Hot Pink
    'email': '#00FA9A',  # Medium Spring Green
    'address_line_1': '#FFA500',  # Orange
    'address_line_2': '#FF8C00',  # Dark Orange
    'city': '#9932CC',  # Dark Orchid
    'state': '#FF6347',  # Tomato
    'zipcode': '#A0522D',  # Sienna
    'company': '#8B008B',  # Dark Magenta
    'country': '#DC143C',  # Crimson
}

# Maps entity types to colors for highlighting
fake = Faker()
faker_func: Dict[str, str] = {
    'first_name': fake.first_name,
    'last_name': fake.last_name,
    'middle_name': lambda x: '',
    'phone': fake.phone_number, 
    'email': fake.safe_email,
    'address_line_1': fake.street_address, 
    'address_line_2': fake.street_address,
    'city': fake.city, 
    'state': fake.state,
    'zipcode': fake.zipcode,
    'company': fake.company,
    'country': fake.country,
}


def highlight_text(tagged_text: str) -> str:
    """
    Highlights the tagged entities in the given text using HTML and CSS.
    
    Args:
        tagged_text (str): The input text with tagged entities.
        
    Returns:
        str: The input text with tags replaced with colors for entities.
    """
    # Define the color mapping for each tag
    for tag, color in color_map.items():
        pattern = re.compile(f'<{tag}>(.*?)</{tag}>')
        tagged_text = pattern.sub(f'<span style="color:{color}">**\\1**</span>', tagged_text)

    return tagged_text


def mask_text(tagged_text: str, identifiers: Dict[str, list]) -> Tuple[str, str]:
    """
    Masks the tagged entities in the given text with fake values.
    
    Args:
        tagged_text (str): The input text with PII tagged.
        identifiers (Dict[str, list]): A dictionary mapping entity types to lists of entity values.
        
    Returns:
        Tuple[str, str]: A tuple containing the masked text and the masked text with highlights.
    """
    fake_values = {}
    masked_text = tagged_text
    masked_text_with_highlights = tagged_text
    for entity, values in identifiers.items():
        color = color_map[entity]                
        masking_func = faker_func[entity]
        for value in values:           
            masked_value = masking_func()
            highlighted_value = f'<span style="color:{color}">**{masked_value}**</span>'
            masked_text = masked_text.replace(f'<{entity}>{value}</{entity}>', masked_value)  
            masked_text_with_highlights = masked_text_with_highlights.replace(f'<{entity}>{value}</{entity}>', highlighted_value)
            fake_values[value] = masked_value
    return masked_text, masked_text_with_highlights