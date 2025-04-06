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

def classify_college(row, target_sat):
    """Helper function to classify colleges based on SAT score difference."""
    delta = row["avg_SAT"] - target_sat
    if -40 <= delta <= -20:
        return "Foundation"
    elif -10 <= delta <= 10:
        return "Thrive"
    elif 20 <= delta <= 40:
        return "Aspire"
    else:
        return "Other"

def calculate_distance(row, student_state):
    """Calculate a simple distance score based on state."""
    return 1 if row["state"] == student_state else 0

def generate_recommendations(student_features, encoded_df, feature_cols, student_data, logger):
    """
    Generate college recommendations based on student features.
    
    Args:
        student_features (pandas.DataFrame): Processed student input features
        encoded_df (pandas.DataFrame): Training data with encoded features
        feature_cols (list): List of feature columns to use
        student_data (dict): Original student input data
        logger: Logger object for output messages
        
    Returns:
        pandas.DataFrame: Recommendations with college statistics and categories
    """
    try:
        logger.info("Finding similar students...")
        
        # Get the student's SAT score and location
        target_sat = student_data["SAT"]
        student_state = student_data["state"]
        importance_location = student_data["importance_close_to_home"]
        
        # Initialize and fit KNN model
        knn = NearestNeighbors(n_neighbors=25)
        knn.fit(encoded_df[feature_cols])
        
        # Find nearest neighbors
        distances, indices = knn.kneighbors(student_features[feature_cols])
        
        # Load original data
        original_data_path = Path("../data/working_data/collegerecs_synthetic/student_college_history.csv")
        original_df = pd.read_csv(original_data_path)
        
        # Get similar students
        similar_students = original_df.iloc[indices[0]]
        
        # Calculate college statistics
        college_stats = similar_students.groupby("college_name").agg({
            "SAT": ["count", "mean"],
            "GPA": "mean",
            "state": lambda x: x.iloc[0],  # Get the state for each college
            "importance_close_to_home": "mean",
            "importance_school_reputation": "mean",
            "importance_school_cost": "mean"
        }).round(2)
        
        # Flatten column names
        college_stats.columns = [
            "num_similar_students",
            "avg_SAT",
            "avg_GPA",
            "state",
            "avg_importance_location",
            "avg_importance_reputation",
            "avg_importance_cost"
        ]
        
        # Reset index to make college_name a column
        college_stats = college_stats.reset_index()
        
        # Add distance information
        college_stats["same_state"] = college_stats.apply(
            lambda x: calculate_distance(x, student_state), axis=1
        )
        
        # Add category classification
        college_stats["category"] = college_stats.apply(
            lambda x: classify_college(x, target_sat), axis=1
        )
        
        # Adjust ranking based on location importance
        if importance_location >= 4:  # High importance on location
            # Prioritize in-state colleges
            college_stats["rank_score"] = (
                college_stats["num_similar_students"] * 
                (1 + 0.5 * college_stats["same_state"])
            )
        else:
            college_stats["rank_score"] = college_stats["num_similar_students"]
        
        # Get top colleges for each category
        categorized_colleges = []
        for category in ["Foundation", "Thrive", "Aspire"]:
            category_colleges = college_stats[college_stats["category"] == category] \
                .sort_values(by="rank_score", ascending=False) \
                .head(3)
            categorized_colleges.append(category_colleges)
        
        # Combine all categories
        final_recommendations = pd.concat(categorized_colleges, ignore_index=True)
        
        # Reorder columns
        column_order = [
            "college_name",
            "category",
            "state",
            "num_similar_students",
            "avg_SAT",
            "avg_GPA",
            "avg_importance_location",
            "avg_importance_reputation",
            "avg_importance_cost"
        ]
        final_recommendations = final_recommendations[column_order]
        
        logger.info(f"Generated recommendations across {len(final_recommendations)} colleges")
        logger.info(f"Categories represented: {final_recommendations['category'].unique()}")
        
        return final_recommendations
        
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