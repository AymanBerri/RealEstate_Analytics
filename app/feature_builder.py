# This file's only task is to convert user input into a DataFrame

import pandas as pd
import numpy as np

def build_features(user_input, model_columns):
    """
    user_input: dict with user selections
    model_columns: list of columns used during training
    """

    # Create empty row with ALL columns set to 0
    X = pd.DataFrame(0, index=[0], columns=model_columns)

    # Numerical features
    X["bedrooms_clean"] = user_input["bedrooms"]
    X["bathrooms_clean"] = user_input["bathrooms"]
    X["area_clean"] = user_input["area"]
    X["area_per_bedroom"] = user_input["area"] / max(user_input["bedrooms"], 1)
    X["bathrooms_per_bedroom"] = user_input["bathrooms"] / max(user_input["bedrooms"], 1)
    X["log_area"] = np.log(user_input["area"])


    # Encoding, bec the model was trained on encoded values, and to use the model we must do the same for the input.
    # One-hot: building
    building_col = f"building_grouped_{user_input['building']}"
    if building_col in X.columns:
        X[building_col] = 1

    # One-hot: district
    district_col = f"district_{user_input['district']}"
    if district_col in X.columns:
        X[district_col] = 1

    return X
