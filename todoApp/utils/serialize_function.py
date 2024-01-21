def serialize_model(obj, model_class):
    if isinstance(obj, model_class):
        data = {}
        for key, value in obj.__dict__.items():
            # handles not returning null values
            # might change this, not sure of best format yet
            if not key.startswith('_') and value is not None:
                data[key] = value
        return data
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")