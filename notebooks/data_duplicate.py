# import csv
import datetime
import pandas as pd
import os


def main():
    # with open('No13_3000.csv', "w", encoding="utf-8") as wf:
    #     writer = csv.writer(wf)
    #     writer.writerow(
    #         ["#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-V02", "(3)HA-V03", "(3)HA-V04", "(3)HA-C01"])

    # for i in range(0, 429):
    #     print(i, datetime.datetime.now())
    #     with open("No13(80spm).CSV", "r", encoding="utf-8") as rf:
    #         reader = csv.reader(rf)
    #         _ = next(reader)

    #         with open("No13_3000.csv", "a", encoding="utf-8") as wf:
    #             writer = csv.writer(wf)

    #             for row in reader:
    #                 writer.writerow(row)

    input_filename = "notebooks/No13(80spm).CSV"
    output_filename = "notebooks/No13_3000.csv"

    if os.path.exists(output_filename):
        os.remove(output_filename)

    dtype = {
        "(2)HA-V01": "str",
        "(2)HA-V02": "str",
        "(2)HA-V03": "str",
        "(2)HA-V04": "str",
        "(2)HA-C01": "str",
        "(2)HA-C02": "str",
    }

    df = pd.read_csv(input_filename, dtype=dtype)
    df.drop("#EndHeader", axis=1, inplace=True)
    df.drop("日時(μs)", axis=1, inplace=True)
    df.drop("(2)HA-C02", axis=1, inplace=True)

    for i in range(429):
        print(i, datetime.datetime.now())

        df.to_csv(
            output_filename, mode="a", encoding="utf-8", header=False, index=False,
        )


if __name__ == "__main__":
    main()
