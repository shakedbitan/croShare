# Written by Shaked Bitan
# Machine learning model that uses linear regression
# in order to predict how long a pattern is going to complete

import numpy as np
import pandas as pd
import sys
from sklearn import linear_model
import pickle
import cProfile

CSV_FILE = r"C:\Users\Toshiba\PycharmProjects\tensorEnv\ml-file.csv"


def main():
    try:
        data = pd.read_csv(CSV_FILE)

        data = data[["name", "level", "time"]]
        data = data.iloc[:, 1:]  # remove the first column (the name column)

        predict = "time"

        x = np.array(data.drop(predict, axis=1))
        y = np.array(data[predict])

        linear = linear_model.LinearRegression()

        linear.fit(x, y)

        # with open("saved_ml_model.pickle", "wb") as f:
        #     pickle.dump(linear, f)

        for i in range(1, 11):
            prediction = str(np.round(linear.predict([[i]])))
            print(prediction[1:-2], end=' ')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
