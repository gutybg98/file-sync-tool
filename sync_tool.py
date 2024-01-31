import sys
import shutil
import filecmp
import time
import os
import logging


# Ensure correct command-line arguments are provided
if len(sys.argv) != 5:
    sys.stdout.write("The command must contain the following arguments:\n")
    sys.stdout.write("- path/to/source/folder\n")
    sys.stdout.write("- path/to/destination/folder\n")
    sys.stdout.write("- synchronization interval (in minutes)\n")
    sys.stdout.write("- path/to/log/file ('*.log')\n")
    exit()

# Extract command-line arguments
src_path = sys.argv[1].replace('\\', '/')
dst_path = sys.argv[2].replace('\\', '/')
sync_interval = float(sys.argv[3]) * 60
log_path = sys.argv[4].replace('\\', '/')

# Set up logging
FORMAT = '%(levelname)s - %(asctime)s - %(message)s'
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_path, mode='a')
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Synchronization:
    """
    Class to handle synchronization of files and directories.
    """
    messages = set()
    dirs_to_delete = []
    files_to_delete = []

    def __init__(self, src: str, dst: str, logger: logging.Logger):
        """
        Initialize Synchronization object.

        Args:
            src (str): Path to source directory.
            dst (str): Path to destination directory.
            logger (logging.Logger): Logger object for logging messages.
        """
        self.src = src
        self.dst = dst
        self.logger = logger

    def log_message(self, action: str, file_name: str, file_path: str):
        """
        Log a message and add it to the set of messages.

        Args:
            action (str): The action being performed.
            file_name (str): The name of the file or directory.
            file_path (str): The path of the file or directory.

        Returns:
            bool: True if the message was added, False otherwise.
        """
        message = f'{action} "{file_name}" in "{file_path}"'
        if message not in Synchronization.messages:
            sys.stdout.write(f'{message}\n')
            self.logger.info(message)
            Synchronization.messages.add(message)
            return True
        return False

    def logging(self, dcmp: filecmp.dircmp):
        """
        Log differences between source and destination directories.

        Args:
            dcmp (filecmp.dircmp): A dircmp object representing the comparison between source and destination directories.
        """
        # Log files/directories only present in source
        for file_name in dcmp.left_only:
            full_path = os.path.join(dcmp.left, file_name)
            if os.path.isdir(full_path):
                self.log_message('Created directory', file_name, dcmp.left)
            elif os.path.isfile(full_path):
                self.log_message('Created file', file_name, dcmp.left)

        # Log files/directories only present in destination
        for file_name in dcmp.right_only:
            full_path = f"{dcmp.right}/{file_name}"
            if os.path.isdir(full_path):
                if self.log_message('Deleted directory', file_name, dcmp.left):
                    Synchronization.dirs_to_delete.append(full_path)
            elif os.path.isfile(full_path):
                if self.log_message('Deleted file', file_name, dcmp.left):
                    Synchronization.files_to_delete.append(full_path)

        # Log modified files
        for file_name in dcmp.diff_files:
            self.log_message('Modified file', file_name, dcmp.left)

        # Recursively log subdirectories
        for sub_dcmp in dcmp.subdirs.values():
            self.logging(sub_dcmp)

    def copy(self):
        """
        Copy files from source to destination, and delete files and directories as needed.
        """
        try:
            sys.stdout.write('Making a full copy...\n')
            shutil.copytree(self.src, self.dst, dirs_exist_ok=True)
            if Synchronization.dirs_to_delete:
                for dir in Synchronization.dirs_to_delete:
                    shutil.rmtree(dir)
            if Synchronization.files_to_delete:
                for file in Synchronization.files_to_delete:
                    os.remove(file)
            sys.stdout.write(f'Success! All folders are up to date.\n')
            sys.stdout.write('Press Ctrl-C to stop the program\n')
            sys.stdout.write(f'Listening to {src_path}...\n')
            self.logger.info("A full copy was made")
        except Exception as e:
            sys.stdout.write(e.__str__())

        # Reset lists after copying
        Synchronization.messages = set()
        Synchronization.dirs_to_delete = []
        Synchronization.files_to_delete = []


# Initialize Synchronization object
synchronization = Synchronization(src_path, dst_path, logger)

# Perform
synchronization.copy()
try:
    while True:
        start_time = time.time()

        while time.time() - start_time < sync_interval:
            dcmp = filecmp.dircmp(src_path, dst_path)
            synchronization.logging(dcmp)
            time.sleep(0.5)

        synchronization.copy()
except KeyboardInterrupt:
    sys.stdout.write('Program finished')
    exit()
