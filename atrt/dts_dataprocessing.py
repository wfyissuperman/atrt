from datetime import datetime,timedelta
import numpy as np
import pandas as pd

class DtsDataProcessing:
    """
    A class to process Distributed Temperature Sensing (DTS) data.
    This class handles the extraction of temperature data from a DataFrame,
    allowing for time and depth indexing, and extraction of heating data
    within specified depth ranges and time periods.
    """
    def __init__(self, data):
        self.data = data
        self.time = pd.to_datetime(data.columns[1:])
        self.depth = data.iloc[1:, 0].astype(np.float64).to_numpy()
        self.temp = data.iloc[1:, 1:].astype(np.float64).to_numpy()
    
    def find_time_index(self, time_str):
        target_time = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S')
        time_diffs = [abs(target_time - time) for time in self.time]
        closest_time_index = np.argmin(time_diffs)
        return closest_time_index
    
    def find_depth_index(self, depth_value):
        depth_array = self.depth
        idx = (np.abs(depth_array - depth_value)).argmin()
        return idx
    
    def extraction_heating_data(self, top_idx, bottom_idx, start_str, end_str):
        """
        Extract heating data from the DTS data within a specified depth range and time period.
        
        Parameters:
        -----------
        top_idx : int
            Index of the top depth of the borehole.
        bottom_idx : int
            Index of the bottom depth of the borehole.
        start_str : str
            Start time in 'YYYY/MM/DD HH:MM:SS' format.
        end_str : str
            End time in 'YYYY/MM/DD HH:MM:SS' format.
        
        Returns:
        --------
        tuple of (np.ndarray, np.ndarray, np.ndarray)
            - seconds: Time array in seconds from start time
            - delta_temp: Temperature data within specified range and time period
            - natural_temp: Average temperature before heating for each depth
        
        Raises:
        -------
        ValueError
            If time indices are invalid or heating period is too short.
        """
        # Validate inputs
        if top_idx < 0 or bottom_idx < 0 :
            raise ValueError("Invalid depth indices")
        
        try:
            start_time = pd.to_datetime(start_str, format='%Y/%m/%d %H:%M:%S')
            end_time = pd.to_datetime(end_str, format='%Y/%m/%d %H:%M:%S')
        except Exception as e:
            raise ValueError(f"Invalid time format: {e}")
        
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        # Find time indices
        start_idx = self.find_time_index(start_str)
        end_idx = self.find_time_index(end_str)
        
        # Adjust indices to ensure exact time boundaries
        if self.time[start_idx] < start_time:
            start_idx += 1
        if self.time[end_idx] > end_time:
            end_idx -= 1
        
        # Validate time range
        if start_idx >= end_idx:
            raise ValueError("Heating period too short or no data available")
        
        # Extract heating period data
        heating_time_section = self.time[start_idx:end_idx + 1]
        seconds = (heating_time_section - start_time).total_seconds()
        
        # Extract temperature data for specified depth range and time period
        delta_temp = self.temp[top_idx:bottom_idx + 1, start_idx:end_idx + 1]
        
        # Calculate average temperature before heating (1 minute before start)
        before_time = start_time - pd.Timedelta(minutes=1)
        before_time_str = before_time.strftime('%Y/%m/%d %H:%M:%S')
        before_idx = self.find_time_index(before_time_str)
        
        # Extract temperature data before heating
        before_temp = self.temp[top_idx:bottom_idx + 1, before_idx:start_idx]
        natural_temp = np.mean(before_temp, axis=1)
        
        return seconds, delta_temp, natural_temp