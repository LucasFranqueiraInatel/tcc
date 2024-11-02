import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_json('filtered_data.json')

# Encode target labels
label_encoder = LabelEncoder()
df['TARGET'] = label_encoder.fit_transform(df['TARGET'])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['COMMENT'], df['TARGET'], test_size=0.2, random_state=42)

# Use TF-IDF to vectorize the text data
vectorizer = TfidfVectorizer(max_features=5000)  # You can tune max_features based on your needs
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Predict on the test set
y_pred = model.predict(X_test_tfidf)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=label_encoder.classes_))
