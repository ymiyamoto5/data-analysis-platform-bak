import csv
import datetime


def main():

    with open('3000wave.csv', "w", encoding="utf-8") as wf:
        writer = csv.writer(wf)
        writer.writerow(
            ["#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-C01"])

    for i in range(0, 200):
        print(i, datetime.datetime.now())
        with open('wave1-15.csv', "r", encoding="utf-8") as rf:
            reader = csv.reader(rf)
            _ = next(reader)

            with open('3000wave.csv', "a", encoding="utf-8") as wf:
                writer = csv.writer(wf)

                for row in reader:
                    writer.writerow(row)


if __name__ == '__main__':
    main()
