# Assignment 4 - Predictive Modelling with Pandas

Cleans the Titanic dataset, looks for correlations, and trains a model to
predict who survived.

## Files

```
titanic.csv       891 passengers, the Kaggle training set
titanic_demo.py   the three steps, as charts
predict.py        type in a passenger and see what the model says
```

## Running

```
uv run titanic_demo.py
uv run predict.py
```

`titanic_demo.py` opens three windows - close each to move on.

## Cleaning

| column | problem | what was done |
|---|---|---|
| `Cabin` | missing for 687 of 891 | dropped - 77% empty, nothing to impute from |
| `Age` | missing for 177 | filled with the median for that class and sex |
| `Embarked` | missing for 2 | filled with the most common port |
| `PassengerId`, `Name`, `Ticket` | unique per passenger | dropped - they identify rather than describe |

Ages are filled per class and sex rather than with one global median, because
one number would stack all 177 passengers onto the same age. A first class
man was typically 40, a third class woman 22.

`Sex` becomes 0/1. `Embarked` becomes three columns, one per port - three
categories cannot be 0, 1 and 2, because that would tell the model there is
an order and that Q is twice as far from S as C is.

## Results

```
always guessing "died"   61.6%
the model                80.9%   cross validated over 5 folds
```

The baseline matters: 549 of the 891 passengers died, so answering "died"
every time is right 61.6% of the time. 81% only means something next to that.

Cross validation rather than a single split, because a single split swings
about seven points depending on which quarter of the data gets held back.

`Sex` is the strongest signal at -0.54 - and negative, because `Sex` is 1 for
male. Being male sharply reduced the chance of surviving.

## The interactive one

`predict.py` asks for a passenger's class, sex, age, fare and family aboard,
and returns the model's odds. It uses `predict_proba` rather than `predict`,
so you get "98%" rather than just "survived" - that is the share of the 100
trees that voted yes.
