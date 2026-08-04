"""Type in a passenger and see whether the model thinks they survived.

    uv run predict.py
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from titanic_demo import TARGET, encode, load_clean


def ask_number(question, low, high):
    while True:
        answer = input(question)
        try:
            value = float(answer)
        except ValueError:
            print(f"  needs to be a number between {low} and {high}")
            continue
        if low <= value <= high:
            return value
        print(f"  needs to be between {low} and {high}")


def ask_choice(question, choices):
    while True:
        answer = input(question).strip().lower()
        if answer in choices:
            return answer
        print(f"  pick one of: {', '.join(choices)}")


def main():
    numbers = encode(load_clean())
    X = numbers.drop(columns=[TARGET])
    y = numbers[TARGET]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    print(f"model trained on {len(X)} real passengers\n")

    while True:
        print("-" * 46)
        pclass = ask_number("ticket class, 1 2 or 3      : ", 1, 3)
        sex = ask_choice("male or female              : ", ["male", "female"])
        age = ask_number("age                         : ", 0, 100)
        fare = ask_number("fare paid, 0 to 512         : ", 0, 512)
        siblings = ask_number("siblings or spouse aboard   : ", 0, 10)
        parents = ask_number("parents or children aboard  : ", 0, 10)

        passenger = pd.DataFrame([{
            "Pclass": pclass,
            "Sex": 1 if sex == "male" else 0,
            "Age": age,
            "SibSp": siblings,
            "Parch": parents,
            "Fare": fare,
            "Embarked_C": False,
            "Embarked_Q": False,
            "Embarked_S": True,
        }])[X.columns]

        chance = model.predict_proba(passenger)[0][1]

        print()
        print(f"  chance of surviving: {chance:.0%}")
        print(f"  the model says     : {'survived' if chance >= 0.5 else 'did not survive'}")
        print()

        if input("another one? y/n: ").strip().lower() != "y":
            break


if __name__ == "__main__":
    main()
