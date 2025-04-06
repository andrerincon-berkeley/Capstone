#!/usr/bin/env python3
"""
Generate college recommendations based on student information.
"""

import pandas as pd
import numpy as np
import joblib
import argparse
from pathlib import Path
from utils.logger_config import setup_logging
from utils.data_processing import process_student_input, generate_recommendations

def main():
    parser = argparse.ArgumentParser(
        description="Generate college recommendations for a student"
    )
    parser.add_argument("--sat", type=int, required=True, help="Student's SAT score")
    parser.add_argument("--gpa", type=float, required=True, help="Student's GPA")
    parser.add_argument("--major", type=str, required=True, help="Student's intended major")
    parser.add_argument(
        "--importance-location", 
        type=int, 
        choices=[1,2,3,4,5], 
        required=True,
        help="Importance of location (1-5)"
    )
    parser.add_argument(
        "--importance-reputation", 
        type=int, 
        choices=[1,2,3,4,5], 
        required=True,
        help="Importance of school reputation (1-5)"
    )
    parser.add_argument(
        "--importance-cost", 
        type=int, 
        choices=[1,2,3,4,5], 
        required=True,
        help="Importance of school cost (1-5)"
    )
    args = parser.parse_args()

    logger = setup_logging('college_recommender')
    
    try:
        # Load model artifacts
        model_dir = Path("../data/working_data/collegerecs_synthetic")
        
        logger.info("Loading encoded features...")
        encoded_df = pd.read_csv(model_dir / 'encoded_features.csv')
        
        logger.info("Loading feature columns...")
        feature_cols = pd.read_csv(model_dir / 'feature_columns.csv')['0'].tolist()
        
        logger.info("Loading scaler...")
        scaler = joblib.load(model_dir / 'feature_scaler.joblib')
        
        # Create student input DataFrame
        student_data = {
            "SAT": args.sat,
            "GPA": args.gpa,
            "major": args.major,
            "importance_close_to_home": args.importance_location,
            "importance_school_reputation": args.importance_reputation,
            "importance_school_cost": args.importance_cost
        }
        student_df = pd.DataFrame([student_data])
        
        # Process student input
        logger.info("Processing student input...")
        student_features = process_student_input(student_df, feature_cols, scaler, logger)
        
        # Generate recommendations
        logger.info("Generating recommendations...")
        recommendations = generate_recommendations(
            student_features, 
            encoded_df,
            feature_cols,
            logger
        )
        
        # Print recommendations
        print("\nTop College Recommendations:")
        print("===========================")
        print(recommendations.to_string())
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()