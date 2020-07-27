def get_error(status_code, message, **kwargs):
    return {"errors": [
        {
            "status": status_code,
            "detail": message,
            **kwargs
        }
    ]}, status_code
