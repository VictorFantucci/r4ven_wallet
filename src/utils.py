import os
import sys

utils_directory =  os.path.dirname(os.path.dirname(__file__))

def get_logs_folder() -> str:
    """
    Returns the path to the logs folder.

    The logs folder is located within the `src/logs` directory inside the
    `utils_directory`.

    Returns:
        str: The absolute path to the logs folder.
    """
    return os.path.join(utils_directory, "src", "logs")

