#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar-related data models for Persian Life Manager Application
"""

from datetime import datetime

class Event:
    """Calendar event model"""
    
    def __init__(self, id, user_id, title, date, start_time=None, end_time=None, 
                 location=None, description=None, all_day=False, has_reminder=False):
        """Initialize a calendar event
        
        Args:
            id (int): Event ID (None for new events)
            user_id (int): User ID
            title (str): Event title
            date (str): Event date (YYYY-MM-DD)
            start_time (str, optional): Start time (HH:MM)
            end_time (str, optional): End time (HH:MM)
            location (str, optional): Event location
            description (str, optional): Event description
            all_day (bool, optional): Whether the event is all-day
            has_reminder (bool, optional): Whether the event has a reminder
        """
        self.id = id
        self.user_id = user_id
        self.title = title
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.location = location or ""
        self.description = description or ""
        self.all_day = all_day
        self.has_reminder = has_reminder
    
    def __str__(self):
        if self.all_day:
            return f"Event({self.id}, {self.title}, {self.date}, All Day)"
        return f"Event({self.id}, {self.title}, {self.date}, {self.start_time}-{self.end_time})"
    
    def get_start_datetime(self):
        """Get the start date and time as a datetime object
        
        Returns:
            datetime: Start date and time
        """
        if self.all_day:
            return datetime.strptime(self.date, "%Y-%m-%d")
        
        return datetime.strptime(f"{self.date} {self.start_time}", "%Y-%m-%d %H:%M")
    
    def get_end_datetime(self):
        """Get the end date and time as a datetime object
        
        Returns:
            datetime: End date and time
        """
        if self.all_day:
            # End of the day
            return datetime.strptime(f"{self.date} 23:59", "%Y-%m-%d %H:%M")
        
        return datetime.strptime(f"{self.date} {self.end_time}", "%Y-%m-%d %H:%M")


class Task:
    """Task model"""
    
    def __init__(self, id, user_id, title, due_date, priority="medium", 
                 description=None, completed=False, completion_date=None, has_reminder=False):
        """Initialize a task
        
        Args:
            id (int): Task ID (None for new tasks)
            user_id (int): User ID
            title (str): Task title
            due_date (str): Due date (YYYY-MM-DD)
            priority (str, optional): Priority (low, medium, high)
            description (str, optional): Task description
            completed (bool, optional): Whether the task is completed
            completion_date (str, optional): Completion date (YYYY-MM-DD)
            has_reminder (bool, optional): Whether the task has a reminder
        """
        self.id = id
        self.user_id = user_id
        self.title = title
        self.due_date = due_date
        self.priority = priority
        self.description = description or ""
        self.completed = completed
        self.completion_date = completion_date
        self.has_reminder = has_reminder
    
    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        return f"Task({self.id}, {self.title}, {self.due_date}, {self.priority}, {status})"
    
    def get_due_datetime(self):
        """Get the due date as a datetime object
        
        Returns:
            datetime: Due date
        """
        return datetime.strptime(self.due_date, "%Y-%m-%d")


class Reminder:
    """Reminder model"""
    
    def __init__(self, id, user_id, title, date, time, source_type, source_id):
        """Initialize a reminder
        
        Args:
            id (int): Reminder ID (None for new reminders)
            user_id (int): User ID
            title (str): Reminder title (from event or task)
            date (str): Reminder date (YYYY-MM-DD)
            time (str): Reminder time (HH:MM)
            source_type (str): Source type (event or task)
            source_id (int): Source ID (event_id or task_id)
        """
        self.id = id
        self.user_id = user_id
        self.title = title
        self.date = date
        self.time = time
        self.source_type = source_type
        self.source_id = source_id
    
    def __str__(self):
        return f"Reminder({self.id}, {self.title}, {self.date} {self.time}, {self.source_type})"
    
    def get_datetime(self):
        """Get the reminder date and time as a datetime object
        
        Returns:
            datetime: Reminder date and time
        """
        return datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
