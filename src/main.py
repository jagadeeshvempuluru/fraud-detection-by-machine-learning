import pandas as pd
import numpy as np
from preprocessing import DataPreprocessor
from models import FraudDetectionModel
import joblib
import os

def load_data(file_path):
    # Load the data from CSV file
    df = pd.read_csv(file_path)
    return df

def save_model(model, file_path):
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    joblib.dump(model, file_path)

def load_saved_model(file_path):
    return joblib.load(file_path)
def get_sample_prediction_data():
    # Return sample data format for API prediction
    sample_data = {
        "amount": 123.45,
        "time": 12345,
        "v1": 0.123,
        "v2": -0.456,
        "v3": 1.234,
        # Add other V features with sample values
        "v28": -0.089
    }
    return sample_data
    
def main():
    # Sample usage of the fraud detection system
    try:
        # Load data
        print("Loading data...")
        data = load_data('data/transactions.csv')
        
        # Print basic data info
        print(f"Data loaded. Shape: {data.shape}")
        print(f"Columns: {data.columns.tolist()}")
        
        # Check and convert Label to numeric
        if 'Label' in data.columns:
            print("Converting Label to numeric values...")
            # Check if Label is already numeric
            if data['Label'].dtype == np.int64 or data['Label'].dtype == np.float64:
                print("Label is already numeric.")
            else:
                # Map text labels to numbers
                label_mapping = {'Legitimate': 0, 'Fraudulent': 1}
                if data['Label'].isin(label_mapping.keys()).all():
                    data['Label'] = data['Label'].map(label_mapping)
                    print("Label converted using mapping.")
                else:
                    # Handle other cases
                    unique_labels = data['Label'].unique()
                    print(f"Unknown label values: {unique_labels}")
                    # Create a mapping for all unique values
                    custom_mapping = {val: idx for idx, val in enumerate(unique_labels)}
                    data['Label'] = data['Label'].map(custom_mapping)
                    print(f"Created custom mapping: {custom_mapping}")
        
        # Preprocess data
        print("Preprocessing data...")
        preprocessor = DataPreprocessor()
        processed_data = preprocessor.preprocess_data(data)
        
        # Prepare features and target
        if 'Label' in processed_data.columns:
            X = processed_data.drop('Label', axis=1)
            y = processed_data['Label']
            print(f"Features shape: {X.shape}")
            print(f"Target shape: {y.shape}")
            print(f"Target values: {np.unique(y)}")
        else:
            raise ValueError("Label column not found in processed data.")
        
        # Train and evaluate models
        print("Training models...")
        fraud_detector = FraudDetectionModel()
        results = fraud_detector.train_evaluate(X, y)
        
        # Print results
        print("\nEvaluation Results:")
        for model_name, metrics in results.items():
            print(f"\nResults for {model_name}:")
            print(f"Precision: {metrics['precision']:.4f}")
            print(f"Recall: {metrics['recall']:.4f}")
            print(f"F1-Score: {metrics['f1']:.4f}")
            print(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        
        # Get best model information
        best_model_info = fraud_detector.get_best_model_info()
        print(f"\nBest performing model: {best_model_info['model_name']}")
        print(f"Best F1-Score: {best_model_info['best_score']:.4f}")
        
        # Save the best model
        print("Saving best model...")
        save_model(fraud_detector.best_model, 'models/best_model.joblib')
        print("Model saved successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()