import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to clear
output_dir = "output"

def clear_output_folder(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logging.info(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
                    logging.info(f"Deleted directory: {file_path}")
            except Exception as e:
                logging.error(f"Failed to delete {file_path}. Reason: {e}")
    else:
        logging.warning(f"Directory {directory} does not exist.")

# Main execution
clear_output_folder(output_dir)