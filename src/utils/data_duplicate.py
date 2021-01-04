# import csv
import datetime
import pandas as pd
import os


def main():
    input_filename = "data/No13(80spm).CSV"
    output_filename = "data/No13_3000.csv"

    if os.path.exists(output_filename):
        os.remove(output_filename)

    dtype = {
        "(2)HA-V01": float,
        "(2)HA-V02": float,
        "(2)HA-V03": float,
        "(2)HA-V04": float,
        "(2)HA-C01": float,
        "(2)HA-C02": float,
    }
    # dtype = {
    #     "(2)HA-V01": "str",
    #     "(2)HA-V02": "str",
    #     "(2)HA-V03": "str",
    #     "(2)HA-V04": "str",
    #     "(2)HA-C01": "str",
    #     "(2)HA-C02": "str",
    # }

    df = pd.read_csv(input_filename, dtype=dtype)
    df.drop("#EndHeader", axis=1, inplace=True)
    df.drop("日時(μs)", axis=1, inplace=True)
    df.drop("(2)HA-C02", axis=1, inplace=True)

    # df["(2)HA-V01"] = df["(2)HA-V01"].apply(lambda x: round(x, 3))
    # df["(2)HA-V02"] = df["(2)HA-V01"].apply(lambda x: round(x, 3))
    # df["(2)HA-V03"] = df["(2)HA-V01"].apply(lambda x: round(x, 3))
    # df["(2)HA-V04"] = df["(2)HA-V01"].apply(lambda x: round(x, 3))
    # df["(2)HA-C01"] = df["(2)HA-V01"].apply(lambda x: round(x, 3))

    df = df.reindex(columns=["(2)HA-C01", "(2)HA-V01", "(2)HA-V02", "(2)HA-V03", "(2)HA-V04"])

    for i in range(429):
        print(i, datetime.datetime.now())

        df.to_csv(
            output_filename, mode="a", encoding="utf-8", header=False, index=False,
        )


if __name__ == "__main__":
    main()
