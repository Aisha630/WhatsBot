from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import numpy as np
from joblib import dump
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

with open("./english.txt", "r") as file:
    lines = file.readlines()
    english_sentences = [line.rstrip("\n") for line in lines]
with open("./roman_urdu.txt", "r") as file:
    lines = file.readlines()
    urdu_sentences = [line.rstrip("\n") for line in lines]
    
    
# Labels: 0 for English, 1 for Urdu written in English script
data = english_sentences + urdu_sentences
labels = np.array([0] * len(english_sentences) + [1] * len(urdu_sentences))

# X_train, X_test, y_train, y_test = train_test_split(
#     data, labels, test_size=0.2, random_state=42)

y_train = labels

vectorizer = TfidfVectorizer()
# X_train_vectors = vectorizer.fit_transform(X_train)
X_train_vectors = vectorizer.fit_transform(data)
# X_test_vectors = vectorizer.transform(X_test)

model = SVC(kernel='linear')
model.fit(X_train_vectors, y_train)

# y_pred = model.predict(X_test_vectors)

print(model.predict(vectorizer.transform(
    ["Ap mujhse shaadi krogi kiya"])))
print(model.predict(vectorizer.transform(
    ["Stomach ache k lye kiya precautions zaroori hain"])))
print(model.predict(vectorizer.transform(
    ["How can I check apna or baakion ka balance without internet?"])))

dump(model, 'model.joblib')
dump(vectorizer, 'vectorizer.joblib')
# print("Classification Report:\n", classification_report(y_test, y_pred))
# accuracy = accuracy_score(y_test, y_pred)
# print("Accuracy:", accuracy)
