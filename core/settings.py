
import os


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DbSettings:

    MYSQL_URI = os.getenv('MYSQL_URI', 'mysql://root:root@localhost:3306/d_fastapi_app')


class SecuritySettings:

    SECRET_KEY = os.getenv('SECRET_KEY', 'CO4F2GLAqK7UiunTRysPaO4SILGGh73QSImCe15gKDphbSz4eMw8R7JuDkJMhFCG')


class DataSettings:

    DATA_PATH = os.getenv('DATA_PATH', 'data')


if not os.path.exists(DataSettings.DATA_PATH):
    os.makedirs(DataSettings.DATA_PATH)


DATA_SET_PATH = os.path.join(PROJECT_DIR, 'data', 'user_action.csv')
