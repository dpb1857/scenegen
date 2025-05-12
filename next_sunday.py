
import datetime

def next_sunday_noon():
    """
    Calculate the next Sunday at noon from the current date and time.

    Returns:
        str: The date of the next Sunday in 'yyyy-mm-dd' format.
    """
    now = datetime.datetime.now()

    # Get the current day of the week (0 = Monday, 6 = Sunday)
    current_day_of_week = now.weekday()

    # Calculate days until next Sunday
    # If today is Sunday (6) and it's before noon, next Sunday is today
    # If today is Sunday (6) and it's noon or after, next Sunday is in 7 days
    # Otherwise, calculate days until Sunday
    if current_day_of_week == 6:  # Today is Sunday
        if now.hour < 12 or (now.hour == 12 and now.minute == 0 and now.second == 0):
            days_until_sunday = 0
        else:
            days_until_sunday = 7
    else:
        days_until_sunday = 6 - current_day_of_week

    # Calculate the next Sunday date
    next_sunday = now + datetime.timedelta(days=days_until_sunday)

    # Set the time to noon (12:00:00)
    next_sunday_noon = datetime.datetime(
        next_sunday.year,
        next_sunday.month,
        next_sunday.day,
        12, 0, 0
    )

    # Format the date as yyyy-mm-dd
    return next_sunday_noon.strftime('%Y-%m-%d')

# Example usage
if __name__ == "__main__":
    print(f"Next Sunday at noon will be on: {next_sunday_noon()}")
