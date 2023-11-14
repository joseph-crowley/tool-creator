import numpy as np

def numpy_json_serializer(obj):
    """
    Custom serializer for objects including numpy data types
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, 
                          np.int16, np.int32, np.int64, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, 
                          np.float64, np.floating)):
        return float(obj)
    elif isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif hasattr(obj, '__dict__'):
        # Recursively apply serialization to attributes of custom objects
        return {k: numpy_json_serializer(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [numpy_json_serializer(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: numpy_json_serializer(v) for k, v in obj.items()}
    else:
        return obj