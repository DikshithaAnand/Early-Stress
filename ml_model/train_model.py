"""
Train the stress detection model using synthetic data.
Run this script once to generate the model file: stress_model.pkl
"""

import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

np.random.seed(42)

def generate_stress_data(n_samples=2000):
    """Generate synthetic stress dataset based on lifestyle factors."""
    data = []
    labels = []

    for _ in range(n_samples):
        # Low stress profile
        if np.random.random() < 0.33:
            sleep = np.random.uniform(7, 9)
            study = np.random.uniform(4, 7)
            social_media = np.random.uniform(0.5, 2)
            screen_time = np.random.uniform(2, 5)
            mood = np.random.choice([4, 5], p=[0.3, 0.7])  # Happy/Very Happy
            label = 0  # Low Stress

        # Moderate stress profile
        elif np.random.random() < 0.5:
            sleep = np.random.uniform(5.5, 7.5)
            study = np.random.uniform(7, 10)
            social_media = np.random.uniform(2, 4)
            screen_time = np.random.uniform(5, 8)
            mood = np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3])  # Neutral/Stressed
            label = 1  # Moderate Stress

        # High stress profile
        else:
            sleep = np.random.uniform(2, 5.5)
            study = np.random.uniform(10, 16)
            social_media = np.random.uniform(4, 8)
            screen_time = np.random.uniform(8, 14)
            mood = np.random.choice([1, 2], p=[0.6, 0.4])  # Stressed/Very Stressed
            label = 2  # High Stress

        # Add noise
        sleep = max(0, min(sleep + np.random.normal(0, 0.3), 12))
        study = max(0, min(study + np.random.normal(0, 0.5), 18))
        social_media = max(0, min(social_media + np.random.normal(0, 0.2), 12))
        screen_time = max(0, min(screen_time + np.random.normal(0, 0.4), 18))

        data.append([sleep, study, social_media, screen_time, mood])
        labels.append(label)

    return np.array(data), np.array(labels)


def train():
    print("Generating training data...")
    X, y = generate_stress_data(3000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Low Stress', 'Moderate Stress', 'High Stress']))

    with open('stress_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("\n✅ Model saved to stress_model.pkl")
    return model


if __name__ == "__main__":
    train()
