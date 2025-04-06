#!/usr/bin/env python3
"""
Prepare feature set for college recommendation system by encoding categorical variables
and scaling numerical features.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
import argparse
from pathlib import Path
import joblib
from utils.logger_config import setup_logging
from utils.data_processing import encode_and_scale_features

def main():
    parser = argparse.ArgumentParser(
        description="Prepare features for college recommendation system"
    )
    parser.add_argument(
        "--input_file",
        default="../data/working_data/collegerecs_synthetic/student_college_history.csv",
        help="Path to input CSV file"
    )
    parser.add_argument(
        "--output_dir",
        default="../data/working_data/collegerecs_synthetic",
        help="Directory to save processed features and scaler"
    )
    args = parser.parse_args()

    # Setup logging first
    logger = setup_logging('feature_preparation')
    
    try:
        # Load data
        input_path = Path(args.input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return
            
        logger.info(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
        
        # Process features
        encoded_df, scaler, feature_cols = encode_and_scale_features(df, logger)
        
        # Save processed data and scaler
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        encoded_path = output_path / 'encoded_features.csv'
        cols_path = output_path / 'feature_columns.csv'
        scaler_path = output_path / 'feature_scaler.joblib'
        
        logger.info(f"Saving encoded features to {encoded_path}")
        encoded_df.to_csv(encoded_path, index=False)
        
        logger.info(f"Saving feature columns to {cols_path}")
        pd.Series(feature_cols).to_csv(cols_path, index=False)
        
        logger.info(f"Saving scaler to {scaler_path}")
        joblib.dump(scaler, scaler_path)
        
        logger.info("Feature preparation completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()