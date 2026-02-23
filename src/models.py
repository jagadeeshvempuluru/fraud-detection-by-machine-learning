import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf

class FraudDetectionModel:
    def __init__(self):
        self.models = {
            'logistic': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': XGBClassifier(random_state=42)
            # Neural network will be created separately
        }
        self.best_model = None
        self.best_model_name = None
        self.best_score = 0
    
    def create_neural_network(self, input_dim):
        # Reset the TensorFlow graph
        tf.keras.backend.clear_session()
        
        model = Sequential([
            Dense(64, activation='relu', input_dim=input_dim),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001),
                     loss='binary_crossentropy',
                     metrics=['accuracy'])
        return model
    
    def train_evaluate(self, X, y, test_size=0.2):
        # Ensure y is 1-dimensional
        if len(y.shape) > 1 and y.shape[1] > 1:
            print(f"Warning: Target variable has shape {y.shape}. Converting to 1D array.")
            # If y is one-hot encoded, convert to class indices
            y = np.argmax(y, axis=1)
        
        # Print data shapes for debugging
        print(f"X shape: {X.shape}, y shape: {y.shape}, y dtype: {y.dtype}")
        
        # Convert y to numpy array if it's a pandas Series
        if hasattr(y, 'values'):
            y = y.values
        
        # Ensure y is the right type
        y = y.astype(int)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Create neural network
        self.models['neural_network'] = self.create_neural_network(X.shape[1])
        
        results = {}
        for name, model in self.models.items():
            print(f"Training {name} model...")
            try:
                if name == 'neural_network':
                    # Reshape y to 1D array before passing to model
                    y_train_1d = y_train.reshape(-1)
                    model.fit(X_train, y_train_1d, epochs=10, batch_size=32, verbose=1)
                    y_pred = (model.predict(X_test) > 0.5).astype(int).reshape(-1)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Ensure y_test and y_pred are 1D
                y_test_1d = y_test.reshape(-1)
                y_pred_1d = y_pred.reshape(-1)
                
                # Calculate metrics
                results[name] = {
                    'precision': precision_score(y_test_1d, y_pred_1d),
                    'recall': recall_score(y_test_1d, y_pred_1d),
                    'f1': f1_score(y_test_1d, y_pred_1d),
                    'auc_roc': roc_auc_score(y_test_1d, y_pred_1d),
                    'accuracy': (y_pred_1d == y_test_1d).mean(),
                    'confusion_matrix': confusion_matrix(y_test_1d, y_pred_1d)
                }
                
                # Update best model
                if results[name]['f1'] > self.best_score:
                    self.best_score = results[name]['f1']
                    self.best_model = model
                    self.best_model_name = name
                    
                print(f"  {name} F1 Score: {results[name]['f1']:.4f}")
                
            except Exception as e:
                print(f"Error training {name} model: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Add empty results to avoid breaking the code
                results[name] = {
                    'precision': 0,
                    'recall': 0,
                    'f1': 0,
                    'auc_roc': 0,
                    'accuracy': 0,
                    'confusion_matrix': np.array([[0, 0], [0, 0]])
                }
        
        return results
    
    def predict(self, X):
        if self.best_model is None:
            raise ValueError("Model hasn't been trained yet!")
        
        if self.best_model_name == 'neural_network':
            return (self.best_model.predict(X) > 0.5).astype(int).reshape(-1)
        return self.best_model.predict(X)
    
    def get_best_model_info(self):
        return {
            'model_name': self.best_model_name,
            'best_score': self.best_score
        }