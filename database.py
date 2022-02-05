import sqlite3


class SQLighter:
    def __init__(self, database):
        """Подключние к БД и сохранение курсора соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

        with self.connection:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS sofas ("
                "id integer PRIMARY KEY, "
                "name integer NOT NULL, "
                "price text NOT NULL, "
                "image blob NOT NULL);"
            )

    def new_sofa(self, name, price, image):
        """Создание дивана в БД"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `sofas` (`name`, `price`, `image`) VALUES(?,?,?)", (name, price, image))

    def get_sofa(self, id_sofa):
        """Диван по ID"""
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM `sub` WHERE `status` = ?", (id_sofa,)).fetchone()

    def all_sofa(self):
        """Получение списка диванов"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `sofas`").fetchall()

    def count_sofa(self):
        """Количество диванов в базе данных"""
        with self.connection:
            return self.cursor.execute("SELECT Count(*) FROM `sofas`")