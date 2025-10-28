"""
Validation functions for user input.
"""
import re

def validate_mpesa_code(code: str) -> bool:
    """Validate M-Pesa transaction code format."""
    return bool(re.match(r'^[A-Z0-9]{8,12}$', code))

def validate_phone_number(phone: str) -> bool:
    """Validate Kenyan phone number format."""
    return bool(re.match(r'^\+254[17]\d{8}$|^0[17]\d{8}$', phone))