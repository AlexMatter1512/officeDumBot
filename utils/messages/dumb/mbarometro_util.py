import dotenv
import os
import yaml
import logging

log = logging.getLogger("dumb")
dotenv.load_dotenv()
MBAROMETRO_FILE_PATH = os.getenv('MBAROMETRO_FILE_PATH', './mbarometro.yaml')
# Ensure the directory exists
os.makedirs(os.path.dirname(MBAROMETRO_FILE_PATH), exist_ok=True)

def increment(user: str, amount: int = 1):
    """
        Increment the value stored in the file by a specified amount.
        Args:
            user (str): The user to increment the value for.
            amount (int, optional): The amount to increment the value by. Defaults to 1.
        Returns:
            int: The new incremented value.
    """

    try:
        #read the yaml file
        with open(MBAROMETRO_FILE_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        data = {}

    try:
        total = 0
        for _, value in data.items():
            total += value

        #increment the value for the user
        data[user] = data.get(user, 0) + amount

        #write the yaml file
        with open(MBAROMETRO_FILE_PATH, 'w') as file:
            yaml.dump(data, file)

        return data[user], total + amount
    
    except Exception as e:
        log.error(e)
        return 0, 0

# def get_value(user: str = None) -> str: 
#     """Retrieve the value from the file."""
#     try:
#         with open(MBAROMETRO_FILE_PATH, 'r') as file:
#             data = yaml.safe_load(file)
#             if user:
#                 return data.get(user, 0)
#             return data
#     except Exception:
#         return 0