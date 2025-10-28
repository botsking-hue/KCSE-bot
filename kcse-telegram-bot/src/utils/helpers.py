"""
Helper functions for the bot.
"""

def format_price(amount: int) -> str:
    """Format price as Kenyan Shillings."""
    return f"KES {amount:,}"

def format_user_info(user_data: dict) -> str:
    """Format user information for display."""
    return f"👤 {user_data.get('name', 'Unknown')} | 📦 {user_data.get('package', 'None')}"