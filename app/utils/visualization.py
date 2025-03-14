#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualization utilities for Persian Life Manager Application
"""

import logging
import os
import json
from datetime import datetime, timedelta
import math

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QSizePolicy, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient, QRadialGradient, QPainterPath

logger = logging.getLogger(__name__)

def create_chart_html(chart_type, labels, datasets, title=None, colors=None, rtl=True):
    """Create HTML for Chart.js chart
    
    Args:
        chart_type (str): Chart type ('bar', 'line', 'pie', 'doughnut')
        labels (list): List of labels for chart
        datasets (list): List of datasets for chart
        title (str, optional): Chart title
        colors (list, optional): List of colors for datasets
        rtl (bool, optional): Whether to use RTL layout
        
    Returns:
        str: HTML content for chart
    """
    try:
        # Default colors if not provided
        if not colors:
            colors = [
                'rgba(0, 255, 170, 0.7)',  # Neon green
                'rgba(255, 0, 128, 0.7)',  # Neon pink
                'rgba(0, 170, 255, 0.7)',  # Neon blue
                'rgba(255, 170, 0, 0.7)',  # Neon orange
                'rgba(170, 0, 255, 0.7)'   # Neon purple
            ]
        
        # Format datasets based on chart type
        formatted_datasets = []
        if chart_type in ['bar', 'line']:
            for i, dataset in enumerate(datasets):
                color_idx = i % len(colors)
                formatted_dataset = {
                    'label': dataset.get('label', f'Dataset {i+1}'),
                    'data': dataset.get('data', []),
                    'backgroundColor': dataset.get('backgroundColor', colors[color_idx]),
                    'borderColor': dataset.get('borderColor', colors[color_idx].replace('0.7', '1.0')),
                    'borderWidth': dataset.get('borderWidth', 1)
                }
                
                # For line charts, add additional properties
                if chart_type == 'line':
                    formatted_dataset.update({
                        'fill': dataset.get('fill', False),
                        'tension': dataset.get('tension', 0.2),
                        'pointBackgroundColor': dataset.get('pointBackgroundColor', colors[color_idx])
                    })
                
                formatted_datasets.append(formatted_dataset)
        else:  # pie or doughnut
            formatted_datasets = [{
                'data': datasets,
                'backgroundColor': colors[:len(datasets)],
                'borderWidth': 1,
                'borderColor': '#171717'
            }]
        
        # Create chart configuration
        chart_config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': formatted_datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'position': 'right' if rtl else 'top',
                        'labels': {
                            'color': '#ecf0f1',
                            'font': {
                                'family': "'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif"
                            }
                        }
                    },
                    'title': {
                        'display': bool(title),
                        'text': title or '',
                        'color': '#ecf0f1',
                        'font': {
                            'family': "'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif",
                            'size': 16
                        }
                    }
                },
                'scales': {
                    'x': {
                        'display': chart_type in ['bar', 'line'],
                        'ticks': {
                            'color': '#ecf0f1',
                            'font': {
                                'family': "'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif"
                            }
                        },
                        'grid': {
                            'color': 'rgba(45, 45, 45, 0.5)'
                        }
                    },
                    'y': {
                        'display': chart_type in ['bar', 'line'],
                        'ticks': {
                            'color': '#ecf0f1',
                            'font': {
                                'family': "'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif"
                            }
                        },
                        'grid': {
                            'color': 'rgba(45, 45, 45, 0.5)'
                        }
                    }
                }
            }
        }
        
        # Set RTL if needed
        if rtl:
            chart_config['options']['rtl'] = True
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html dir="{'rtl' if rtl else 'ltr'}">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ 
                    background-color: #171717; 
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    font-family: 'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif;
                }}
                #chart-container {{
                    width: 100%;
                    height: 100%;
                }}
            </style>
        </head>
        <body>
            <div id="chart-container">
                <canvas id="chart"></canvas>
            </div>
            
            <script>
                const ctx = document.getElementById('chart').getContext('2d');
                const chart = new Chart(ctx, {json.dumps(chart_config, ensure_ascii=False)});
            </script>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        logger.error(f"Error creating chart HTML: {str(e)}")
        return create_error_chart_html()

def create_error_chart_html():
    """Create HTML for an error message instead of a chart
    
    Returns:
        str: HTML content with error message
    """
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                background-color: #171717; 
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif;
            }
            #error-message {
                color: #ff0080;
                font-size: 16px;
                text-align: center;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div id="error-message">
            <p>خطا در نمایش نمودار</p>
            <p>لطفا بعدا دوباره تلاش کنید</p>
        </div>
    </body>
    </html>
    """

def create_empty_chart_html():
    """Create HTML for an empty chart
    
    Returns:
        str: HTML content for empty chart
    """
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                background-color: #171717; 
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Vazirmatn', 'Vazir', 'Tahoma', sans-serif;
            }
            #empty-message {
                color: #555;
                font-size: 14px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div id="empty-message">داده‌ای برای نمایش وجود ندارد</div>
    </body>
    </html>
    """

def create_finance_summary_chart(income, expenses, months=None):
    """Create a finance summary bar chart HTML
    
    Args:
        income (list): List of income values
        expenses (list): List of expense values
        months (list, optional): List of month labels. If None, uses last 6 months.
        
    Returns:
        str: HTML content for finance summary chart
    """
    try:
        # If months not provided, generate for last 6 months
        if not months:
            months = []
            current_month = datetime.now().month
            for i in range(5, -1, -1):
                month_num = ((current_month - i - 1) % 12) + 1
                from app.utils.persian_utils import get_persian_month_name
                months.append(get_persian_month_name(month_num))
        
        datasets = [
            {
                'label': 'درآمد',
                'data': income,
                'backgroundColor': 'rgba(0, 255, 170, 0.7)'
            },
            {
                'label': 'هزینه',
                'data': expenses,
                'backgroundColor': 'rgba(255, 0, 128, 0.7)'
            }
        ]
        
        return create_chart_html('bar', months, datasets, title="مقایسه درآمد و هزینه")
    except Exception as e:
        logger.error(f"Error creating finance summary chart: {str(e)}")
        return create_error_chart_html()

def create_expense_categories_chart(categories, amounts):
    """Create a pie chart for expense categories
    
    Args:
        categories (list): List of category names
        amounts (list): List of expense amounts for each category
        
    Returns:
        str: HTML content for expense categories chart
    """
    try:
        return create_chart_html('pie', categories, amounts, title="هزینه‌ها بر اساس دسته‌بندی")
    except Exception as e:
        logger.error(f"Error creating expense categories chart: {str(e)}")
        return create_error_chart_html()

def create_health_trend_chart(dates, values, metric_name):
    """Create a health metric trend line chart
    
    Args:
        dates (list): List of date labels
        values (list): List of metric values
        metric_name (str): Name of the health metric
        
    Returns:
        str: HTML content for health trend chart
    """
    try:
        # Format data for line chart
        dataset = {
            'label': metric_name,
            'data': values,
            'backgroundColor': 'rgba(0, 170, 255, 0.7)'
        }
        
        return create_chart_html('line', dates, [dataset], title=f"روند {metric_name}")
    except Exception as e:
        logger.error(f"Error creating health trend chart: {str(e)}")
        return create_error_chart_html()

def create_tasks_completion_chart(completed, pending, overdue=None):
    """Create a doughnut chart for task completion status
    
    Args:
        completed (int): Number of completed tasks
        pending (int): Number of pending tasks
        overdue (int, optional): Number of overdue tasks
        
    Returns:
        str: HTML content for tasks completion chart
    """
    try:
        labels = ["تکمیل شده", "در انتظار"]
        data = [completed, pending]
        colors = ['rgba(0, 255, 170, 0.7)', 'rgba(0, 170, 255, 0.7)']
        
        if overdue is not None:
            labels.append("با تاخیر")
            data.append(overdue)
            colors.append('rgba(255, 0, 128, 0.7)')
        
        return create_chart_html('doughnut', labels, data, title="وضعیت وظایف", colors=colors)
    except Exception as e:
        logger.error(f"Error creating tasks completion chart: {str(e)}")
        return create_error_chart_html()

class SimpleChartView(QGraphicsView):
    """A native chart view without web dependencies"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Set background
        self.setBackgroundBrush(QBrush(QColor("#171717")))
        
        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Chart data
        self.chart_type = None
        self.labels = []
        self.datasets = []
        self.colors = [
            QColor(0, 255, 170, 180),  # Neon green
            QColor(255, 0, 128, 180),  # Neon pink
            QColor(0, 170, 255, 180),  # Neon blue
            QColor(255, 170, 0, 180),  # Neon orange
            QColor(170, 0, 255, 180)   # Neon purple
        ]
        
        # Empty state
        self.is_empty = True
        self.is_error = False
        self.empty_message = "داده‌ای برای نمایش وجود ندارد"
        self.error_message = "خطا در نمایش نمودار"
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(QSize(200, 150))
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.redraw_chart()
    
    def set_bar_chart(self, labels, datasets, title=None):
        """Set bar chart data
        
        Args:
            labels (list): List of labels for X axis
            datasets (list): List of datasets for chart
            title (str, optional): Chart title
        """
        self.chart_type = "bar"
        self.labels = labels
        self.datasets = datasets
        self.title = title
        self.is_empty = False
        self.is_error = False
        self.redraw_chart()
    
    def set_line_chart(self, labels, datasets, title=None):
        """Set line chart data
        
        Args:
            labels (list): List of labels for X axis
            datasets (list): List of datasets for chart 
            title (str, optional): Chart title
        """
        self.chart_type = "line"
        self.labels = labels
        self.datasets = datasets
        self.title = title
        self.is_empty = False
        self.is_error = False
        self.redraw_chart()
    
    def set_pie_chart(self, labels, values, title=None):
        """Set pie chart data
        
        Args:
            labels (list): List of segment labels
            values (list): List of values
            title (str, optional): Chart title
        """
        self.chart_type = "pie"
        self.labels = labels
        self.datasets = [{'data': values}]
        self.title = title
        self.is_empty = False
        self.is_error = False
        self.redraw_chart()
    
    def set_doughnut_chart(self, labels, values, title=None):
        """Set doughnut chart data
        
        Args:
            labels (list): List of segment labels
            values (list): List of values
            title (str, optional): Chart title
        """
        self.chart_type = "doughnut"
        self.labels = labels
        self.datasets = [{'data': values}]
        self.title = title
        self.is_empty = False
        self.is_error = False
        self.redraw_chart()
    
    def set_empty(self):
        """Set empty state"""
        self.is_empty = True
        self.is_error = False
        self.redraw_chart()
    
    def set_error(self):
        """Set error state"""
        self.is_empty = True
        self.is_error = True
        self.redraw_chart()
    
    def redraw_chart(self):
        """Redraw the chart"""
        self.scene.clear()
        
        # Set scene size
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        
        if self.is_empty:
            self.draw_message()
            return
            
        # Draw title if available
        title_height = 0
        if hasattr(self, 'title') and self.title:
            title = self.scene.addText(self.title, QFont("Segoe UI", 10, QFont.Weight.Bold))
            title.setDefaultTextColor(QColor("#FFFFFF"))
            title_width = title.boundingRect().width()
            title.setPos(self.width()/2 - title_width/2, 10)
            title_height = 30
        
        # Draw based on chart type
        if self.chart_type == "bar":
            self.draw_bar_chart(title_height)
        elif self.chart_type == "line":
            self.draw_line_chart(title_height)
        elif self.chart_type == "pie":
            self.draw_pie_chart(title_height, False)
        elif self.chart_type == "doughnut":
            self.draw_pie_chart(title_height, True)
    
    def draw_message(self):
        """Draw a message (empty or error)"""
        message = self.error_message if self.is_error else self.empty_message
        text = self.scene.addText(message, QFont("Segoe UI", 10))
        text.setDefaultTextColor(QColor("#FF0080" if self.is_error else "#555555"))
        
        # Center the text
        text_rect = text.boundingRect()
        text.setPos(
            self.width()/2 - text_rect.width()/2,
            self.height()/2 - text_rect.height()/2
        )
    
    def draw_bar_chart(self, top_offset=0):
        """Draw a bar chart
        
        Args:
            top_offset (int): Top offset for the chart (e.g., for title)
        """
        chart_height = self.height() - top_offset - 50  # Space for labels
        chart_width = self.width() - 100  # Space for labels
        
        # Starting position
        start_x = 50
        start_y = self.height() - 50
        
        # Draw axes
        pen = QPen(QColor("#333333"))
        self.scene.addLine(start_x, top_offset + 20, start_x, start_y, pen)  # Y-axis
        self.scene.addLine(start_x, start_y, start_x + chart_width, start_y, pen)  # X-axis
        
        # No data to display
        if not self.labels or not self.datasets or not self.datasets[0].get('data'):
            self.set_empty()
            return
        
        # Find max value for scaling
        max_value = 0
        for dataset in self.datasets:
            data = dataset.get('data', [])
            if data:
                max_value = max(max_value, max(data))
        
        # Ensure we have a non-zero max_value
        if max_value == 0:
            max_value = 1
        
        # Calculate bar width based on number of datasets and labels
        bar_width = chart_width / (len(self.labels) * (len(self.datasets) + 1))
        bar_spacing = bar_width / 2
        
        # Draw bars
        for label_idx, label in enumerate(self.labels):
            # Draw label
            text = self.scene.addText(str(label), QFont("Segoe UI", 8))
            text.setDefaultTextColor(QColor("#FFFFFF"))
            text_width = text.boundingRect().width()
            x_pos = start_x + label_idx * (bar_width * len(self.datasets) + bar_spacing) + (bar_width * len(self.datasets)) / 2
            text.setPos(x_pos - text_width/2, start_y + 5)
            
            # Draw bars for each dataset
            for ds_idx, dataset in enumerate(self.datasets):
                data = dataset.get('data', [])
                if label_idx < len(data):
                    value = data[label_idx]
                    bar_height = (value / max_value) * chart_height
                    
                    # Bar position
                    x = start_x + label_idx * (bar_width * len(self.datasets) + bar_spacing) + ds_idx * bar_width
                    y = start_y - bar_height
                    
                    # Create bar
                    color = self.colors[ds_idx % len(self.colors)]
                    self.scene.addRect(x, y, bar_width, bar_height, QPen(color), QBrush(color))
                    
                    # Add value text
                    text = self.scene.addText(str(value), QFont("Segoe UI", 8))
                    text.setDefaultTextColor(QColor("#FFFFFF"))
                    text_width = text.boundingRect().width()
                    text.setPos(x + (bar_width - text_width)/2, y - 15)
        
        # Draw legend
        legend_x = 10
        legend_y = 10 + top_offset
        for ds_idx, dataset in enumerate(self.datasets):
            if 'label' in dataset:
                # Draw color box
                color = self.colors[ds_idx % len(self.colors)]
                self.scene.addRect(legend_x, legend_y, 10, 10, QPen(color), QBrush(color))
                
                # Draw label
                text = self.scene.addText(dataset['label'], QFont("Segoe UI", 8))
                text.setDefaultTextColor(QColor("#FFFFFF"))
                text.setPos(legend_x + 15, legend_y - 4)
                
                legend_y += 20
    
    def draw_line_chart(self, top_offset=0):
        """Draw a line chart
        
        Args:
            top_offset (int): Top offset for the chart (e.g., for title)
        """
        chart_height = self.height() - top_offset - 50  # Space for labels
        chart_width = self.width() - 100  # Space for labels
        
        # Starting position
        start_x = 50
        start_y = self.height() - 50
        
        # Draw axes
        pen = QPen(QColor("#333333"))
        self.scene.addLine(start_x, top_offset + 20, start_x, start_y, pen)  # Y-axis
        self.scene.addLine(start_x, start_y, start_x + chart_width, start_y, pen)  # X-axis
        
        # No data to display
        if not self.labels or not self.datasets or not self.datasets[0].get('data'):
            self.set_empty()
            return
        
        # Find max value for scaling
        max_value = 0
        for dataset in self.datasets:
            data = dataset.get('data', [])
            if data:
                max_value = max(max_value, max(data))
        
        # Ensure we have a non-zero max_value
        if max_value == 0:
            max_value = 1
        
        # X steps
        num_points = len(self.labels)
        if num_points <= 1:
            self.set_empty()
            return
            
        x_step = chart_width / (num_points - 1)
        
        # Draw lines and points
        for ds_idx, dataset in enumerate(self.datasets):
            data = dataset.get('data', [])
            if not data:
                continue
                
            # Use dataset color or default
            color = self.colors[ds_idx % len(self.colors)]
            
            # Create path for the line
            path = QPainterPath()
            points = []
            
            for i, value in enumerate(data[:num_points]):
                x = start_x + i * x_step
                y = start_y - (value / max_value) * chart_height
                points.append((x, y))
                
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            
            # Draw the line
            pen = QPen(color, 2)
            self.scene.addPath(path, pen)
            
            # Draw points
            for x, y in points:
                self.scene.addEllipse(x-3, y-3, 6, 6, QPen(color), QBrush(color))
                
                # Add value text
                idx = points.index((x, y))
                if idx < len(data):
                    value = data[idx]
                    text = self.scene.addText(str(value), QFont("Segoe UI", 8))
                    text.setDefaultTextColor(QColor("#FFFFFF"))
                    text_width = text.boundingRect().width()
                    text.setPos(x - text_width/2, y - 20)
            
            # Draw labels
            for i, label in enumerate(self.labels[:num_points]):
                x = start_x + i * x_step
                text = self.scene.addText(str(label), QFont("Segoe UI", 8))
                text.setDefaultTextColor(QColor("#FFFFFF"))
                text_width = text.boundingRect().width()
                text.setPos(x - text_width/2, start_y + 5)
        
        # Draw legend
        legend_x = 10
        legend_y = 10 + top_offset
        for ds_idx, dataset in enumerate(self.datasets):
            if 'label' in dataset:
                # Draw color box
                color = self.colors[ds_idx % len(self.colors)]
                self.scene.addRect(legend_x, legend_y, 10, 10, QPen(color), QBrush(color))
                
                # Draw label
                text = self.scene.addText(dataset['label'], QFont("Segoe UI", 8))
                text.setDefaultTextColor(QColor("#FFFFFF"))
                text.setPos(legend_x + 15, legend_y - 4)
                
                legend_y += 20
    
    def draw_pie_chart(self, top_offset=0, is_doughnut=False):
        """Draw a pie or doughnut chart
        
        Args:
            top_offset (int): Top offset for the chart (e.g., for title)
            is_doughnut (bool): Whether to draw as doughnut
        """
        # No data to display
        if not self.labels or not self.datasets or not self.datasets[0].get('data'):
            self.set_empty()
            return
        
        # Get chart dimensions
        chart_size = min(self.width(), self.height() - top_offset) - 80
        
        # Chart center
        center_x = self.width() / 2
        center_y = (self.height() - top_offset) / 2 + top_offset
        
        # Get total value
        values = self.datasets[0].get('data', [])
        total = sum(values)
        
        # If total is 0, show empty
        if total == 0:
            self.set_empty()
            return
        
        # Draw pie segments
        start_angle = 0
        for i, value in enumerate(values):
            if i >= len(self.labels):
                break
                
            # Calculate percentage and angle
            angle = 360 * value / total
            color = self.colors[i % len(self.colors)]
            
            # Create a path for the pie segment
            path = QPainterPath()
            path.moveTo(center_x, center_y)
            
            # Calculate arc based on angle
            arc_rect = QRectF(
                center_x - chart_size/2, 
                center_y - chart_size/2,
                chart_size, 
                chart_size
            )
            
            path.arcTo(arc_rect, start_angle, angle)
            path.closeSubpath()
            
            # For doughnut, cut out the center
            if is_doughnut:
                inner_size = chart_size * 0.5
                inner_rect = QRectF(
                    center_x - inner_size/2,
                    center_y - inner_size/2,
                    inner_size,
                    inner_size
                )
                
                # Create inner circle path
                inner_path = QPainterPath()
                inner_path.addEllipse(inner_rect)
                
                # Subtract inner circle from segment
                path = path.subtracted(inner_path)
            
            # Add segment to scene
            self.scene.addPath(path, QPen(color), QBrush(color))
            
            # Add percentage label
            mid_angle = start_angle + angle/2
            label_radius = chart_size * (0.35 if is_doughnut else 0.30)
            label_x = center_x + math.cos(math.radians(mid_angle)) * label_radius
            label_y = center_y - math.sin(math.radians(mid_angle)) * label_radius
            
            percent = int(100 * value / total)
            text = self.scene.addText(f"{percent}%", QFont("Segoe UI", 8, QFont.Weight.Bold))
            text.setDefaultTextColor(QColor("#FFFFFF"))
            text_width = text.boundingRect().width()
            text_height = text.boundingRect().height()
            text.setPos(label_x - text_width/2, label_y - text_height/2)
            
            # Update start angle for next segment
            start_angle += angle
        
        # Draw legend
        legend_x = 10
        legend_y = 10 + top_offset
        for i, label in enumerate(self.labels):
            if i < len(values):
                # Draw color box
                color = self.colors[i % len(self.colors)]
                self.scene.addRect(legend_x, legend_y, 10, 10, QPen(color), QBrush(color))
                
                # Draw label
                text = self.scene.addText(f"{label} ({values[i]})", QFont("Segoe UI", 8))
                text.setDefaultTextColor(QColor("#FFFFFF"))
                text.setPos(legend_x + 15, legend_y - 4)
                
                legend_y += 20


class WebChartWidget(QWidget):
    """Widget for displaying charts (using native drawing)"""
    
    def __init__(self, parent=None):
        """Initialize the chart widget"""
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a chart view
        self.chart_view = SimpleChartView(self)
        layout.addWidget(self.chart_view)
        
        # Display empty chart initially
        self.display_empty_chart()
    
    def display_chart(self, html_content):
        """Legacy method for backward compatibility
        
        Args:
            html_content (str): Ignored
        """
        # This method is kept for backward compatibility
        self.display_empty_chart()
        logger.warning("WebChartWidget.display_chart is deprecated, use specific chart methods instead")
    
    def display_empty_chart(self):
        """Display an empty chart"""
        self.chart_view.set_empty()
    
    def display_error_chart(self):
        """Display an error message instead of a chart"""
        self.chart_view.set_error()
    
    def display_finance_summary(self, income, expenses, months=None):
        """Display a finance summary chart
        
        Args:
            income (list): List of income values
            expenses (list): List of expense values
            months (list, optional): List of month labels
        """
        try:
            # If months not provided, generate for last 6 months
            if not months:
                months = []
                current_month = datetime.now().month
                for i in range(5, -1, -1):
                    month_num = ((current_month - i - 1) % 12) + 1
                    from app.utils.persian_utils import get_persian_month_name
                    months.append(get_persian_month_name(month_num))
            
            # Ensure arrays have the same length
            min_length = min(len(income), len(expenses), len(months))
            months = months[:min_length]
            income = income[:min_length]
            expenses = expenses[:min_length]
            
            datasets = [
                {
                    'label': 'درآمد',
                    'data': income
                },
                {
                    'label': 'هزینه',
                    'data': expenses
                }
            ]
            
            self.chart_view.set_bar_chart(months, datasets, "مقایسه درآمد و هزینه")
        except Exception as e:
            logger.error(f"Error displaying finance summary chart: {str(e)}")
            self.display_error_chart()
    
    def display_expense_categories(self, categories, amounts):
        """Display an expense categories pie chart
        
        Args:
            categories (list): List of category names
            amounts (list): List of expense amounts
        """
        try:
            # Check data
            if not categories or not amounts:
                self.display_empty_chart()
                return
                
            # Ensure arrays have the same length
            min_length = min(len(categories), len(amounts))
            categories = categories[:min_length]
            amounts = amounts[:min_length]
            
            self.chart_view.set_pie_chart(categories, amounts, "هزینه‌ها بر اساس دسته‌بندی")
        except Exception as e:
            logger.error(f"Error displaying expense categories chart: {str(e)}")
            self.display_error_chart()
    
    def display_health_trend(self, dates, values, metric_name):
        """Display a health metric trend chart
        
        Args:
            dates (list): List of date labels
            values (list): List of metric values
            metric_name (str): Name of the health metric
        """
        try:
            # Check data
            if not dates or not values:
                self.display_empty_chart()
                return
                
            # Ensure arrays have the same length
            min_length = min(len(dates), len(values))
            dates = dates[:min_length]
            values = values[:min_length]
            
            dataset = {
                'label': metric_name,
                'data': values
            }
            
            self.chart_view.set_line_chart(dates, [dataset], f"روند {metric_name}")
        except Exception as e:
            logger.error(f"Error displaying health trend chart: {str(e)}")
            self.display_error_chart()
    
    def display_tasks_completion(self, completed, pending, overdue=None):
        """Display a tasks completion doughnut chart
        
        Args:
            completed (int): Number of completed tasks
            pending (int): Number of pending tasks
            overdue (int, optional): Number of overdue tasks
        """
        try:
            labels = ["تکمیل شده", "در انتظار"]
            values = [completed, pending]
            
            if overdue is not None:
                labels.append("با تاخیر")
                values.append(overdue)
            
            self.chart_view.set_doughnut_chart(labels, values, "وضعیت وظایف")
        except Exception as e:
            logger.error(f"Error displaying tasks completion chart: {str(e)}")
            self.display_error_chart()
