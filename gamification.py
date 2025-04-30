"""
Module: gamification.py

Purpose: Gamify both affiliate and user experiences to drive engagement and loyalty. Includes functions for leaderboards, badges, streaks, and progress bars.
"""

def update_leaderboard(scores):
    """
    Update and return a sorted leaderboard for affiliates or users.
    """
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def unlock_badge(earnings):
    """
    Unlock badges based on earnings milestones.
    """
    if earnings >= 1000:
        return "Badge unlocked: $1,000+ earner!"
    return None

def user_streaks(login_days):
    """
    Track and reward user streaks.
    """
    if login_days >= 7:
        return "7-day streak! Bonus unlocked."
    return None

def progress_bar(current, goal):
    """
    Return a simple text progress bar.
    """
    percent = min(100, int((current / goal) * 100))
    return f"Progress: {percent}%" 