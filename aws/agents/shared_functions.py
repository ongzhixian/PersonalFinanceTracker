import logging
import os

def get_standard_log_file_name(file_path):
    return f"{os.path.basename(file_path).replace('.py', '')}.log"


def get_logger(name, log_file_name=None, level=logging.INFO):
    if log_file_name is None: log_file_name = f"{os.path.basename(__file__).replace('.py', '')}.log"
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create file handler
    fh = logging.FileHandler(log_file_name)
    fh.setFormatter(formatter)
    # Create console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger