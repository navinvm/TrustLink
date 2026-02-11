"""
Serverless Compatibility Utilities
Handles file operations gracefully for read-only filesystems
"""
import os
import json
from functools import wraps

def safe_file_write(filepath, data, mode='w'):
    """
    Safely write to a file, handling read-only filesystem errors
    Returns: (success: bool, error: str or None)
    """
    try:
        with open(filepath, mode) as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=4)
            else:
                f.write(data)
        return True, None
    except (OSError, PermissionError, IOError) as e:
        # Serverless read-only filesystem
        return False, f"Read-only filesystem: {str(e)}"
    except Exception as e:
        return False, f"Write error: {str(e)}"

def safe_file_read(filepath, as_json=True, default=None):
    """
    Safely read from a file with fallback
    Returns: (data, error: str or None)
    """
    try:
        if not os.path.exists(filepath):
            return default, "File not found"
        
        with open(filepath, 'r') as f:
            if as_json:
                data = json.load(f)
            else:
                data = f.read()
        return data, None
    except Exception as e:
        return default, f"Read error: {str(e)}"

def serverless_safe(func):
    """
    Decorator to make functions serverless-safe
    Catches file write errors and continues gracefully
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (OSError, PermissionError, IOError) as e:
            print(f"⚠️ Serverless mode - skipping file operation: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error in {func.__name__}: {e}")
            raise
    return wrapper

def is_writable_filesystem():
    """
    Check if the filesystem is writable
    Returns: bool
    """
    try:
        test_file = '.write_test'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except (OSError, PermissionError, IOError):
        return False

# Global flag for filesystem type
IS_SERVERLESS = None

def detect_environment():
    """Detect if running in serverless environment"""
    global IS_SERVERLESS
    if IS_SERVERLESS is None:
        IS_SERVERLESS = not is_writable_filesystem()
        if IS_SERVERLESS:
            print("🔧 Detected serverless/read-only environment - using cache-only mode")
        else:
            print("💾 Detected writable filesystem - using file persistence")
    return IS_SERVERLESS
