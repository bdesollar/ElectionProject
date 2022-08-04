from models import database


def drop_tables():
    database.drop_all()


if __name__ == '__main__':
    drop_tables()
