#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar service for Persian Life Manager Application
"""

import os
import logging
from datetime import datetime, timedelta

from app.core.database import DatabaseManager
from app.models.calendar import Event, Task, Reminder

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for managing calendar data and time planning"""
    
    def __init__(self, user_id, db_path=None):
        """Initialize the calendar service
        
        Args:
            user_id (int): User ID
            db_path (str, optional): Path to the database file. If None, uses default path.
        """
        if not db_path:
            db_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', 'database.db')
        
        self.db_manager = DatabaseManager(db_path)
        self.user_id = user_id
    
    def get_events(self, limit=None):
        """Get calendar events for the user
        
        Args:
            limit (int, optional): Maximum number of events to return
            
        Returns:
            list: List of Event objects
        """
        try:
            query = """
                SELECT id, user_id, title, date, start_time, end_time, location, description, all_day, has_reminder
                FROM calendar_events
                WHERE user_id = ?
                ORDER BY date DESC, start_time, id DESC
            """
            
            if limit:
                query += " LIMIT ?"
                results = self.db_manager.execute_query(query, (self.user_id, limit))
            else:
                results = self.db_manager.execute_query(query, (self.user_id,))
            
            events = []
            for row in results:
                event = Event(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    location=row['location'],
                    description=row['description'],
                    all_day=bool(row['all_day']),
                    has_reminder=bool(row['has_reminder'])
                )
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return []
    
    def get_event(self, event_id):
        """Get a specific event by ID
        
        Args:
            event_id (int): Event ID
            
        Returns:
            Event: The event object, or None if not found
        """
        try:
            query = """
                SELECT id, user_id, title, date, start_time, end_time, location, description, all_day, has_reminder
                FROM calendar_events
                WHERE id = ? AND user_id = ?
            """
            
            results = self.db_manager.execute_query(query, (event_id, self.user_id))
            
            if not results:
                return None
            
            row = results[0]
            
            event = Event(
                id=row['id'],
                user_id=row['user_id'],
                title=row['title'],
                date=row['date'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                location=row['location'],
                description=row['description'],
                all_day=bool(row['all_day']),
                has_reminder=bool(row['has_reminder'])
            )
            
            return event
        except Exception as e:
            logger.error(f"Error getting event: {str(e)}")
            return None
    
    def get_events_for_date(self, date_str):
        """Get events for a specific date
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            list: List of Event objects for the specified date
        """
        try:
            query = """
                SELECT id, user_id, title, date, start_time, end_time, location, description, all_day, has_reminder
                FROM calendar_events
                WHERE user_id = ? AND date = ?
                ORDER BY all_day DESC, start_time, id
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, date_str))
            
            events = []
            for row in results:
                event = Event(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    location=row['location'],
                    description=row['description'],
                    all_day=bool(row['all_day']),
                    has_reminder=bool(row['has_reminder'])
                )
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting events for date: {str(e)}")
            return []
    
    def get_upcoming_events(self, limit=5):
        """Get upcoming events
        
        Args:
            limit (int, optional): Maximum number of events to return
            
        Returns:
            list: List of Event objects for upcoming events
        """
        try:
            today = datetime.now().date().isoformat()
            
            query = """
                SELECT id, user_id, title, date, start_time, end_time, location, description, all_day, has_reminder
                FROM calendar_events
                WHERE user_id = ? AND date >= ?
                ORDER BY date, start_time, id
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, today, limit))
            
            events = []
            for row in results:
                event = Event(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    location=row['location'],
                    description=row['description'],
                    all_day=bool(row['all_day']),
                    has_reminder=bool(row['has_reminder'])
                )
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting upcoming events: {str(e)}")
            return []
    
    def add_event(self, event, reminder_data=None):
        """Add a new event
        
        Args:
            event (Event): The event to add
            reminder_data (dict, optional): Dictionary with reminder data
                - value: Reminder value (e.g., 15)
                - unit: Reminder unit (e.g., 'minutes', 'hours', 'days')
            
        Returns:
            int: The ID of the new event, or None if adding failed
        """
        try:
            # Validate time if not all-day event
            if not event.all_day:
                if not event.start_time or not event.end_time:
                    raise ValueError("Start time and end time are required for non-all-day events.")
                
                # Convert times to datetime for comparison
                start_datetime = datetime.strptime(f"{event.date} {event.start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{event.date} {event.end_time}", "%Y-%m-%d %H:%M")
                
                if start_datetime >= end_datetime:
                    raise ValueError("End time must be after start time.")
            
            # Add the event
            query = """
                INSERT INTO calendar_events (
                    user_id, title, date, start_time, end_time, location, description, 
                    all_day, has_reminder, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            event_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, event.title, event.date, event.start_time, event.end_time,
                    event.location, event.description, int(event.all_day), 
                    int(event.has_reminder), now
                )
            )
            
            # Add reminder if needed
            if event.has_reminder and reminder_data:
                self.add_reminder_for_event(event_id, event.date, event.title, reminder_data)
            
            event.id = event_id
            return event_id
        except Exception as e:
            logger.error(f"Error adding event: {str(e)}")
            raise
    
    def update_event(self, event, reminder_data=None):
        """Update an event
        
        Args:
            event (Event): The event to update
            reminder_data (dict, optional): Dictionary with reminder data
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Check if event exists
            query = "SELECT id FROM calendar_events WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (event.id, self.user_id))
            
            if not results:
                raise ValueError(f"Event with ID {event.id} not found.")
            
            # Validate time if not all-day event
            if not event.all_day:
                if not event.start_time or not event.end_time:
                    raise ValueError("Start time and end time are required for non-all-day events.")
                
                # Convert times to datetime for comparison
                start_datetime = datetime.strptime(f"{event.date} {event.start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{event.date} {event.end_time}", "%Y-%m-%d %H:%M")
                
                if start_datetime >= end_datetime:
                    raise ValueError("End time must be after start time.")
            
            # Update the event
            query = """
                UPDATE calendar_events
                SET title = ?, date = ?, start_time = ?, end_time = ?, location = ?, 
                    description = ?, all_day = ?, has_reminder = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    event.title, event.date, event.start_time, event.end_time,
                    event.location, event.description, int(event.all_day),
                    int(event.has_reminder), event.id, self.user_id
                )
            )
            
            # Update reminder if needed
            if event.has_reminder:
                # First delete existing reminders
                self.delete_reminder_for_source('event', event.id)
                
                # Then add new reminder
                if reminder_data:
                    self.add_reminder_for_event(event.id, event.date, event.title, reminder_data)
            else:
                # Delete any existing reminders
                self.delete_reminder_for_source('event', event.id)
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            raise
    
    def delete_event(self, event_id):
        """Delete an event
        
        Args:
            event_id (int): The event ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if event exists
            query = "SELECT id FROM calendar_events WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (event_id, self.user_id))
            
            if not results:
                raise ValueError(f"Event with ID {event_id} not found.")
            
            # Delete associated reminders
            self.delete_reminder_for_source('event', event_id)
            
            # Delete the event
            query = "DELETE FROM calendar_events WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (event_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            raise
    
    def get_tasks(self, completed=None, limit=None):
        """Get tasks for the user
        
        Args:
            completed (bool, optional): Filter by completion status
            limit (int, optional): Maximum number of tasks to return
            
        Returns:
            list: List of Task objects
        """
        try:
            query_parts = [
                """
                SELECT id, user_id, title, due_date, priority, description, completed, 
                       completion_date, has_reminder
                FROM tasks
                WHERE user_id = ?
                """
            ]
            params = [self.user_id]
            
            if completed is not None:
                query_parts.append("AND completed = ?")
                params.append(int(completed))
            
            # Add ordering based on completion status
            if completed:
                query_parts.append("ORDER BY completion_date DESC, id DESC")
            else:
                query_parts.append("ORDER BY due_date, priority = 'high' DESC, priority = 'medium' DESC, id")
            
            if limit:
                query_parts.append("LIMIT ?")
                params.append(limit)
            
            query = " ".join(query_parts)
            results = self.db_manager.execute_query(query, tuple(params))
            
            tasks = []
            for row in results:
                task = Task(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    description=row['description'],
                    completed=bool(row['completed']),
                    completion_date=row['completion_date'],
                    has_reminder=bool(row['has_reminder'])
                )
                tasks.append(task)
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    def get_task(self, task_id):
        """Get a specific task by ID
        
        Args:
            task_id (int): Task ID
            
        Returns:
            Task: The task object, or None if not found
        """
        try:
            query = """
                SELECT id, user_id, title, due_date, priority, description, completed, 
                       completion_date, has_reminder
                FROM tasks
                WHERE id = ? AND user_id = ?
            """
            
            results = self.db_manager.execute_query(query, (task_id, self.user_id))
            
            if not results:
                return None
            
            row = results[0]
            
            task = Task(
                id=row['id'],
                user_id=row['user_id'],
                title=row['title'],
                due_date=row['due_date'],
                priority=row['priority'],
                description=row['description'],
                completed=bool(row['completed']),
                completion_date=row['completion_date'],
                has_reminder=bool(row['has_reminder'])
            )
            
            return task
        except Exception as e:
            logger.error(f"Error getting task: {str(e)}")
            return None
    
    def get_pending_tasks(self, limit=None):
        """Get pending (incomplete) tasks
        
        Args:
            limit (int, optional): Maximum number of tasks to return
            
        Returns:
            list: List of pending Task objects
        """
        return self.get_tasks(completed=False, limit=limit)
    
    def get_completed_tasks(self, limit=None):
        """Get completed tasks
        
        Args:
            limit (int, optional): Maximum number of tasks to return
            
        Returns:
            list: List of completed Task objects
        """
        return self.get_tasks(completed=True, limit=limit)
    
    def get_today_tasks(self):
        """Get tasks due today
        
        Returns:
            list: List of Task objects due today
        """
        try:
            today = datetime.now().date().isoformat()
            
            query = """
                SELECT id, user_id, title, due_date, priority, description, completed, 
                       completion_date, has_reminder
                FROM tasks
                WHERE user_id = ? AND due_date = ?
                ORDER BY priority = 'high' DESC, priority = 'medium' DESC, id
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, today))
            
            tasks = []
            for row in results:
                task = Task(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    due_date=row['due_date'],
                    priority=row['priority'],
                    description=row['description'],
                    completed=bool(row['completed']),
                    completion_date=row['completion_date'],
                    has_reminder=bool(row['has_reminder'])
                )
                tasks.append(task)
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting today's tasks: {str(e)}")
            return []
    
    def add_task(self, task, reminder_data=None):
        """Add a new task
        
        Args:
            task (Task): The task to add
            reminder_data (dict, optional): Dictionary with reminder data
                - value: Reminder value (e.g., 15)
                - unit: Reminder unit (e.g., 'minutes', 'hours', 'days')
            
        Returns:
            int: The ID of the new task, or None if adding failed
        """
        try:
            # Validate priority
            if task.priority not in ['low', 'medium', 'high']:
                raise ValueError("Invalid priority. Must be 'low', 'medium', or 'high'.")
            
            # Add the task
            query = """
                INSERT INTO tasks (
                    user_id, title, due_date, priority, description, completed, 
                    completion_date, has_reminder, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            task_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, task.title, task.due_date, task.priority, task.description,
                    int(task.completed), task.completion_date, int(task.has_reminder), now
                )
            )
            
            # Add reminder if needed
            if task.has_reminder and reminder_data:
                self.add_reminder_for_task(task_id, task.due_date, task.title, reminder_data)
            
            task.id = task_id
            return task_id
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            raise
    
    def update_task(self, task, reminder_data=None):
        """Update a task
        
        Args:
            task (Task): The task to update
            reminder_data (dict, optional): Dictionary with reminder data
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Check if task exists
            query = "SELECT id FROM tasks WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (task.id, self.user_id))
            
            if not results:
                raise ValueError(f"Task with ID {task.id} not found.")
            
            # Validate priority
            if task.priority not in ['low', 'medium', 'high']:
                raise ValueError("Invalid priority. Must be 'low', 'medium', or 'high'.")
            
            # Update the task
            query = """
                UPDATE tasks
                SET title = ?, due_date = ?, priority = ?, description = ?, 
                    completed = ?, completion_date = ?, has_reminder = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    task.title, task.due_date, task.priority, task.description,
                    int(task.completed), task.completion_date, int(task.has_reminder),
                    task.id, self.user_id
                )
            )
            
            # Update reminder if needed
            if task.has_reminder:
                # First delete existing reminders
                self.delete_reminder_for_source('task', task.id)
                
                # Then add new reminder
                if reminder_data:
                    self.add_reminder_for_task(task.id, task.due_date, task.title, reminder_data)
            else:
                # Delete any existing reminders
                self.delete_reminder_for_source('task', task.id)
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            raise
    
    def delete_task(self, task_id):
        """Delete a task
        
        Args:
            task_id (int): The task ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if task exists
            query = "SELECT id FROM tasks WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (task_id, self.user_id))
            
            if not results:
                raise ValueError(f"Task with ID {task_id} not found.")
            
            # Delete associated reminders
            self.delete_reminder_for_source('task', task_id)
            
            # Delete the task
            query = "DELETE FROM tasks WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (task_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            raise
    
    def complete_task(self, task_id):
        """Mark a task as completed
        
        Args:
            task_id (int): The task ID to mark as completed
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Check if task exists
            query = "SELECT id FROM tasks WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (task_id, self.user_id))
            
            if not results:
                raise ValueError(f"Task with ID {task_id} not found.")
            
            # Mark the task as completed
            now = datetime.now().date().isoformat()
            query = """
                UPDATE tasks
                SET completed = 1, completion_date = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(query, (now, task_id, self.user_id))
            
            # Delete associated reminders (no need for reminders for completed tasks)
            self.delete_reminder_for_source('task', task_id)
            
            return result > 0
        except Exception as e:
            logger.error(f"Error completing task: {str(e)}")
            raise
    
    def restore_task(self, task_id):
        """Restore a completed task to pending status
        
        Args:
            task_id (int): The task ID to restore
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Check if task exists
            query = "SELECT id, due_date, has_reminder FROM tasks WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (task_id, self.user_id))
            
            if not results:
                raise ValueError(f"Task with ID {task_id} not found.")
            
            # Restore the task
            query = """
                UPDATE tasks
                SET completed = 0, completion_date = NULL
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(query, (task_id, self.user_id))
            
            # Re-add reminder if the task had one
            if bool(results[0]['has_reminder']):
                due_date = results[0]['due_date']
                # We need the task title
                task_query = "SELECT title FROM tasks WHERE id = ?"
                task_result = self.db_manager.execute_query(task_query, (task_id,))
                
                if task_result:
                    task_title = task_result[0]['title']
                    reminder_data = {'value': 15, 'unit': 'دقیقه'}  # Default reminder (15 minutes before)
                    self.add_reminder_for_task(task_id, due_date, task_title, reminder_data)
            
            return result > 0
        except Exception as e:
            logger.error(f"Error restoring task: {str(e)}")
            raise
    
    def get_reminders(self):
        """Get all reminders for the user
        
        Returns:
            list: List of Reminder objects
        """
        try:
            query = """
                SELECT r.id, r.user_id, r.source_type, r.source_id, r.reminder_time, r.status,
                       CASE
                           WHEN r.source_type = 'event' THEN e.title
                           WHEN r.source_type = 'task' THEN t.title
                           ELSE NULL
                       END as title
                FROM reminders r
                LEFT JOIN calendar_events e ON r.source_type = 'event' AND r.source_id = e.id
                LEFT JOIN tasks t ON r.source_type = 'task' AND r.source_id = t.id
                WHERE r.user_id = ?
                ORDER BY r.reminder_time
            """
            
            results = self.db_manager.execute_query(query, (self.user_id,))
            
            reminders = []
            for row in results:
                reminder_time = datetime.fromisoformat(row['reminder_time'])
                reminder = Reminder(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=reminder_time.date().isoformat(),
                    time=reminder_time.strftime("%H:%M"),
                    source_type=row['source_type'],
                    source_id=row['source_id']
                )
                reminders.append(reminder)
            
            return reminders
        except Exception as e:
            logger.error(f"Error getting reminders: {str(e)}")
            return []
    
    def get_today_reminders(self):
        """Get reminders for today
        
        Returns:
            list: List of Reminder objects for today
        """
        try:
            today = datetime.now().date().isoformat()
            
            query = """
                SELECT r.id, r.user_id, r.source_type, r.source_id, r.reminder_time, r.status,
                       CASE
                           WHEN r.source_type = 'event' THEN e.title
                           WHEN r.source_type = 'task' THEN t.title
                           ELSE NULL
                       END as title
                FROM reminders r
                LEFT JOIN calendar_events e ON r.source_type = 'event' AND r.source_id = e.id
                LEFT JOIN tasks t ON r.source_type = 'task' AND r.source_id = t.id
                WHERE r.user_id = ? AND date(r.reminder_time) = ?
                ORDER BY r.reminder_time
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, today))
            
            reminders = []
            for row in results:
                reminder_time = datetime.fromisoformat(row['reminder_time'])
                reminder = Reminder(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=reminder_time.date().isoformat(),
                    time=reminder_time.strftime("%H:%M"),
                    source_type=row['source_type'],
                    source_id=row['source_id']
                )
                reminders.append(reminder)
            
            return reminders
        except Exception as e:
            logger.error(f"Error getting today's reminders: {str(e)}")
            return []
    
    def get_upcoming_reminders(self, limit=5):
        """Get upcoming reminders
        
        Args:
            limit (int, optional): Maximum number of reminders to return
            
        Returns:
            list: List of Reminder objects for upcoming reminders
        """
        try:
            now = datetime.now().isoformat()
            
            query = """
                SELECT r.id, r.user_id, r.source_type, r.source_id, r.reminder_time, r.status,
                       CASE
                           WHEN r.source_type = 'event' THEN e.title
                           WHEN r.source_type = 'task' THEN t.title
                           ELSE NULL
                       END as title
                FROM reminders r
                LEFT JOIN calendar_events e ON r.source_type = 'event' AND r.source_id = e.id
                LEFT JOIN tasks t ON r.source_type = 'task' AND r.source_id = t.id
                WHERE r.user_id = ? AND r.reminder_time > ?
                ORDER BY r.reminder_time
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(query, (self.user_id, now, limit))
            
            reminders = []
            for row in results:
                reminder_time = datetime.fromisoformat(row['reminder_time'])
                reminder = Reminder(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    date=reminder_time.date().isoformat(),
                    time=reminder_time.strftime("%H:%M"),
                    source_type=row['source_type'],
                    source_id=row['source_id']
                )
                reminders.append(reminder)
            
            return reminders
        except Exception as e:
            logger.error(f"Error getting upcoming reminders: {str(e)}")
            return []
    
    def delete_reminder(self, reminder_id):
        """Delete a reminder
        
        Args:
            reminder_id (int): The reminder ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if reminder exists
            query = "SELECT id FROM reminders WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (reminder_id, self.user_id))
            
            if not results:
                raise ValueError(f"Reminder with ID {reminder_id} not found.")
            
            # Delete the reminder
            query = "DELETE FROM reminders WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (reminder_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting reminder: {str(e)}")
            raise
    
    def delete_reminder_for_source(self, source_type, source_id):
        """Delete reminders for a specific source
        
        Args:
            source_type (str): Source type ('event' or 'task')
            source_id (int): Source ID
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Delete the reminders
            query = """
                DELETE FROM reminders
                WHERE user_id = ? AND source_type = ? AND source_id = ?
            """
            
            result = self.db_manager.execute_update(query, (self.user_id, source_type, source_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting reminders for source: {str(e)}")
            raise
    
    def add_reminder_for_event(self, event_id, event_date, event_title, reminder_data):
        """Add a reminder for an event
        
        Args:
            event_id (int): Event ID
            event_date (str): Event date (YYYY-MM-DD)
            event_title (str): Event title
            reminder_data (dict): Dictionary with reminder data
                - value: Reminder value (e.g., 15)
                - unit: Reminder unit (e.g., 'دقیقه', 'ساعت', 'روز')
            
        Returns:
            int: The ID of the new reminder, or None if adding failed
        """
        try:
            # Get the event details
            query = "SELECT date, start_time, all_day FROM calendar_events WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (event_id, self.user_id))
            
            if not results:
                raise ValueError(f"Event with ID {event_id} not found.")
            
            row = results[0]
            event_date = row['date']
            
            # Calculate reminder time
            if row['all_day']:
                # For all-day events, set reminder at 9:00 AM
                event_datetime = datetime.strptime(f"{event_date} 09:00", "%Y-%m-%d %H:%M")
            else:
                # For regular events, use the start time
                event_datetime = datetime.strptime(f"{event_date} {row['start_time']}", "%Y-%m-%d %H:%M")
            
            # Calculate reminder time based on unit
            value = int(reminder_data['value'])
            unit = reminder_data['unit']
            
            if unit == 'دقیقه':
                reminder_time = event_datetime - timedelta(minutes=value)
            elif unit == 'ساعت':
                reminder_time = event_datetime - timedelta(hours=value)
            elif unit == 'روز':
                reminder_time = event_datetime - timedelta(days=value)
            else:
                # Default to 15 minutes before
                reminder_time = event_datetime - timedelta(minutes=15)
            
            # Add the reminder
            query = """
                INSERT INTO reminders (
                    user_id, source_type, source_id, reminder_time, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            reminder_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, 'event', event_id, reminder_time.isoformat(),
                    'pending', now
                )
            )
            
            return reminder_id
        except Exception as e:
            logger.error(f"Error adding reminder for event: {str(e)}")
            raise
    
    def add_reminder_for_task(self, task_id, task_due_date, task_title, reminder_data):
        """Add a reminder for a task
        
        Args:
            task_id (int): Task ID
            task_due_date (str): Task due date (YYYY-MM-DD)
            task_title (str): Task title
            reminder_data (dict): Dictionary with reminder data
                - value: Reminder value (e.g., 15)
                - unit: Reminder unit (e.g., 'دقیقه', 'ساعت', 'روز')
            
        Returns:
            int: The ID of the new reminder, or None if adding failed
        """
        try:
            # Check if task exists
            query = "SELECT id FROM tasks WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (task_id, self.user_id))
            
            if not results:
                raise ValueError(f"Task with ID {task_id} not found.")
            
            # Calculate reminder time
            # For tasks, set reminder at 9:00 AM on the due date by default
            task_datetime = datetime.strptime(f"{task_due_date} 09:00", "%Y-%m-%d %H:%M")
            
            # Calculate reminder time based on unit
            value = int(reminder_data['value'])
            unit = reminder_data['unit']
            
            if unit == 'دقیقه':
                reminder_time = task_datetime - timedelta(minutes=value)
            elif unit == 'ساعت':
                reminder_time = task_datetime - timedelta(hours=value)
            elif unit == 'روز':
                reminder_time = task_datetime - timedelta(days=value)
            else:
                # Default to 15 minutes before
                reminder_time = task_datetime - timedelta(minutes=15)
            
            # Add the reminder
            query = """
                INSERT INTO reminders (
                    user_id, source_type, source_id, reminder_time, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            reminder_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, 'task', task_id, reminder_time.isoformat(),
                    'pending', now
                )
            )
            
            return reminder_id
        except Exception as e:
            logger.error(f"Error adding reminder for task: {str(e)}")
            raise
    
    def get_reminder_preferences(self):
        """Get reminder preferences for the user
        
        Returns:
            dict: Dictionary with reminder preferences
        """
        try:
            # Get enable_notifications setting
            enable_query = """
                SELECT setting_value
                FROM user_settings
                WHERE user_id = ? AND setting_key = 'enable_notifications'
            """
            
            enable_result = self.db_manager.execute_query(enable_query, (self.user_id,))
            
            # Get default_reminder_time setting
            time_query = """
                SELECT setting_value
                FROM user_settings
                WHERE user_id = ? AND setting_key = 'default_reminder_time'
            """
            
            time_result = self.db_manager.execute_query(time_query, (self.user_id,))
            
            # Default values
            enable_notifications = True
            default_reminder_time = 15
            
            # Parse results
            if enable_result:
                enable_notifications = enable_result[0]['setting_value'].lower() == 'true'
            
            if time_result:
                try:
                    default_reminder_time = int(time_result[0]['setting_value'])
                except (ValueError, TypeError):
                    default_reminder_time = 15
            
            return {
                'enable_notifications': enable_notifications,
                'default_reminder_time': default_reminder_time
            }
        except Exception as e:
            logger.error(f"Error getting reminder preferences: {str(e)}")
            return {
                'enable_notifications': True,
                'default_reminder_time': 15
            }
    
    def save_reminder_preferences(self, preferences):
        """Save reminder preferences for the user
        
        Args:
            preferences (dict): Dictionary with reminder preferences
                - enable_notifications (bool): Whether to enable notifications
                - default_reminder_time (int): Default reminder time in minutes
            
        Returns:
            bool: True if save was successful
        """
        try:
            # Convert values to strings for storage
            enable_value = str(preferences.get('enable_notifications', True)).lower()
            time_value = str(preferences.get('default_reminder_time', 15))
            
            # Current timestamp
            now = datetime.now().isoformat()
            
            # Save enable_notifications setting
            enable_query = """
                INSERT OR REPLACE INTO user_settings (user_id, setting_key, setting_value, created_at)
                VALUES (?, 'enable_notifications', ?, ?)
            """
            
            self.db_manager.execute_update(enable_query, (self.user_id, enable_value, now))
            
            # Save default_reminder_time setting
            time_query = """
                INSERT OR REPLACE INTO user_settings (user_id, setting_key, setting_value, created_at)
                VALUES (?, 'default_reminder_time', ?, ?)
            """
            
            self.db_manager.execute_update(time_query, (self.user_id, time_value, now))
            
            return True
        except Exception as e:
            logger.error(f"Error saving reminder preferences: {str(e)}")
            return False
