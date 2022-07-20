from sklearn.linear_model import LinearRegression


def diff(df, field):
    """微分"""
    return df[field].diff() / df["sequential_number"].diff()


def add(df, field_1, field_2):
    """加算"""
    return df[field_1] + df[field_2]


def sub(df, field_1, field_2):
    """減算"""
    return df[field_1] - df[field_2]


def mul(df, field, coefficient):
    """係数乗算"""
    return df[field] * coefficient


def shift(df, field, periods):
    """シフト"""
    return df[field].shift(periods)


def calibration(df, field, n):
    """校正"""
    return df[field] - df[field].head(n).mean()


def moving_average(df, field, window):
    """移動平均"""
    return df[field].rolling(window).mean()


def regression_line(df, field_1, field_2):
    """回帰直線"""
    model = LinearRegression()
    return model.fit(df[field_1], df[field_2])


def thinning_out(df, field, value):
    """間引き"""
    return df[field].loc[::value]
