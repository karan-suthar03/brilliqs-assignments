"""Load the penguin data, clean it, and turn it into numbers for the model."""

import pandas as pd

INPUT_FILE = "penguins.csv"
MEASUREMENTS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
TARGET = "species"


def load_clean():
    df = pd.read_csv(INPUT_FILE)

    # year is just when the survey ran, it says nothing about the penguin
    df = df.drop(columns=["year"])

    # two rows have no measurements at all, so there is nothing to impute from
    df = df.dropna(subset=MEASUREMENTS)

    # sex is missing for 11 birds, fill with whichever is more common
    df["sex"] = df["sex"].fillna(df["sex"].mode()[0])

    return df


def encode(df):
    df = df.copy()
    df["sex"] = (df["sex"] == "male").astype(int)
    df = pd.get_dummies(df, columns=["island"], prefix="island")
    return df
