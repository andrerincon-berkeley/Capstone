import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from typing import List, Dict, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HSLSFeatureProcessor:
    def __init__(self, raw_data_path: str, features_columns_path: str, output_path: str):
        self.raw_data_path = Path(raw_data_path)
        self.features_columns_path = Path(features_columns_path)
        self.output_path = Path(output_path)
        self.required_columns = ['X3TGPATOT', 'X4PS1SELECT', 'X4ATNDCLG16FB']
        self.df = None
        self.features_columns = None

    def load_data(self) -> None:
        """Load and validate raw data and feature columns."""
        try:
            self.df = pd.read_csv(self.raw_data_path)
            logger.info(f"Successfully loaded raw data with {len(self.df)} rows")
        except FileNotFoundError:
            logger.error(f"Raw data file not found at: {self.raw_data_path}")
            raise
        
        try:
            with open(self.features_columns_path, 'r') as file:
                self.features_columns = file.read().splitlines()
            logger.info(f"Successfully loaded {len(self.features_columns)} feature columns")
        except FileNotFoundError:
            logger.error(f"Features columns file not found at: {self.features_columns_path}")
            raise

    def validate_columns(self) -> None:
        """Validate that required columns exist in the dataset."""
        missing_columns = [col for col in self.required_columns if col not in self.df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")

    @staticmethod
    def map_gpa_to_category(gpa: float) -> int:
        """
        Map GPA to categorical values.
        
        Args:
            gpa (float): The GPA value to map
            
        Returns:
            int: Mapped category value (-1 to 6)
        """
        if gpa < 0:
            return -1
        
        ranges = [
            (0.00, 1.00, 0),
            (1.01, 1.50, 1),
            (1.51, 2.00, 2),
            (2.01, 2.50, 3),
            (2.51, 3.00, 4),
            (3.01, 3.50, 5)
        ]
        
        for low, high, category in ranges:
            if low <= gpa <= high:
                return category
        
        return 6  # > 3.51

    @staticmethod
    def map_selectivity(x: int, attended: int) -> int:
        """
        Map post-secondary selectivity based on values and attendance.
        
        Args:
            x (int): X4PS1SELECT value
            attended (int): X4ATNDCLG16FB value
            
        Returns:
            int: Mapped selectivity value
        """
        if x >= 3:
            return 3
        elif attended == 0:
            return -1
        else:
            return x

    def create_features(self) -> None:
        """Create all derived features."""
        # Create high school GPA categories
        self.df['high_school_gpa'] = self.df['X3TGPATOT'].apply(self.map_gpa_to_category)
        logger.info("\nHigh school GPA distribution:")
        logger.info(self.df['high_school_gpa'].value_counts().sort_index())

        # Create post-secondary selectivity
        self.df['ps_selectivity'] = self.df.apply(
            lambda row: self.map_selectivity(row['X4PS1SELECT'], row['X4ATNDCLG16FB']), 
            axis=1
        )
        logger.info("\nPost-secondary selectivity distribution:")
        logger.info(self.df['ps_selectivity'].value_counts().sort_index())

        # Create undermatched indicator
        self.df['undermatched'] = ((self.df['high_school_gpa'] == 6) & 
                                  ((self.df['ps_selectivity'] == -1) | 
                                   (self.df['ps_selectivity'] == 3))).astype(int)
        logger.info("\nUndermatched distribution:")
        logger.info(self.df['undermatched'].value_counts().sort_index())

    def filter_and_save(self) -> None:
        """Filter to highest GPA students and save the final dataset."""
        # Filter to highest GPA students
        self.df = self.df[self.df['high_school_gpa'] == 6][self.features_columns + ['undermatched']]
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the dataset
        self.df.to_csv(self.output_path, index=False)
        logger.info(f"Successfully saved processed data to {self.output_path}")

    def process(self) -> None:
        """Execute the full processing pipeline."""
        logger.info("Starting data processing")
        self.load_data()
        self.validate_columns()
        self.create_features()
        self.filter_and_save()
        logger.info("Data processing completed successfully")

def main():
    # Define paths
    raw_data_path = '../data/raw_data/hsls_09/hsls_17_student_pets_sr_v1_0.csv'
    features_columns_path = '../data/raw_data/hsls_09/filtered_correlated_columns.txt'
    output_path = '../data/working_data/hsls_09/features_file_hsls09.csv'

    try:
        processor = HSLSFeatureProcessor(raw_data_path, features_columns_path, output_path)
        processor.process()
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()