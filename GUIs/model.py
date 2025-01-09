import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import os
from joblib import dump, load

# Filepath for saving the model
model_file = "salary_prediction_model.joblib"

# Load and preprocess the dataset
data = pd.read_csv("data/Salary.csv")

# Handle missing values
numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

# Separate features and target variable
x = data.drop('Salary', axis=1)
y = data['Salary']

# Identify categorical and numeric columns
categorical_columns = x.select_dtypes(include=['object']).columns
numeric_columns = x.select_dtypes(include=['float64', 'int64']).columns

# Create a column transformer with one-hot encoding and scaling
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_columns),
        ('num', StandardScaler(), numeric_columns)
    ],
    remainder='passthrough'  # Keep remaining columns as they are
)

# Use Random Forest Regressor
model = RandomForestRegressor(random_state=0)

# Create a pipeline with the preprocessor and model
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', model)
])

# Check if a pre-trained model exists
if os.path.exists(model_file):
    # Load the saved model
    best_model = load(model_file)
    print(f"Model loaded from {model_file}")
else:
    # Split the dataset into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

    # Perform hyperparameter tuning using GridSearchCV
    param_grid = {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [None, 10, 20, 30],
        'model__min_samples_split': [2, 5, 10]
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_absolute_error', verbose=2, n_jobs=-1)
    grid_search.fit(x_train, y_train)

    # Use the best model from the grid search
    best_model = grid_search.best_estimator_

    # Save the trained model to disk
    dump(best_model, model_file)
    print(f"Model saved to {model_file}")

# Make predictions
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)  # Ensure testing data exists
predictions = best_model.predict(x_test)

# Evaluate the model
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print(f"Mean Absolute Error: {mae:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")

# Function to predict salary
def predict_salary(age, gender, education_level, job_title, years_of_experience, country, race, senior):
    # Create a DataFrame with the input data
    input_data = pd.DataFrame({
        'Age': [age],
        'Gender': [gender],
        'Education Level': [education_level],
        'Job Title': [job_title],
        'Years of Experience': [years_of_experience],
        'Country': [country],
        'Race': [race],
        'Senior': [senior]
    })

    # Use the pipeline to preprocess the input data and make a prediction
    predicted_salary = best_model.predict(input_data)
    return predicted_salary[0]
