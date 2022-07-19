def diff(df, field):
    return df[field].diff() / df["sequential_number"].diff()


def add(df, field_1, field_2):
    return df[field_1] + df[field_2]
