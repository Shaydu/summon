# error_handling.py
"""
Shared error formatting and logging utilities for API v3.4
"""
def format_error(message, code=400):
    return {"status": "error", "message": message, "code": code}
