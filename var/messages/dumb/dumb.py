from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Union
import random
import os
import requests
import json

unsplash_api_key = os.getenv("UNSPLASH_API_KEY")

@dataclass
class MediaInfo:
    MEDIA_TYPE: Optional[Union[str, Callable[[], Optional[str]]]]
    TG_FILE_ID: Optional[Union[str, Callable[[], Optional[str]]]]
    FILE_LOCATION: Union[Path, int, Callable[[], Union[Path, int]]]
    TEXT_MESSAGE: Union[str, Callable[[], str]]

    def resolve(self, value):
        """Helper method to resolve callable values."""
        return value() if callable(value) else value
    
    @property
    def text_message(self) -> str:
        return self.resolve(self.TEXT_MESSAGE)

    @property
    def media_type(self) -> Optional[str]:
        return self.resolve(self.MEDIA_TYPE)
    
    @property
    def tg_file_id(self) -> Optional[str]:
        return self.resolve(self.TG_FILE_ID)
    
    @property
    def file_location(self) -> Union[Path, int]:
        return self.resolve(self.FILE_LOCATION)

# Resolve the current directory dynamically
current_directory = Path(__file__).parent.absolute()


#helpers
def get_unsplash_image_url(query: str = "random") -> Optional[str]:
    """
    Fetches a random image URL from Unsplash using the specified query.
    Returns the small size URL of the image.
    """
    if not unsplash_api_key:
        print("Unsplash API key is not set.")
        return None
    api_key = unsplash_api_key.strip()
    # Build the URL
    url = f"https://api.unsplash.com/photos/random?client_id={api_key}&query={query}"
    
    try:
        # Make the request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse JSON response
        data = response.json()
        
        # Extract the small URL
        small_url = data['urls']['small']
        return small_url
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        return None


PREPUZIO = MediaInfo(
    MEDIA_TYPE="audio",
    TG_FILE_ID="CQACAgQAAxkBAAEuj8tnFiZsSou8WT-8GGyzOicNF10KLAACHhQAArEHsFAdBD4UDirq6DYE",
    FILE_LOCATION=current_directory / 'prepuzio_monella.mp3',
    TEXT_MESSAGE="monella!"
)

LETSGOSKY = MediaInfo(
    MEDIA_TYPE="photo",
    TG_FILE_ID="AgACAgQAAxkBAAEukR9nFloCPsXaHH5bXkAarmXqzaVxEAACDbYxGwmstFBRC0elajO5tQEAAwIAA3MAAzYE",
    FILE_LOCATION=current_directory / 'letsgosky.webp',
    TEXT_MESSAGE="Qualcuno ha detto LETSGOSKI?"
)

CARTOCCIATA = MediaInfo(
    MEDIA_TYPE="photo",
    # TG_FILE_ID="CgACAgQAAxkBAAEukSVnFlusdNveyGV9HLVQxa7JSl8qiQACPAMAAlfTBVOiKuLLaoHf-zYE",
    TG_FILE_ID=lambda: get_unsplash_image_url("food"),
    # FILE_LOCATION=lambda: random.choice(list((current_directory / 'eat').glob('*'))),
    FILE_LOCATION=None,
    TEXT_MESSAGE=lambda: random.choice([
        "La cochina fresca fresca",
        "Ammuccamu",
        "Ector?",
        "Non riesco a mandare l'animassione akdhgpqoierqwjepofj eeee salvo?! reflusso"
    ])
)

RECORDED = MediaInfo(
    MEDIA_TYPE=None,
    TG_FILE_ID=None,
    FILE_LOCATION=0,
    TEXT_MESSAGE=lambda: random.choice([
        "Su chiavi? 🔑",
        "Eeeeeee Salvo",
        "Stutututuuuuu 💨",
        "WOWOWOWOWOWWOWOWO"
    ])
)

CEO = MediaInfo(
    MEDIA_TYPE="photo",
    # TG_FILE_ID="https://evek.uno/4432-large_default/test.jpg",
    TG_FILE_ID=lambda: get_unsplash_image_url(random.choice([
        "sexy",
        "foot fetish",
        "feet fetish",
        "sexy lady",
        "sexy woman",
        "beautiful woman",
        "beautiful lady",
    ])),
    FILE_LOCATION=None,
    TEXT_MESSAGE=lambda: random.choice([
        "mhhh 37 smalto bianco",
        "oouuughhh 💦",
        "addivettiti ceo"
    ])
)
