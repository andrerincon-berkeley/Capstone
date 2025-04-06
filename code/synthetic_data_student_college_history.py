#!/usr/bin/env python3
"""
Generate synthetic student college history data for college recommendation system.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from pathlib import Path
import argparse
import logging
from datetime import datetime

def setup_logging():
    """
    Configure logging to both console and file.
    
    Creates a logs directory if it doesn't exist and generates log files
    with timestamps in the filename.
    
    Returns:
        logger: Configured logging object
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('../logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'synthetic_data_generation_{timestamp}.log'
    
    # Configure logging
    logger = logging.getLogger('synthetic_data_generator')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f'Log file created at: {log_file}')
    return logger

# Modify the rest of the functions to use the logger object
def load_college_data(filepath, logger):
    """
    Load the selected colleges data from CSV.

    Args:
        filepath (str): Path to the CSV file containing college data
        logger: Logger object for output messages

    Returns:
        pandas.DataFrame: DataFrame containing college information
        list: List of unique college names

    Raises:
        FileNotFoundError: If the college data file doesn't exist
    """
    try:
        selected_colleges = pd.read_csv(filepath)
        college_names = selected_colleges['school_name'].unique().tolist()
        logger.info(f"Loaded {len(college_names)} colleges from {filepath}")
        return selected_colleges, college_names
    except FileNotFoundError:
        logger.error(f"College data file not found: {filepath}")
        raise

def generate_synthetic_data(num_students, selected_colleges, college_names, logger):
    """
    Generate synthetic student records.

    Args:
        num_students (int): Number of student records to generate
        selected_colleges (pandas.DataFrame): DataFrame containing college information
        college_names (list): List of college names to choose from
        logger: Logger object for output messages

    Returns:
        pandas.DataFrame: DataFrame containing synthetic student records
    """
    faker = Faker()
    majors = ["Computer Science", "Biology", "Engineering", "Business", 
              "Psychology", "Nursing", "Art", "Economics"]
    
    logger.info(f"Generating {num_students} synthetic student records...")
    
    students = []
    for student_id in range(1, num_students + 1):
        college = random.choice(college_names)
        sat = selected_colleges.loc[selected_colleges['school_name'] == college, 'avg_total_sat'].iloc[0]
        gpa = np.round(np.random.normal(3.4, 0.4), 2)
        
        students.append({
            "student_id": student_id,
            "SAT": sat,
            "GPA": max(min(gpa, 4.0), 0.0),  # Clamp to [0, 4.0]
            "city": faker.city(),
            "state": faker.state_abbr(),
            "major": random.choice(majors),
            "college_name": college,
            "importance_close_to_home": random.randint(1, 5),
            "importance_school_reputation": random.randint(1, 5),
            "importance_school_cost": random.randint(1, 5)
        })
        
        if student_id % 5000 == 0:
            logger.info(f"Generated {student_id} records...")
    
    df_students = pd.DataFrame(students)
    logger.info(f"Completed generating {num_students} student records")
    return df_students

def save_data(df, filepath, logger):
    """Save the synthetic data to a CSV file."""
    output_dir = Path(filepath).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(filepath, index=False, mode='w')
    logger.info(f"Saved synthetic data to {filepath}")

def main():
    """Main function to generate synthetic student college history data."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate synthetic student college history data"
    )
    parser.add_argument(
        "--num_students",
        type=int,
        default=30000,
        help="Number of synthetic student records to generate (default: 30000)"
    )
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

    # Set the filepaths
    raw_data_path = '../data/working_data/collegerecs_synthetic/selected_colleges.csv'
    student_school_filepath = '../data/working_data/collegerecs_synthetic/student_college_history.csv'

    try:
        # Load college data
        selected_colleges, college_names = load_college_data(raw_data_path, logger)

        # Generate synthetic data
        df_students = generate_synthetic_data(
            args.num_students,
            selected_colleges,
            college_names,
            logger
        )

        # Save the data
        save_data(df_students, student_school_filepath, logger)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()