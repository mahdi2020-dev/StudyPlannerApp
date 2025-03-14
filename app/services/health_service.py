#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Health service for Persian Life Manager Application
"""

import os
import logging
from datetime import datetime, timedelta

from app.core.database import DatabaseManager
from app.models.health import Exercise, HealthMetric, HealthGoal

logger = logging.getLogger(__name__)

class HealthService:
    """Service for managing health data"""
    
    def __init__(self, user_id, db_path=None):
        """Initialize the health service
        
        Args:
            user_id (int): User ID
            db_path (str, optional): Path to the database file. If None, uses default path.
        """
        if not db_path:
            db_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', 'database.db')
        
        self.db_manager = DatabaseManager(db_path)
        self.user_id = user_id
    
    def get_exercises(self, limit=None):
        """Get exercises for the user
        
        Args:
            limit (int, optional): Maximum number of exercises to return
            
        Returns:
            list: List of Exercise objects
        """
        try:
            query = """
                SELECT id, user_id, exercise_type, duration, calories_burned, date, notes
                FROM health_exercises
                WHERE user_id = ?
                ORDER BY date DESC, id DESC
            """
            
            if limit:
                query += " LIMIT ?"
                results = self.db_manager.execute_query(query, (self.user_id, limit))
            else:
                results = self.db_manager.execute_query(query, (self.user_id,))
            
            exercises = []
            for row in results:
                exercise = Exercise(
                    id=row['id'],
                    user_id=row['user_id'],
                    exercise_type=row['exercise_type'],
                    duration=row['duration'],
                    calories_burned=row['calories_burned'],
                    date=row['date'],
                    notes=row['notes']
                )
                exercises.append(exercise)
            
            return exercises
        except Exception as e:
            logger.error(f"Error getting exercises: {str(e)}")
            return []
    
    def add_exercise(self, exercise):
        """Add a new exercise
        
        Args:
            exercise (Exercise): The exercise to add
            
        Returns:
            int: The ID of the new exercise, or None if adding failed
        """
        try:
            # Validate data
            if exercise.duration <= 0:
                raise ValueError("Exercise duration must be positive.")
            
            if exercise.calories_burned < 0:
                raise ValueError("Calories burned cannot be negative.")
            
            # Add the exercise
            query = """
                INSERT INTO health_exercises (
                    user_id, exercise_type, duration, calories_burned, date, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            exercise_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, exercise.exercise_type, exercise.duration,
                    exercise.calories_burned, exercise.date, exercise.notes, now
                )
            )
            
            # Update goals progress after adding exercise
            self.update_goal_progress()
            
            exercise.id = exercise_id
            return exercise_id
        except Exception as e:
            logger.error(f"Error adding exercise: {str(e)}")
            raise
    
    def update_exercise(self, exercise):
        """Update an exercise
        
        Args:
            exercise (Exercise): The exercise to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate data
            if exercise.duration <= 0:
                raise ValueError("Exercise duration must be positive.")
            
            if exercise.calories_burned < 0:
                raise ValueError("Calories burned cannot be negative.")
            
            # Check if exercise exists
            query = "SELECT id FROM health_exercises WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (exercise.id, self.user_id))
            
            if not results:
                raise ValueError(f"Exercise with ID {exercise.id} not found.")
            
            # Update the exercise
            query = """
                UPDATE health_exercises
                SET exercise_type = ?, duration = ?, calories_burned = ?, date = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    exercise.exercise_type, exercise.duration, exercise.calories_burned,
                    exercise.date, exercise.notes, exercise.id, self.user_id
                )
            )
            
            # Update goals progress after updating exercise
            self.update_goal_progress()
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating exercise: {str(e)}")
            raise
    
    def delete_exercise(self, exercise_id):
        """Delete an exercise
        
        Args:
            exercise_id (int): The exercise ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if exercise exists
            query = "SELECT id FROM health_exercises WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (exercise_id, self.user_id))
            
            if not results:
                raise ValueError(f"Exercise with ID {exercise_id} not found.")
            
            # Delete the exercise
            query = "DELETE FROM health_exercises WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (exercise_id, self.user_id))
            
            # Update goals progress after deleting exercise
            self.update_goal_progress()
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting exercise: {str(e)}")
            raise
    
    def get_metrics(self, limit=None):
        """Get health metrics for the user
        
        Args:
            limit (int, optional): Maximum number of metrics to return
            
        Returns:
            list: List of HealthMetric objects
        """
        try:
            query = """
                SELECT id, user_id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes
                FROM health_metrics
                WHERE user_id = ?
                ORDER BY date DESC, id DESC
            """
            
            if limit:
                query += " LIMIT ?"
                results = self.db_manager.execute_query(query, (self.user_id, limit))
            else:
                results = self.db_manager.execute_query(query, (self.user_id,))
            
            metrics = []
            for row in results:
                metric = HealthMetric(
                    id=row['id'],
                    user_id=row['user_id'],
                    date=row['date'],
                    weight=row['weight'],
                    systolic=row['systolic'],
                    diastolic=row['diastolic'],
                    heart_rate=row['heart_rate'],
                    sleep_hours=row['sleep_hours'],
                    notes=row['notes']
                )
                metrics.append(metric)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting health metrics: {str(e)}")
            return []
    
    def get_latest_metrics(self):
        """Get the most recent health metrics for the user
        
        Returns:
            HealthMetric: The most recent health metric, or None if not found
        """
        try:
            metrics = self.get_metrics(limit=1)
            if metrics:
                return metrics[0]
            return None
        except Exception as e:
            logger.error(f"Error getting latest metrics: {str(e)}")
            return None
    
    def add_metrics(self, metrics):
        """Add new health metrics
        
        Args:
            metrics (HealthMetric): The health metrics to add
            
        Returns:
            int: The ID of the new metrics, or None if adding failed
        """
        try:
            # Validate data
            if metrics.weight and metrics.weight <= 0:
                raise ValueError("Weight must be positive.")
            
            if metrics.systolic and metrics.diastolic and metrics.systolic <= metrics.diastolic:
                raise ValueError("Systolic pressure must be greater than diastolic pressure.")
            
            if metrics.heart_rate and metrics.heart_rate <= 0:
                raise ValueError("Heart rate must be positive.")
            
            if metrics.sleep_hours and metrics.sleep_hours < 0:
                raise ValueError("Sleep hours cannot be negative.")
            
            # Add the metrics
            query = """
                INSERT INTO health_metrics (
                    user_id, date, weight, systolic, diastolic, heart_rate, sleep_hours, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            metrics_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, metrics.date, metrics.weight, metrics.systolic,
                    metrics.diastolic, metrics.heart_rate, metrics.sleep_hours,
                    metrics.notes, now
                )
            )
            
            # Update goals progress after adding metrics
            self.update_goal_progress()
            
            metrics.id = metrics_id
            return metrics_id
        except Exception as e:
            logger.error(f"Error adding health metrics: {str(e)}")
            raise
    
    def update_metrics(self, metrics):
        """Update health metrics
        
        Args:
            metrics (HealthMetric): The health metrics to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate data
            if metrics.weight and metrics.weight <= 0:
                raise ValueError("Weight must be positive.")
            
            if metrics.systolic and metrics.diastolic and metrics.systolic <= metrics.diastolic:
                raise ValueError("Systolic pressure must be greater than diastolic pressure.")
            
            if metrics.heart_rate and metrics.heart_rate <= 0:
                raise ValueError("Heart rate must be positive.")
            
            if metrics.sleep_hours and metrics.sleep_hours < 0:
                raise ValueError("Sleep hours cannot be negative.")
            
            # Check if metrics exists
            query = "SELECT id FROM health_metrics WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (metrics.id, self.user_id))
            
            if not results:
                raise ValueError(f"Health metrics with ID {metrics.id} not found.")
            
            # Update the metrics
            query = """
                UPDATE health_metrics
                SET date = ?, weight = ?, systolic = ?, diastolic = ?, heart_rate = ?, sleep_hours = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    metrics.date, metrics.weight, metrics.systolic, metrics.diastolic,
                    metrics.heart_rate, metrics.sleep_hours, metrics.notes,
                    metrics.id, self.user_id
                )
            )
            
            # Update goals progress after updating metrics
            self.update_goal_progress()
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating health metrics: {str(e)}")
            raise
    
    def delete_metric(self, metric_id):
        """Delete health metrics
        
        Args:
            metric_id (int): The metric ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if metrics exists
            query = "SELECT id FROM health_metrics WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (metric_id, self.user_id))
            
            if not results:
                raise ValueError(f"Health metrics with ID {metric_id} not found.")
            
            # Delete the metrics
            query = "DELETE FROM health_metrics WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (metric_id, self.user_id))
            
            # Update goals progress after deleting metrics
            self.update_goal_progress()
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting health metrics: {str(e)}")
            raise
    
    def get_goals(self):
        """Get health goals for the user
        
        Returns:
            list: List of HealthGoal objects
        """
        try:
            query = """
                SELECT id, user_id, goal_type, target_value, deadline, progress, notes
                FROM health_goals
                WHERE user_id = ?
                ORDER BY deadline, id
            """
            
            results = self.db_manager.execute_query(query, (self.user_id,))
            
            goals = []
            for row in results:
                goal = HealthGoal(
                    id=row['id'],
                    user_id=row['user_id'],
                    goal_type=row['goal_type'],
                    target_value=row['target_value'],
                    deadline=row['deadline'],
                    progress=row['progress'],
                    notes=row['notes']
                )
                goals.append(goal)
            
            return goals
        except Exception as e:
            logger.error(f"Error getting health goals: {str(e)}")
            return []
    
    def add_goal(self, goal):
        """Add a new health goal
        
        Args:
            goal (HealthGoal): The health goal to add
            
        Returns:
            int: The ID of the new goal, or None if adding failed
        """
        try:
            # Validate data
            if goal.target_value <= 0:
                raise ValueError("Goal target value must be positive.")
            
            # Add the goal
            query = """
                INSERT INTO health_goals (
                    user_id, goal_type, target_value, deadline, progress, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            goal_id = self.db_manager.execute_insert(
                query, (
                    self.user_id, goal.goal_type, goal.target_value,
                    goal.deadline, goal.progress, goal.notes, now
                )
            )
            
            # Update this goal's progress based on current data
            goal.id = goal_id
            self.update_specific_goal_progress(goal)
            
            return goal_id
        except Exception as e:
            logger.error(f"Error adding health goal: {str(e)}")
            raise
    
    def update_goal(self, goal):
        """Update a health goal
        
        Args:
            goal (HealthGoal): The health goal to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate data
            if goal.target_value <= 0:
                raise ValueError("Goal target value must be positive.")
            
            # Check if goal exists
            query = "SELECT id FROM health_goals WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (goal.id, self.user_id))
            
            if not results:
                raise ValueError(f"Health goal with ID {goal.id} not found.")
            
            # Update the goal
            query = """
                UPDATE health_goals
                SET goal_type = ?, target_value = ?, deadline = ?, progress = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """
            
            result = self.db_manager.execute_update(
                query, (
                    goal.goal_type, goal.target_value, goal.deadline,
                    goal.progress, goal.notes, goal.id, self.user_id
                )
            )
            
            return result > 0
        except Exception as e:
            logger.error(f"Error updating health goal: {str(e)}")
            raise
    
    def delete_goal(self, goal_id):
        """Delete a health goal
        
        Args:
            goal_id (int): The goal ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if goal exists
            query = "SELECT id FROM health_goals WHERE id = ? AND user_id = ?"
            results = self.db_manager.execute_query(query, (goal_id, self.user_id))
            
            if not results:
                raise ValueError(f"Health goal with ID {goal_id} not found.")
            
            # Delete the goal
            query = "DELETE FROM health_goals WHERE id = ? AND user_id = ?"
            result = self.db_manager.execute_update(query, (goal_id, self.user_id))
            
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting health goal: {str(e)}")
            raise
    
    def update_goal_progress(self):
        """Update the progress of all health goals based on current data"""
        try:
            goals = self.get_goals()
            for goal in goals:
                self.update_specific_goal_progress(goal)
        except Exception as e:
            logger.error(f"Error updating goal progress: {str(e)}")
    
    def update_specific_goal_progress(self, goal):
        """Update the progress of a specific health goal
        
        Args:
            goal (HealthGoal): The goal to update
        """
        try:
            progress = 0
            
            # Calculate progress based on goal type
            if goal.goal_type == "وزن":
                # Get latest weight
                latest_metrics = self.get_latest_metrics()
                if latest_metrics and latest_metrics.weight:
                    # Get the starting weight
                    oldest_query = """
                        SELECT weight
                        FROM health_metrics
                        WHERE user_id = ? AND weight IS NOT NULL
                        ORDER BY date ASC
                        LIMIT 1
                    """
                    oldest_result = self.db_manager.execute_query(oldest_query, (self.user_id,))
                    
                    if oldest_result:
                        start_weight = oldest_result[0]['weight']
                        current_weight = latest_metrics.weight
                        
                        # Calculate how close we are to target
                        if start_weight > goal.target_value:  # Weight loss
                            weight_loss_needed = start_weight - goal.target_value
                            weight_loss_achieved = start_weight - current_weight
                            if weight_loss_needed > 0:
                                progress = min(100, (weight_loss_achieved / weight_loss_needed) * 100)
                        else:  # Weight gain
                            weight_gain_needed = goal.target_value - start_weight
                            weight_gain_achieved = current_weight - start_weight
                            if weight_gain_needed > 0:
                                progress = min(100, (weight_gain_achieved / weight_gain_needed) * 100)
            
            elif goal.goal_type == "ورزش هفتگی":
                # Count weekly exercise sessions
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                
                exercise_query = """
                    SELECT COUNT(*) as count
                    FROM health_exercises
                    WHERE user_id = ? AND date BETWEEN ? AND ?
                """
                exercise_result = self.db_manager.execute_query(
                    exercise_query, (self.user_id, week_start.isoformat(), week_end.isoformat())
                )
                
                if exercise_result:
                    weekly_exercises = exercise_result[0]['count']
                    progress = min(100, (weekly_exercises / goal.target_value) * 100)
            
            elif goal.goal_type == "کالری مصرفی هفتگی":
                # Calculate weekly calories burned
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                
                calories_query = """
                    SELECT SUM(calories_burned) as total
                    FROM health_exercises
                    WHERE user_id = ? AND date BETWEEN ? AND ?
                """
                calories_result = self.db_manager.execute_query(
                    calories_query, (self.user_id, week_start.isoformat(), week_end.isoformat())
                )
                
                if calories_result and calories_result[0]['total']:
                    weekly_calories = calories_result[0]['total']
                    progress = min(100, (weekly_calories / goal.target_value) * 100)
            
            elif goal.goal_type == "مدت خواب روزانه":
                # Get average sleep hours from recent metrics
                sleep_query = """
                    SELECT AVG(sleep_hours) as avg_sleep
                    FROM health_metrics
                    WHERE user_id = ? AND sleep_hours IS NOT NULL
                    ORDER BY date DESC
                    LIMIT 7
                """
                sleep_result = self.db_manager.execute_query(sleep_query, (self.user_id,))
                
                if sleep_result and sleep_result[0]['avg_sleep']:
                    avg_sleep = sleep_result[0]['avg_sleep']
                    progress = min(100, (avg_sleep / goal.target_value) * 100)
            
            elif goal.goal_type == "تعداد قدم روزانه":
                # This would require specific step tracking, which we're not directly implementing
                # For now, we'll just leave the progress as it is
                pass
            
            # Update the goal progress in the database
            if progress > 0:
                update_query = """
                    UPDATE health_goals
                    SET progress = ?
                    WHERE id = ? AND user_id = ?
                """
                self.db_manager.execute_update(update_query, (progress, goal.id, self.user_id))
        except Exception as e:
            logger.error(f"Error updating goal progress: {str(e)}")
    
    def get_weekly_summary(self):
        """Get summary of health activities for the current week
        
        Returns:
            dict: Dictionary with weekly health summary
        """
        try:
            # Calculate date range for current week
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Count weekly exercises
            exercise_query = """
                SELECT COUNT(*) as count
                FROM health_exercises
                WHERE user_id = ? AND date BETWEEN ? AND ?
            """
            exercise_result = self.db_manager.execute_query(
                exercise_query, (self.user_id, week_start.isoformat(), week_end.isoformat())
            )
            
            # Calculate total calories burned
            calories_query = """
                SELECT SUM(calories_burned) as total
                FROM health_exercises
                WHERE user_id = ? AND date BETWEEN ? AND ?
            """
            calories_result = self.db_manager.execute_query(
                calories_query, (self.user_id, week_start.isoformat(), week_end.isoformat())
            )
            
            # Get total exercise minutes
            duration_query = """
                SELECT SUM(duration) as total
                FROM health_exercises
                WHERE user_id = ? AND date BETWEEN ? AND ?
            """
            duration_result = self.db_manager.execute_query(
                duration_query, (self.user_id, week_start.isoformat(), week_end.isoformat())
            )
            
            # Get results
            exercise_count = exercise_result[0]['count'] if exercise_result[0]['count'] else 0
            calories_burned = calories_result[0]['total'] if calories_result[0]['total'] else 0
            total_duration = duration_result[0]['total'] if duration_result[0]['total'] else 0
            
            return {
                'exercise_count': exercise_count,
                'calories_burned': calories_burned,
                'total_duration': total_duration,
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting weekly summary: {str(e)}")
            return {
                'exercise_count': 0,
                'calories_burned': 0,
                'total_duration': 0,
                'week_start': '',
                'week_end': ''
            }
    
    def get_latest_blood_pressure(self):
        """Get the most recent blood pressure reading
        
        Returns:
            dict: Dictionary with systolic and diastolic values
        """
        try:
            query = """
                SELECT systolic, diastolic
                FROM health_metrics
                WHERE user_id = ? AND systolic IS NOT NULL AND diastolic IS NOT NULL
                ORDER BY date DESC, id DESC
                LIMIT 1
            """
            
            result = self.db_manager.execute_query(query, (self.user_id,))
            
            if result:
                return {
                    'systolic': result[0]['systolic'],
                    'diastolic': result[0]['diastolic']
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting latest blood pressure: {str(e)}")
            return None
    
    def get_exercise_trend(self, days=30):
        """Get exercise trend for the last N days
        
        Args:
            days (int, optional): Number of days to include
            
        Returns:
            list: List of dictionaries with date and duration
        """
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            query = """
                SELECT date, SUM(duration) as duration
                FROM health_exercises
                WHERE user_id = ? AND date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date
            """
            
            results = self.db_manager.execute_query(
                query, (self.user_id, start_date.isoformat(), end_date.isoformat())
            )
            
            # Format results
            trend_data = []
            for row in results:
                trend_data.append({
                    'date': row['date'],
                    'duration': row['duration']
                })
            
            return trend_data
        except Exception as e:
            logger.error(f"Error getting exercise trend: {str(e)}")
            return []
    
    def get_weight_trend(self):
        """Get weight trend over time
        
        Returns:
            list: List of dictionaries with date and weight
        """
        try:
            query = """
                SELECT date, weight
                FROM health_metrics
                WHERE user_id = ? AND weight IS NOT NULL
                ORDER BY date
            """
            
            results = self.db_manager.execute_query(query, (self.user_id,))
            
            # Format results
            trend_data = []
            for row in results:
                trend_data.append({
                    'date': row['date'],
                    'weight': row['weight']
                })
            
            return trend_data
        except Exception as e:
            logger.error(f"Error getting weight trend: {str(e)}")
            return []
