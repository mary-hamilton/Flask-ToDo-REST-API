def serialize_model(obj, model_class):
    if isinstance(obj, model_class):
        data = {}
        # As written, this will not serialize any SQLAlchemy relationship properties; they
        # need to be handled explicitly within the specific model serialization functions
        for key, value in obj.__dict__.items():

            # does not return None or empty values but DOES return False
            if not key.startswith('_') and (value is False or value):
                if isinstance(value, list):
                    data[key] = [serialize_model(item, type(item)) for item in value]
                elif hasattr(value, '__dict__'):
                    data[key] = serialize_model(value, type(value))
                else:
                    data[key] = value
        return data
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")