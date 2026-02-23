from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import ModelTrainingForm, PredictionForm
from .models import TrainedModel, PredictionHistory
import pandas as pd
import joblib
from src.preprocessing import DataPreprocessor
from src.models import FraudDetectionModel

@staff_member_required
def train_model(request):
    if request.method == 'POST':
        form = ModelTrainingForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Load and preprocess data
                dataset = pd.read_csv(request.FILES['dataset'])
                preprocessor = DataPreprocessor()
                # First fit the preprocessor
                preprocessor.fit(dataset)
                # Then preprocess the data
                processed_data = preprocessor.preprocess_data(dataset)
                
                # Prepare features and target
                X = processed_data.drop('Label', axis=1)
                y = dataset['Label'].map({'Legitimate': 0, 'Fraudulent': 1})
                
                # Train and evaluate models
                fraud_detector = FraudDetectionModel()
                results = fraud_detector.train_evaluate(X, y)
                
                # Save selected models
                selected_algorithms = form.cleaned_data['algorithms']
                for algorithm in selected_algorithms:
                    if algorithm in results:
                        metrics = results[algorithm]
                        model = TrainedModel(
                            name=f'{algorithm}_model',
                            algorithm=algorithm,
                            precision=metrics['precision'],
                            recall=metrics['recall'],
                            f1_score=metrics['f1'],
                            auc_roc=metrics['auc_roc'],
                            accuracy=metrics['accuracy'],
                            is_active=True
                        )
                        # Save the model file and preprocessor
                        if algorithm == 'neural_network':
                            model_path = f'fraud_detection/models/{algorithm}_model.keras'
                            fraud_detector.models[algorithm].save(model_path)
                        else:
                            model_path = f'fraud_detection/models/{algorithm}_model.joblib'
                            joblib.dump(fraud_detector.models[algorithm], model_path)
                        model.model_file.name = model_path
                        
                        # Save preprocessor along with the model
                        preprocessor_path = f'fraud_detection/models/{algorithm}_preprocessor.joblib'
                        joblib.dump(preprocessor, preprocessor_path)
                        model.preprocessor_file = preprocessor_path
                        model.save()
                
                messages.success(request, 'Models trained and saved successfully!')
                return redirect('model_comparison')
            except Exception as e:
                messages.error(request, f'Error during training: {str(e)}')
    else:
        form = ModelTrainingForm()
    
    return render(request, 'fraud_detection/train_model.html', {'form': form})

@staff_member_required
def model_comparison(request):
    models = TrainedModel.objects.all().order_by('-created_at')
    return render(request, 'fraud_detection/model_comparison.html', {'models': models})

@staff_member_required
def toggle_model_status(request, model_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            model = TrainedModel.objects.get(id=model_id)
            model.is_active = data.get('is_active', False)
            model.save()
            return JsonResponse({'success': True})
        except TrainedModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Model not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def predict(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            try:
                # Get the selected model
                model = form.cleaned_data['model']
                
                # Prepare input data
                input_data = {
                    'Amount': form.cleaned_data['amount'],
                    'IP_Address': form.cleaned_data['ip_address'],
                    'Timestamp': form.cleaned_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'Location': f"{form.cleaned_data['location']}, USA",  # Append country for consistency
                    'Payment_Method': form.cleaned_data['payment_method'],
                    'Device_Info': form.cleaned_data['device_info']
                }
                
                # Create DataFrame
                df = pd.DataFrame([input_data])
                
                # Load the saved preprocessor and model
                loaded_model = joblib.load(model.model_file.path)
                
                # Load the preprocessor that was used during training
                if hasattr(model, 'preprocessor_file') and model.preprocessor_file:
                    preprocessor = joblib.load(model.preprocessor_file.path)
                else:
                    # Fallback to a new preprocessor if the saved one is not available
                    preprocessor = DataPreprocessor()
                    preprocessor.fit(df)  # Try to fit with current data
                
                # Preprocess the data using the loaded preprocessor
                processed_data = preprocessor.preprocess_data(df)
                if model.algorithm == 'neural_network':
                    prediction_prob = loaded_model.predict(processed_data)[0][0]
                else:
                    prediction_prob = loaded_model.predict_proba(processed_data)[0][1]
                
                prediction = prediction_prob >= 0.5
                
                # Save prediction history with the current user
                PredictionHistory.objects.create(
                    model=model,
                    user=request.user,  # Add the authenticated user
                    input_data=input_data,
                    prediction=prediction,
                    prediction_probability=prediction_prob
                )
                
                return render(request, 'fraud_detection/prediction_result.html', {
                    'prediction': prediction,
                    'probability': prediction_prob
                })
            except Exception as e:
                messages.error(request, f'Error during prediction: {str(e)}')
    else:
        form = PredictionForm()
    
    return render(request, 'fraud_detection/predict.html', {'form': form})
