import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from datetime import datetime

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.categorical_features = {}
        self.encoders = {}
        self.is_fitted = False

    def fit(self, df):
        # Store unique values for each categorical column
        categorical_columns = ['Payment_Method', 'Device_Info', 'City', 'Country']
        categorical_columns = [col for col in categorical_columns if col in df.columns]
        
        for col in categorical_columns:
            top_categories = df[col].value_counts().nlargest(10).index.tolist()
            self.categorical_features[col] = top_categories
        
        self.is_fitted = True
        return self

    def preprocess_data(self, df):
        # Create a copy of the dataframe
        df = df.copy()
        
        try:
            # First extract the Label column if it exists
            label = None
            if 'Label' in df.columns:
                label = df['Label'].copy()
                # Remove Label from processing
                df = df.drop('Label', axis=1)
            
            # Remove Transaction_ID as it's not useful for modeling
            if 'Transaction_ID' in df.columns:
                df = df.drop('Transaction_ID', axis=1)
            
            # Convert timestamp to datetime features
            if 'Timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                df['Hour'] = df['Timestamp'].dt.hour
                df['Day'] = df['Timestamp'].dt.day
                df['Month'] = df['Timestamp'].dt.month
                df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
            
            # Extract location features
            if 'Location' in df.columns:
                try:
                    df[['City', 'Country']] = df['Location'].str.split(', ', expand=True)
                except:
                    df['City'] = df['Location'].apply(lambda x: str(x).split(', ')[0] if isinstance(x, str) and ', ' in x else 'unknown')
                    df['Country'] = df['Location'].apply(lambda x: str(x).split(', ')[1] if isinstance(x, str) and ', ' in x and len(str(x).split(', ')) > 1 else 'unknown')
            
            # Convert IP address to features (simplify by just using the first octet)
            if 'IP_Address' in df.columns:
                df['IP_First_Octet'] = df['IP_Address'].apply(
                    lambda x: int(str(x).split('.')[0]) if isinstance(x, str) and '.' in str(x) else np.nan
                )
                df = df.drop('IP_Address', axis=1)
            
            # Identify categorical and numeric columns
            categorical_columns = ['Payment_Method', 'Device_Info', 'City', 'Country']
            categorical_columns = [col for col in categorical_columns if col in df.columns]
            
            numeric_columns = ['Amount', 'Hour', 'Day', 'Month', 'DayOfWeek', 'IP_First_Octet']
            numeric_columns = [col for col in numeric_columns if col in df.columns]
            
            # Process categorical columns
            if categorical_columns:
                for col in categorical_columns:
                    df[col] = df[col].fillna('unknown')
                    
                    if self.is_fitted:
                        # Use stored categories from training
                        known_categories = self.categorical_features.get(col, [])
                        df[col] = df[col].apply(lambda x: x if x in known_categories else 'other')
                    else:
                        # During training, store top categories
                        top_categories = df[col].value_counts().nlargest(10).index
                        df[col] = df[col].apply(lambda x: x if x in top_categories else 'other')
                        self.categorical_features[col] = top_categories.tolist()
                
                # One-hot encode each categorical column separately
                encoded_dfs = []
                for col in categorical_columns:
                    if not self.is_fitted or col not in self.encoders:
                        # During training, create and fit a new encoder
                        self.encoders[col] = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                        encoded = self.encoders[col].fit_transform(df[[col]])
                    else:
                        # During prediction, use the stored encoder
                        encoded = self.encoders[col].transform(df[[col]])
                    
                    encoded_df = pd.DataFrame(
                        encoded, 
                        columns=[f"{col}_{cat}" for cat in self.encoders[col].categories_[0]], 
                        index=df.index
                    )
                    encoded_dfs.append(encoded_df)
                
                # Join all encoded features
                if encoded_dfs:
                    encoded_features = pd.concat(encoded_dfs, axis=1)
                    
                    # Drop original categorical columns
                    df = df.drop(categorical_columns, axis=1)
                    
                    # Join with encoded features
                    df = pd.concat([df, encoded_features], axis=1)
            
            # Scale numeric columns
            if numeric_columns:
                # Handle missing values
                df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
                
                # Scale the features
                df[numeric_columns] = self.scaler.fit_transform(df[numeric_columns])
            
            # Remove original columns that are no longer needed
            if 'Timestamp' in df.columns:
                df = df.drop('Timestamp', axis=1)
            if 'Location' in df.columns:
                df = df.drop('Location', axis=1)
            
            # Add back the Label column if it existed
            if label is not None:
                df['Label'] = label
            
            return df
        
        except Exception as e:
            raise Exception(f'Error in preprocessing: {str(e)}')
    
    def get_feature_names(self):
        return ['Amount', 'Hour', 'Day', 'Month', 'DayOfWeek', 'IP_First_Octet',
                'Payment_Method', 'Device_Info', 'City', 'Country']