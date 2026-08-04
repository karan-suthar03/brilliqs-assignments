"""Walk through the whole thing: raw data, features, how the model decides,
and whether it is cheating.

Close each window to move on to the next step.
"""

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from prepare_data import MEASUREMENTS, TARGET, encode, load_clean

COLOURS = {"Adelie": "tab:blue", "Chinstrap": "tab:orange", "Gentoo": "tab:green"}
PAIR = ["bill_length_mm", "bill_depth_mm"]


def step_1_raw_and_cleaning(df):
    raw = pd.read_csv("penguins.csv")

    print("STEP 1 - the raw file")
    print(raw.head(6).to_string(index=False))
    print(f"\n  {len(raw)} rows, {raw.isna().sum().sum()} missing values")
    print(f"  dropped {len(raw) - len(df)} rows with no measurements at all")
    print(f"  filled 11 missing sex values with '{raw['sex'].mode()[0]}'")
    print(f"  left with {len(df)} clean rows\n")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    missing = raw.isna().sum()
    axes[0].bar(missing.index, missing.values, color="tomato")
    axes[0].set(ylabel="rows missing", title="missing values in the raw file")
    axes[0].tick_params(axis="x", rotation=30)

    axes[1].bar(["raw", "cleaned"], [len(raw), len(df)], color=["tomato", "seagreen"])
    axes[1].set(ylabel="rows", title="rows kept after cleaning")

    fig.suptitle("Step 1: the raw data and what cleaning did to it")
    plt.tight_layout()
    plt.show()


def step_2_features(df):
    corr = encode(df).drop(columns=[TARGET]).corr()

    print("STEP 2 - what separates the species")
    print(df.groupby(TARGET)[MEASUREMENTS].mean().round(1).to_string())
    print("\ncorrelations:")
    print(corr.round(2).to_string() + "\n")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    for species, data in df.groupby(TARGET):
        axes[0].scatter(data[PAIR[0]], data[PAIR[1]], color=COLOURS[species],
                        label=species, alpha=0.8)
        axes[1].scatter(data["flipper_length_mm"], data["body_mass_g"],
                        color=COLOURS[species], label=species, alpha=0.8)

    axes[0].set(xlabel="bill length (mm)", ylabel="bill depth (mm)",
                title="bill length vs depth")
    axes[0].legend()
    axes[1].set(xlabel="flipper length (mm)", ylabel="body mass (g)",
                title="flipper vs mass")
    axes[1].legend()

    axes[2].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    axes[2].set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right", fontsize=7)
    axes[2].set_yticks(range(len(corr)), corr.columns, fontsize=7)
    axes[2].set_title("correlations")
    for i in range(len(corr)):
        for j in range(len(corr)):
            axes[2].text(j, i, f"{corr.iloc[i, j]:.1f}", ha="center", va="center", fontsize=6)

    fig.suptitle("Step 2: three separate clouds - this is what makes it learnable")
    plt.tight_layout()
    plt.show()


def step_3_decision_boundary(df):
    print("STEP 3 - how the model decides")
    print("trained on bill length and depth only, so the decision can be drawn\n")

    X = df[PAIR]
    y = df[TARGET]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # predict every point on a grid, so the regions can be shaded
    xx, yy = np.meshgrid(
        np.arange(X[PAIR[0]].min() - 2, X[PAIR[0]].max() + 2, 0.1),
        np.arange(X[PAIR[1]].min() - 1, X[PAIR[1]].max() + 1, 0.05),
    )
    grid = pd.DataFrame({PAIR[0]: xx.ravel(), PAIR[1]: yy.ravel()})

    species_order = sorted(y.unique())
    predicted = model.predict(grid)
    as_numbers = np.array([species_order.index(s) for s in predicted]).reshape(xx.shape)

    plt.figure(figsize=(10, 7))
    plt.contourf(xx, yy, as_numbers, alpha=0.25,
                 cmap=ListedColormap([COLOURS[s] for s in species_order]))

    for species, data in df.groupby(TARGET):
        plt.scatter(data[PAIR[0]], data[PAIR[1]], color=COLOURS[species],
                    label=species, edgecolor="black", linewidth=0.4)

    plt.title("Step 3: shaded areas are what the model would guess for any penguin")
    plt.xlabel("bill length (mm)")
    plt.ylabel("bill depth (mm)")
    plt.legend()
    plt.tight_layout()
    plt.show()


def step_4_is_it_cheating(df):
    encoded = encode(df)
    y = encoded[TARGET]

    print("STEP 4 - a perfect score is suspicious, so check it")
    print(pd.crosstab(df["island"], df[TARGET]).to_string())
    print("\nGentoo only live on Biscoe and Chinstrap only on Dream, so island")
    print("nearly gives the answer away. Does the model depend on it?\n")

    tests = {
        "everything": [c for c in encoded.columns if c != TARGET],
        "no island": MEASUREMENTS + ["sex"],
        "measurements only": MEASUREMENTS,
        "island only": [c for c in encoded.columns if c.startswith("island_")],
        "bill length only": ["bill_length_mm"],
    }

    names, scores = [], []
    for label, columns in tests.items():
        score = cross_val_score(RandomForestClassifier(n_estimators=100, random_state=42),
                                encoded[columns], y, cv=5).mean()
        print(f"  {label:<20} {score:.3f}")
        names.append(label)
        scores.append(score)

    features = encoded.drop(columns=[TARGET])
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, y)
    importances = sorted(zip(features.columns, model.feature_importances_),
                         key=lambda pair: pair[1])

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))

    axes[0].barh([name for name, _ in importances],
                 [score for _, score in importances], color="tab:blue")
    axes[0].set(xlabel="importance", title="what the model leaned on")

    axes[1].barh(names[::-1], scores[::-1], color="tab:purple")
    axes[1].axvline(scores[0], color="black", linestyle="--", linewidth=1)
    axes[1].set(xlabel="cross-validated accuracy", xlim=(0, 1.05),
                title="dropping island changes nothing")

    fig.suptitle("Step 4: it is reading anatomy, not geography")
    plt.tight_layout()
    plt.show()


def main():
    df = load_clean()

    step_1_raw_and_cleaning(df)
    step_2_features(df)
    step_3_decision_boundary(df)
    step_4_is_it_cheating(df)

    print("done")


if __name__ == "__main__":
    main()
