import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import json

# Load tokenizer from local storage
def load_tokenizer(tokenizer_path):
    with open(tokenizer_path, 'r') as f:
        tokenizer_json = json.load(f)
    tokenizer = tf.keras.preprocessing.text.Tokenizer()
    tokenizer.word_index = tokenizer_json['word_index']
    return tokenizer

# Load models from local storage
def load_models(encoder_path, decoder_path):
    encoder_model = tf.keras.models.load_model(encoder_path)
    decoder_model = tf.keras.models.load_model(decoder_path)
    return encoder_model, decoder_model

# Temperature-based sampling function
def sample_with_temperature(predictions, temperature=1.0):
    predictions = np.asarray(predictions).astype("float64")
    predictions = np.log(predictions + 1e-10) / temperature  # Apply temperature scaling
    exp_preds = np.exp(predictions)
    probabilities = exp_preds / np.sum(exp_preds)  # Convert logits to probabilities
    return np.random.choice(len(predictions), p=probabilities)  # Sample token

# Generate recipe function (Fixed)
def generate_recipe(ingredients, tokenizer, encoder_model, decoder_model, max_length=100, temperature=0.8):
    sequence = tokenizer.texts_to_sequences([ingredients])
    sequence = pad_sequences(sequence, maxlen=max_length, padding='post')

    states = encoder_model.predict(sequence)
    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = tokenizer.word_index.get('<start>', 1)  # Ensure <start> token exists
    recipe = []

    for _ in range(max_length):
        output_tokens, h, c = decoder_model.predict([target_seq] + states)

        # Sample a word with temperature instead of greedy argmax
        sampled_token_index = sample_with_temperature(output_tokens[0, -1, :], temperature=temperature)
        sampled_word = {v: k for k, v in tokenizer.word_index.items()}.get(sampled_token_index, '')

        if sampled_word == '<end>' or sampled_word == '':
            break

        recipe.append(sampled_word)
        target_seq[0, 0] = sampled_token_index
        states = [h, c]

    return ' '.join(recipe)
