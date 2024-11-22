import numpy as np 
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from keras._tf_keras.keras.utils import to_categorical
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf

# Load and clean data
data = pd.read_json('./data/filtered_data.json')

# Drop missing values in 'COMMENT' and 'TARGET'
data = data.dropna(subset=['COMMENT', 'TARGET'])

# Initialize the BERT tokenizer
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenize all comments with BERT tokenizer
bert_inputs = bert_tokenizer(
    list(data['COMMENT']), 
    padding=True, 
    truncation=True, 
    max_length=100, 
    return_tensors="tf"
)

# Extract input tensors for BERT
X = bert_inputs['input_ids']  # Input IDs
attention_masks = bert_inputs['attention_mask']  # Attention masks

# Encode target labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(data['TARGET'])  # Convert labels to integers
y = to_categorical(y)  # Convert to one-hot encoding for classification

# Check alignment of X and y
assert X.shape[0] == y.shape[0], "Mismatch between inputs and labels!"

# Split data into training and testing sets
X_train, X_test, attn_train, attn_test, y_train, y_test = train_test_split(
    X, attention_masks, y, test_size=0.2, random_state=42
)

# Use the TFBertForSequenceClassification model
bert_model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=y.shape[1])

# Compile the model
bert_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=2e-5), 
    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']
)

# Train the model
history = bert_model.fit(
    {'input_ids': X_train, 'attention_mask': attn_train}, 
    y_train, 
    validation_split=0.2, 
    epochs=3, 
    batch_size=8  # Reduce batch size if memory issues arise
)

# Evaluate the model
test_loss, test_accuracy = bert_model.evaluate(
    {'input_ids': X_test, 'attention_mask': attn_test}, 
    y_test
)
print(f"Test Accuracy: {test_accuracy:.2f}")

# Make predictions
y_pred_logits = bert_model.predict({'input_ids': X_test, 'attention_mask': attn_test})
y_pred = tf.argmax(y_pred_logits.logits, axis=1).numpy()

# Convert true and predicted labels to integer format
y_test_classes = tf.argmax(y_test, axis=1).numpy()

# Generate classification report
report = classification_report(y_test_classes, y_pred, target_names=label_encoder.classes_)
print(report)
