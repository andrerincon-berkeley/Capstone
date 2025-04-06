"""Data processing utilities for college recommendation system."""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

def encode_and_scale_features(df, logger):
    """
    Encode categorical variables and scale numerical features.
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing student records
        logger: Logger object for output messages
        
    Returns:
        tuple: (encoded_df, scaler, feature_cols)
            - encoded_df: DataFrame with encoded and scaled features
            - scaler: Fitted StandardScaler object
            - feature_cols: List of feature column names
    """
    try:
        logger.info("Starting feature encoding and scaling")
        
        # Encode categorical features
        categorical_columns = ["major", 
                             "importance_close_to_home",
                             "importance_school_reputation",
                             "importance_school_cost"]
        
        logger.info(f"Encoding categorical columns: {categorical_columns}")
        df_encoded = pd.get_dummies(df, columns=categorical_columns)
        
        # Define feature columns
        numeric_cols = ["SAT", "GPA"]
        encoded_categorical_cols = [col for col in df_encoded.columns 
                                  if any(col.startswith(prefix + "_") 
                                       for prefix in categorical_columns)]
        
        feature_cols = numeric_cols + encoded_categorical_cols
        
        # Scale numeric features
        logger.info(f"Scaling numeric features: {numeric_cols}")
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_encoded[numeric_cols])
        
        # Replace original numeric columns with scaled versions
        for i, col in enumerate(numeric_cols):
            df_encoded[col] = scaled_features[:, i]
            
        logger.info(f"Created {len(feature_cols)} features")
        
        return df_encoded, scaler, feature_cols
        
    except Exception as e:
        logger.error(f"Error in encode_and_scale_features: {str(e)}")
        raise

def generate_recommendations(student_features, encoded_df, feature_cols, logger):
    """
    Generate college recommendations based on student features.
    
    Args:
        student_features (pandas.DataFrame): Processed student input features
        encoded_df (pandas.DataFrame): Training data with encoded features
        feature_cols (list): List of feature columns to use
        logger: Logger object for output messages
        
    Returns:
        pandas.DataFrame: Recommendations with college statistics
    """
    try:
        logger.info("Finding similar students...")
        
        # Initialize and fit KNN model
        knn = NearestNeighbors(n_neighbors=25)
        knn.fit(encoded_df[feature_cols])
        
        # Find nearest neighbors
        distances, indices = knn.kneighbors(student_features[feature_cols])
        
        # Get similar students and original data
        similar_students_idx = indices[0]
        
        # Load original data to get non-encoded columns
        original_data_path = Path("../data/working_data/collegerecs_synthetic/student_college_history.csv")
        original_df = pd.read_csv(original_data_path)
        
        # Get similar students from original dataset
        similar_students = original_df.iloc[similar_students_idx]
        
        # Calculate college statistics
        college_stats = similar_students.groupby("college_name").agg({
            "SAT": ["count", "mean"],
            "GPA": "mean",
            "importance_close_to_home": "mean",
            "importance_school_reputation": "mean",
            "importance_school_cost": "mean"
        }).round(2)
        
        # Flatten column names
        college_stats.columns = [
            "num_similar_students",
            "avg_SAT",
            "avg_GPA",
            "avg_importance_location",
            "avg_importance_reputation",
            "avg_importance_cost"
        ]
        
        # Sort by number of similar students
        college_stats = college_stats.sort_values(
            by="num_similar_students", 
            ascending=False
        ).head(10)
        
        # Reset index to make college_name a column
        college_stats = college_stats.reset_index()
        
        logger.info(f"Generated recommendations for {len(college_stats)} colleges")
        return college_stats
        
    except Exception as e:
        logger.error(f"Error in generate_recommendations: {str(e)}")
        raise
    
def process_student_input(student_df, feature_cols, scaler, logger):
    """
    Process student input into format needed for recommendations.
    
    Args:
        student_df (pandas.DataFrame): DataFrame with raw student input
        feature_cols (list): List of feature columns to use
        scaler (StandardScaler): Fitted scaler for numeric features
        logger: Logger object for output messages
        
    Returns:
        pandas.DataFrame: Processed student features
    """
    try:
        logger.info("Processing student input features...")
        
        # Encode categorical variables
        student_encoded = pd.get_dummies(student_df, columns=[
            "major",
            "importance_close_to_home",
            "importance_school_reputation",
            "importance_school_cost"
        ])
        
        # Add missing columns that exist in training data
        for col in feature_cols:
            if col not in student_encoded.columns:
                student_encoded[col] = 0
                
        # Ensure columns are in the same order
        student_encoded = student_encoded[feature_cols]
        
        # Scale numeric features
        numeric_cols = ["SAT", "GPA"]
        student_encoded[numeric_cols] = scaler.transform(student_encoded[numeric_cols])
        
        logger.info("Student input processing completed")
        return student_encoded
        
    except Exception as e:
        logger.error(f"Error in process_student_input: {str(e)}")
        raise