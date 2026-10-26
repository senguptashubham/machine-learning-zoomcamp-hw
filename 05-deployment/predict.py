import pandas as pd
import pickle
import argparse
from pathlib import Path
from flask import Flask
from flask import request
from flask import jsonify
from sklearn.feature_extraction import DictVectorizer

app = Flask('course-lead')

MODEL_PATH = Path(__file__).resolve().parent / "model.bin"


def load_model(model_path: Path):
  with open(model_path, 'rb') as f_in:
    vec, model = pickle.load(f_in)
  return vec, model

@app.route('/predict', methods=['POST'])
def predict():
  vectorizer, model = load_model(MODEL_PATH)
  customer = request.get_json()
  test_data = vectorizer.transform(customer)
  df_test = pd.DataFrame(test_data, columns=vectorizer.get_feature_names_out())
  y_pred = model.predict(df_test)
  result = {
    "converted":bool(y_pred[0])
  }
  return jsonify(result)


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=9696)