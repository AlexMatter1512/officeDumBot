# todo_util.py
import dotenv
import os

dotenv.load_dotenv()
TODO_FILE_PATH = os.getenv('TODO_FILE_PATH', './todo.txt')
LAVAGNETTA_FILE_PATH = os.getenv('LAVAGNETTA_FILE_PATH', './lavagnetta.txt')

def add_item(todo_item: str, list:str="todo"):
    """Append a list item to the file."""
    FILE_PATH = TODO_FILE_PATH if list == "todo" else LAVAGNETTA_FILE_PATH
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, 'a') as file:
        file.write(todo_item + '\n')

def get_all_items(list:str="todo"):
    """Retrieve all list items from the file."""
    FILE_PATH = TODO_FILE_PATH if list == "todo" else LAVAGNETTA_FILE_PATH
    try:
        with open(FILE_PATH, 'r') as file:
            todos = file.readlines()
        return todos
    except FileNotFoundError:
        return []


def remove_item_by_index(index: int, list:str="todo"):
    """Remove a list item by its index."""
    FILE_PATH = TODO_FILE_PATH if list == "todo" else LAVAGNETTA_FILE_PATH

    todos = get_all_items(list)
    if index < 0 or index >= len(todos):
        return None
    
    removed_todo = todos.pop(index)

    # Save the updated list back to the file
    with open(FILE_PATH, 'w') as file:
        file.writelines(todos)

    return removed_todo.strip()