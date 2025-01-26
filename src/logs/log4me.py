"""
Script that contains all functions related to project logs.
"""
import io
import os
import glob
import inspect
import logging
from contextlib import redirect_stdout, redirect_stderr
from typing import Callable, Tuple

class r4venLogManager:
    def __init__(self, base_log_dir: str):
        """
        Initializes the LogManager with a base directory for logs.

        Args:
            base_log_dir (str): Path to the base directory where logs will be stored.
        """
        self.base_log_dir = base_log_dir
        self.logs_directory = os.path.join(base_log_dir, "logs")
        self._ensure_directory(self.logs_directory)

    def function_logger(self,
                        script_path: str,
                        file_mode: str = "w",
                        file_level: int = logging.INFO,
                        console_level: int = None) -> logging.Logger:
        """
        Creates a logger object specific to the calling context (module, standalone function, or class method).

        Args:
            script_path (str): Full path of the script that is calling this function.
            file_mode (str): File mode for the log file (default: "w" for write).
            file_level (int): Logging level that will be written in the log file (default: logging.INFO).
            console_level (int, optional): Logging level that will be displayed in the console.

        Returns:
            logging.Logger: Logger object.
        """
        # Create necessary folders for the log file
        script_log_file_path = self._create_script_logs_folder(script_path)

        # Inspect the calling frame
        caller_frame = inspect.stack()[1]
        module_name = os.path.basename(script_path).replace(".py", "")

        # Detect the calling context: module, function, or class method
        if caller_frame.function == "<module>":
            # Module-level logger (e.g., code outside any function or class)
            log_name = module_name
        else:
            # Determine if the caller is within a class
            class_name = None
            if "self" in caller_frame.frame.f_locals:
                # 'self' exists in the caller's local variables, indicating a method
                class_name = caller_frame.frame.f_locals["self"].__class__.__name__

            # Construct the logger name based on the context
            if class_name:
                log_name = f"{module_name}.{class_name}.{caller_frame.function}"
            else:
                # Standalone function
                log_name = f"{module_name}.{caller_frame.function}"

        # Construct the full log file path
        log_file_path = os.path.join(script_log_file_path, f"{log_name}.log")

        # Ensure the directory for the log file exists
        self._ensure_directory(os.path.dirname(log_file_path))

        # Ensure the log file exists
        if not os.path.exists(log_file_path):
            open(log_file_path, "a").close()

        # Initialize the logger
        logger = logging.getLogger(log_name)

        # Clear any existing handlers to avoid duplicate logs
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set logger to log all messages
        logger.setLevel(logging.DEBUG)

        # Add console handler if console_level is set
        if console_level is not None:
            ch = logging.StreamHandler()
            ch.setLevel(console_level)
            ch_format = logging.Formatter("%(levelname)-8s - %(message)s")
            ch.setFormatter(ch_format)
            logger.addHandler(ch)

        # Add file handler for writing logs to a file
        fh = logging.FileHandler(log_file_path, mode=file_mode)
        fh.setLevel(file_level)
        fh_format = logging.Formatter("%(asctime)s - %(lineno)d - %(levelname)-8s - %(message)s")
        fh.setFormatter(fh_format)
        logger.addHandler(fh)

        return logger


    def merge_log_files(self, output_log_path: str, log_files_pattern: str = "*.log") -> None:
        """
        Merges multiple log files from a specified folder into a single log file.

        Args:
            output_log_path (str): The output file path for the merged log.
            log_files_pattern (str, optional): The pattern for .log files (adjust if needed)
                Defaults to "*.log".

        Returns:
            None
        """

        self._ensure_directory(os.path.join(self.base_log_dir, "_output_"))

        log_files = sorted(glob.glob(os.path.join(self.logs_directory, log_files_pattern)),
                           key=os.path.getmtime)

        with open(output_log_path, "w") as merged_log:
            for log_file in log_files:
                with open(log_file, "r") as current_log:
                    merged_log.write(current_log.read())

    def clear_logs_folder(self, log_files_format=".log") -> None:
        """
        Removes all files of a specified format from the 'logs' directory.

        This function deletes all files within the given directory that match the specified
        file format (default is '.log'). It ensures that only files with the designated
        format are targeted, leaving others unaffected.

        Args:
            log_files_format (str): The file extension format to delete (default is '.log').

        Returns:
            None
        """

        self._delete_files_of_specific_format(self.logs_directory, log_files_format)

    def capture_terminal_output(self, func: Callable, *args, **kwargs) -> Tuple[str, None]:
        """
        Runs a function and captures all terminal output (stdout, stderr, and logs).

        Args:
            func (Callable): The function to run and capture output from.
            *args: Positional arguments to pass to `func`.
            **kwargs: Keyword arguments to pass to `func`.

        Returns:
            Tuple[str, None]: Captured output as a string, and None if function has no return.
        """

        buffer = io.StringIO()

        class BufferHandler(logging.StreamHandler):
            def __init__(self, stream):
                super().__init__(stream)

        log_handler = BufferHandler(buffer)
        log_handler.setFormatter(logging.Formatter("%(levelname)-8s - %(message)s"))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)

        try:
            with redirect_stdout(buffer), redirect_stderr(buffer):
                result = func(*args, **kwargs)
        finally:
            logger.removeHandler(log_handler)

        output = buffer.getvalue()
        buffer.close()
        return output, result

    def _create_script_logs_folder(self, script_path: str) -> str:
        """
        Creates a logs folder for the script with the same directory structure as the script itself.
        For example, if the script is located at "src/data/script.py", it will create the folder
        structure "logs/data/script" inside the specified logs directory.

        Args:
            base_log_dir (str): Base directory where the "logs" folder is located.
            script_path (str): Full path of the script that is calling this function.

        Returns:
            str: Logs folder for the script with the same directory structure as the script itself.
        """
        project_directory = os.getcwd()
        relative_script_path = os.path.relpath(script_path, project_directory)
        script_log_path = os.path.splitext(relative_script_path)[0]
        final_directory = os.path.join(self.base_log_dir, script_log_path)
        self._ensure_directory(final_directory)
        return final_directory

    @staticmethod
    def _ensure_directory(directory: str) -> None:
        """Ensures a directory exists, creating it if necessary."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def _delete_files_of_specific_format(path: str, file_extension: str) -> None:
        """
        Delete files of a specific format in the specified path and all subfolders.
        """
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                if file.endswith(file_extension):
                    os.remove(os.path.join(root, file))
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
