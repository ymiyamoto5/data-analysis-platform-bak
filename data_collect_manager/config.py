class Config(object):
    DEBUG = False
    TESTING = False


class Development(Config):
    DEBUG = True


class Testing(Config):
    TESTING = True


class Production(Config):
    pass
