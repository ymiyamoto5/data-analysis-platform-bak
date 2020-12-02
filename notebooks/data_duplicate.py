import csv
import datetime


def main():
    with open('No11_3000.csv', "w", encoding="utf-8") as wf:
        writer = csv.writer(wf)
        writer.writerow(
            ["#EndHeader", "日時(μs)", "time(μs）", "(3)HA-V01", "(3)HA-V02", "(3)HA-V03", "(3)HA-V04", "(3)HA-C01"])

    for i in range(0, 3000):
        print(i, datetime.datetime.now())
        with open('No11(25~30spm)-1shot.CSV', "r", encoding="utf-8") as rf:
            reader = csv.reader(rf)
            _ = next(reader)

            with open('No11_3000.csv', "a", encoding="utf-8") as wf:
                writer = csv.writer(wf)

                for row in reader:
                    writer.writerow(row)


if __name__ == '__main__':
    main()
