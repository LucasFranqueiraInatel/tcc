import numpy as np
import pandas as pd
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import Embedding, SimpleRNN, Dense, LSTM
from keras._tf_keras.keras.preprocessing.text import Tokenizer
from keras._tf_keras.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import LabelEncoder
from keras.src.utils import to_categorical
from keras.src.models import Sequential
from keras.src.layers import Embedding, LSTM, Dense, Dropout
from transformers import BertTokenizer, TFBertForSequenceClassification

data = pd.read_json('./data/filtered_data.json')

tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(data['COMMENT'])
X = tokenizer.texts_to_sequences(data['COMMENT'])
X = pad_sequences(X, maxlen=100)  # Fixed sequence length

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(data['TARGET'])  # Integer encoding

y = to_categorical(y)  # Converts to one-hot vectors

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Sequential([
    Embedding(input_dim=10000, output_dim=128, input_length=100),  # Embedding layer
    LSTM(128, return_sequences=False, activation='tanh'),          # LSTM layer
    Dropout(0.2),                                                  # Dropout to prevent overfitting
    Dense(64, activation='relu'),                                  # Fully connected layer
    Dense(8, activation='softmax')                                 # Output layer (7-8 classes)
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(X_train, y_train, validation_split=0.2, epochs=10, batch_size=32)

test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_accuracy:.2f}")

# Get predicted probabilities
y_pred_probs = model.predict(X_test)

# Convert probabilities to class indices
y_pred = y_pred_probs.argmax(axis=-1)  # For multiclass classification

# If labels are one-hot encoded, convert them to class indices
y_test_classes = y_test.argmax(axis=-1)  # Converts one-hot labels back to integers

report = classification_report(y_test_classes, y_pred, target_names=label_encoder.classes_)
print(report)

