import json
import functools
import os
from datetime import datetime
import uuid
from decouple import config
import inspect

LAKES_BASE_DIR = config("LAKES_BASE_DIR")


def serialize_data(data):
    """
    Attempt to JSON serialize the data, converting non-serializable objects to strings.
    """
    if isinstance(data, (dict, list, tuple)):
        if isinstance(data, dict):
            return {key: serialize_data(value) for key, value in data.items()}
        else:
            return [serialize_data(item) for item in data]
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError):
        return str(data)


def log_io_to_json(func):
    """
    Decorator that logs the input and output of a function to a JSON file.
    
    This function is designed to assist in the creation of data lakes by automatically
    logging all interactions with data sources. It captures and logs the function's
    input arguments and output, along with execution time and any errors encountered.
    
    :param func: The function to be decorated.
    :return: The wrapper function which extends the functionality of 'func' with logging.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Generate a unique identifier for the function call
        call_id = str(uuid.uuid4())
        # Capture the start time
        start_time = datetime.now().isoformat(timespec='seconds')
        
        # Call the original function
        try:
            output_data = func(*args, **kwargs)
            error = False
            error_log = ''
        except Exception as e:
            output_data = None
            error = True
            error_log = str(e)
        # Capture the end time
        end_time = datetime.now().isoformat(timespec='seconds')

        # Get the function's signature and bind the passed arguments to it
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Transform bound_args.arguments into a dictionary with parameter names as keys
        args_dict = {param_name: serialize_data(param_value) for param_name, param_value in bound_args.arguments.items()}
        serialized_input = {'args': args_dict}

        serialized_output = serialize_data(output_data)

        # Store the input, output data, and timing information
        log_data = {
            'id': call_id,
            'start_time': start_time,
            'end_time': end_time,
            'input': serialized_input,
            'output': serialized_output,
            'error': error,
            'error_log': error_log
        }
        
        # Determine the file path using the function's __name__ and prepend the base directory
        file_path = os.path.join(LAKES_BASE_DIR, f"{func.__qualname__.replace('.','_')}.json")
        
        # Check if the directory exists, create it if not
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Read the existing data, if any, and append the new log entry
        try:
            with open(file_path, 'r') as f:
                log_entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log_entries = []
        
        log_entries.append(log_data)
        
        # Write the updated log entries list to the file
        with open(file_path, 'w') as f:
            json.dump(log_entries, f, indent = 1)
        
        return output_data
    return wrapper


def read_log(json_file_path):
    """
    Reads the content of a JSON file and returns the data.

    :param json_file_path: The path to the JSON file.
    :return: The data contained in the JSON file.
    """
    with open(json_file_path, 'r') as file:
        return json.load(file)

