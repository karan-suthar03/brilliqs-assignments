"""Train a model to predict the species of a penguin from its measurements."""

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from prepare_data import TARGET, encode, load_clean


def main():
    df = encode(load_clean())

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    # stratify keeps the same species mix in both halves, which matters
    # because Chinstrap is much smaller than the other two
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"training on {len(X_train)} penguins, testing on {len(X_test)}")
    print(f"features: {list(X.columns)}")
    print()

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(f"accuracy: {accuracy_score(y_test, predictions):.3f}")
    print()
    print(classification_report(y_test, predictions))

    print("confusion matrix (rows = actual, columns = predicted):")
    labels = sorted(y.unique())
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    print(f"{'':<12}" + "".join(f"{label:<12}" for label in labels))
    for label, row in zip(labels, matrix):
        print(f"{label:<12}" + "".join(f"{value:<12}" for value in row))

    importances = sorted(zip(X.columns, model.feature_importances_),
                         key=lambda pair: pair[1], reverse=True)
    print()
    print("what the model actually used:")
    for name, score in importances:
        print(f"  {name:<22} {score:.3f}")

    names = [name for name, _ in importances]
    scores = [score for _, score in importances]

    plt.figure(figsize=(9, 5))
    plt.barh(names[::-1], scores[::-1], color="tab:blue")
    plt.title("Which measurements the model relied on")
    plt.xlabel("importance")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
