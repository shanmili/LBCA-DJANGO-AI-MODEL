import joblib
import os

class Model:
    def __init__(self):
        # Path to your student performance .pkl file
        model_path = os.path.join("model", "best_student_performance_model.pkl")
        self.model = joblib.load(model_path)

    def predict(self, features: list):
        # Your model expects 10 features based on the file content
        result = self.model.predict([features])
        return result.tolist()

model_instance = Model()