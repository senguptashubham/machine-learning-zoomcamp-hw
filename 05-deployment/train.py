import numpy as np
import pandas as pd
import pickle
import argparse
from pathlib import Path
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import precision_score, recall_score, precision_recall_curve, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer


# Parameters
RANDOM_STATE = 42
CSV_DATA_PATH = Path(__file__).resolve().parent / "course_lead_scoring_2026.csv"
n_splits = 5
OUTPUT_PATH = Path(__file__).resolve().parent / "model.bin"

# Metadata
float_cols = ["annual_income", "lead_score"]
integer_cols = ["number_of_courses_viewed", "interaction_count"]
catagorical_cols = ["lead_source", "industry", "employment_status", "location"]

# Data preprocessing

def load_and_clean_data(data_path:Path) -> pd.DataFrame:
  df = pd.read_csv(CSV_DATA_PATH)
  for col in df.columns:
    if df[col].dtype == 'str':
      df[col] = df[col].fillna('NA')
    else:
      df[col] = df[col].fillna(0.0)
  return df


def split_data(df: pd.DataFrame, test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
  df_train, df_test = train_test_split(
      df, test_size=test_size, random_state=RANDOM_STATE)
  return df_train, df_test

def get_encoded_k_folds(df:pd.DataFrame, k) -> tuple[list, list, list, list]:
  kf = KFold(n_splits=k, shuffle=True, random_state=RANDOM_STATE)
  train_fts, train_lbs, val_fts, val_lbs = [], [], [], []
  df_cpy = df.copy()
  y = df_cpy.pop('converted')
  X = df_cpy
  for i, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
    vec = DictVectorizer(sparse=False)
    train_dict = X_train.to_dict(orient='records')
    val_dict = X_val.to_dict(orient='records')
    train_data = vec.fit_transform(train_dict)
    val_data = vec.transform(val_dict)
    df_train = pd.DataFrame(train_data, columns=vec.get_feature_names_out())
    df_val = pd.DataFrame(val_data, columns=vec.get_feature_names_out())
    train_fts.append(df_train)
    train_lbs.append(y_train)
    val_fts.append(df_val)
    val_lbs.append(y_val)
  return train_fts, train_lbs, val_fts, val_lbs

# Training

def get_best_model(df_train:pd.DataFrame, c_vals:list, k=5) -> tuple[LogisticRegression, float | np.floating]:
  best_auc = float('-inf')
  return_model = LogisticRegression()
  for c in c_vals:
    train_fts, train_lbs, val_fts, val_lbs = get_encoded_k_folds(df_train, k=k)
    auc_scores = []
    best_score = float('-inf')
    best_model = LogisticRegression()
    for X_train, y_train, X_val, y_val in zip(train_fts, train_lbs, val_fts, val_lbs):
      model = LogisticRegression(solver='liblinear', C=c, max_iter=1000)
      model.fit(X_train, y_train)
      y_pred = model.predict(X_val)
      score = roc_auc_score(y_val, y_pred)
      auc_scores.append(score)
      if score > best_score:
        best_score = score
        best_model = model
    mean_auc = np.mean(auc_scores)
    if mean_auc > best_auc:
      best_auc = mean_auc
      return_model = best_model
  return (return_model, best_auc)


def train(df_train, model):
  y_train = df_train.pop('converted')
  X_train = df_train
  vec = DictVectorizer(sparse=False)
  train_dict = X_train.to_dict(orient='records')
  train_data = vec.fit_transform(train_dict)
  df_train = pd.DataFrame(train_data, columns=vec.get_feature_names_out())
  model.fit(df_train, y_train)
  return vec, model

# Evaluation

def evaluate(df_test, vectorizer, model):
  df_cpy = df_test.copy()
  y_test = df_cpy.pop('converted')
  X_test = df_cpy
  test_dict = X_test.to_dict(orient='records')
  test_data = vectorizer.transform(test_dict)
  df_test = pd.DataFrame(test_data, columns=vectorizer.get_feature_names_out())
  y_pred = model.predict(df_test)
  score = roc_auc_score(y_test, y_pred)
  return score

# Save Model

def save_model(model, vectorizer):
  with open(OUTPUT_PATH, 'wb') as f_out:
    pickle.dump((vectorizer, model), f_out)

# Load Model

def load_model(model_path:Path):
  with open(model_path, 'rb') as f_in:
    vec, model = pickle.load(f_in)
  return vec, model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the ML Zoomcamp 2026 model")
    parser.add_argument("--data", type=Path, default=CSV_DATA_PATH)
    parser.add_argument("--model", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    df = load_and_clean_data(args.data)
    model, score = get_best_model(df, [0.01, 0.1, 1, 10], k=5)
    print(f"Best model scored: {score}")
    df_train, df_test = split_data(df)
    df_test_cpy = df_test.copy()
    vec, model = train(df_train, model)
    test_score1 = evaluate(df_test, vec, model)
    print(f"Score for test 1: {test_score1}")
    assert abs(test_score1 - score) < 0.15
    save_model(model, vec)
    print("Model saved successfully...")
    vec_n, model_n = load_model(OUTPUT_PATH)
    print("Model loaded successfully...")
    test_score2 = evaluate(df_test_cpy, vec_n, model_n)
    print(f"Score for test 2: {test_score2}")
    assert np.isclose(test_score1, test_score2)
