"""Predicting who survived the Titanic.

A second dataset alongside the penguins, following the same three steps:
clean it, look for correlations, train a model.

Close each window to move on to the next step.
"""

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, train_test_split

INPUT_FILE = "titanic.csv"
TARGET = "Survived"


def load_clean():
    df = pd.read_csv(INPUT_FILE)

    # Cabin is missing for 687 of 891 passengers, so there is nothing to
    # rescue. Name and Ticket are labels, not facts about the passenger.
    df = df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin"])

    # Age is missing for 177. The median keeps the distribution roughly
    # intact, which the mean would not if a few very old passengers pulled it.
    df["Age"] = df["Age"].fillna(df["Age"].median())

    # only two rows, so the most common port is a safe guess
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    return df


def encode(df):
    df = df.copy()
    df["Sex"] = (df["Sex"] == "male").astype(int)
    df = pd.get_dummies(df, columns=["Embarked"], prefix="Embarked")
    return df


def step_1_cleaning(df):
    raw = pd.read_csv(INPUT_FILE)

    print("STEP 1 - cleaning")
    print(raw.isna().sum()[raw.isna().sum() > 0].to_string())
    print()
    print(f"  dropped Cabin, missing for {raw['Cabin'].isna().sum()} of {len(raw)}")
    print(f"  filled {raw['Age'].isna().sum()} ages with the median, {df['Age'].median():.0f}")
    print(f"  filled {raw['Embarked'].isna().sum()} ports with '{raw['Embarked'].mode()[0]}'")
    print(f"  {df.isna().sum().sum()} missing values left")
    print()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    missing = raw.isna().sum()
    axes[0].bar(missing.index, missing.values, color="tomato")
    axes[0].set(ylabel="rows missing", title="before cleaning")
    axes[0].tick_params(axis="x", rotation=45)

    axes[1].hist([raw["Age"].dropna(), df["Age"]], bins=30,
                 label=["original", "after filling"], color=["tomato", "seagreen"])
    axes[1].set(xlabel="age", ylabel="passengers", title="filling 177 ages with the median")
    axes[1].legend()

    fig.suptitle("Step 1: what was missing, and what filling it did")
    plt.tight_layout()
    plt.show()


def step_2_correlations(df):
    numbers = encode(df)
    corr = numbers.corr()

    print("STEP 2 - what correlates with surviving")
    print(corr[TARGET].drop(TARGET).sort_values().to_string())
    print()

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))

    survival = corr[TARGET].drop(TARGET).sort_values()
    axes[0].barh(survival.index, survival.values,
                 color=["tomato" if v < 0 else "seagreen" for v in survival.values])
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set(xlabel="correlation with survival", title="what mattered")

    axes[1].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    axes[1].set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right", fontsize=8)
    axes[1].set_yticks(range(len(corr)), corr.columns, fontsize=8)
    axes[1].set_title("every pair")
    for i in range(len(corr)):
        for j in range(len(corr)):
            axes[1].text(j, i, f"{corr.iloc[i, j]:.1f}", ha="center", va="center", fontsize=6)

    fig.suptitle("Step 2: being male is the strongest signal, and it is negative")
    plt.tight_layout()
    plt.show()


def step_3_model(df):
    numbers = encode(df)
    X = numbers.drop(columns=[TARGET])
    y = numbers[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    cross_validated = cross_val_score(model, X, y, cv=5).mean()

    print("STEP 3 - the model")
    print(f"  trained on {len(X_train)}, tested on {len(X_test)}")
    print(f"  accuracy on the test set : {accuracy:.3f}")
    print(f"  cross validated          : {cross_validated:.3f}")
    print(f"  guessing 'nobody survived': {1 - y.mean():.3f}")
    print()

    importances = sorted(zip(X.columns, model.feature_importances_),
                         key=lambda pair: pair[1])
    for name, score in reversed(importances):
        print(f"  {name:<14} {score:.3f}")
    print()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    axes[0].barh([name for name, _ in importances],
                 [score for _, score in importances], color="tab:blue")
    axes[0].set(xlabel="importance", title="what the model used")

    axes[1].bar(["always guess\n'died'", "the model"], [1 - y.mean(), cross_validated],
                color=["grey", "seagreen"])
    axes[1].set(ylabel="accuracy", ylim=(0, 1), title="is it better than guessing?")

    fig.suptitle(f"Step 3: {cross_validated:.1%} accurate, against {1 - y.mean():.1%} for guessing")
    plt.tight_layout()
    plt.show()


def main():
    df = load_clean()

    step_1_cleaning(df)
    step_2_correlations(df)
    step_3_model(df)

    print("done")


if __name__ == "__main__":
    main()
