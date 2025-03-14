#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Health-related data models for Persian Life Manager Application
"""

class Exercise:
    """Exercise model"""
    
    def __init__(self, id, user_id, date, exercise_type, duration, calories_burned, notes=None):
        """Initialize an exercise
        
        Args:
            id (int): Exercise ID (None for new exercises)
            user_id (int): User ID
            date (str): Exercise date (YYYY-MM-DD)
            exercise_type (str): Type of exercise (e.g. walking, running, swimming)
            duration (int): Duration in minutes
            calories_burned (int): Calories burned
            notes (str, optional): Notes about the exercise
        """
        self.id = id
        self.user_id = user_id
        self.date = date
        self.exercise_type = exercise_type
        self.duration = duration
        self.calories_burned = calories_burned
        self.notes = notes or ""
    
    def __str__(self):
        return f"Exercise({self.id}, {self.exercise_type}, {self.duration} min, {self.date})"


class HealthMetric:
    """Health metrics model"""
    
    def __init__(self, id, user_id, date, weight=None, systolic=None, 
                 diastolic=None, heart_rate=None, sleep_hours=None, notes=None):
        """Initialize health metrics
        
        Args:
            id (int): Metric ID (None for new metrics)
            user_id (int): User ID
            date (str): Measurement date (YYYY-MM-DD)
            weight (float, optional): Weight in kg
            systolic (int, optional): Systolic blood pressure
            diastolic (int, optional): Diastolic blood pressure
            heart_rate (int, optional): Heart rate (bpm)
            sleep_hours (float, optional): Hours of sleep
            notes (str, optional): Notes about the measurements
        """
        self.id = id
        self.user_id = user_id
        self.date = date
        self.weight = weight
        self.systolic = systolic
        self.diastolic = diastolic
        self.heart_rate = heart_rate
        self.sleep_hours = sleep_hours
        self.notes = notes or ""
    
    def __str__(self):
        return f"HealthMetric({self.id}, {self.date}, weight={self.weight}, BP={self.systolic}/{self.diastolic})"


class HealthGoal:
    """Health goal model"""
    
    def __init__(self, id, user_id, goal_type, target_value, deadline, progress=0, notes=None):
        """Initialize a health goal
        
        Args:
            id (int): Goal ID (None for new goals)
            user_id (int): User ID
            goal_type (str): Type of goal (e.g. weight, exercise, sleep)
            target_value (float): Target value for the goal
            deadline (str): Goal deadline (YYYY-MM-DD)
            progress (float, optional): Current progress (percentage)
            notes (str, optional): Notes about the goal
        """
        self.id = id
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_value = target_value
        self.deadline = deadline
        self.progress = progress
        self.notes = notes or ""
    
    def __str__(self):
        return f"HealthGoal({self.id}, {self.goal_type}, target={self.target_value}, progress={self.progress}%)"


class HealthRecommendation:
    """AI-generated health recommendation model"""
    
    def __init__(self, recommendation_type, content, priority="medium"):
        """Initialize a health recommendation
        
        Args:
            recommendation_type (str): Type of recommendation (exercise, diet, sleep, etc.)
            content (str): Recommendation content
            priority (str, optional): Priority level (low, medium, high)
        """
        self.recommendation_type = recommendation_type
        self.content = content
        self.priority = priority
    
    def __str__(self):
        return f"HealthRecommendation({self.recommendation_type}, {self.priority})"
