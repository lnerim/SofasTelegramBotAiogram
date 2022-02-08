import sqlite3


class BotDB:
    def __init__(self, database):
        """Подключние к БД и сохранение курсора соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

        with self.connection:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS sofas ("
                "id integer PRIMARY KEY, "
                "name text NOT NULL, "
                "price integer NOT NULL, "
                "image blob NOT NULL);"
            )

    def new_sofa(self, name, price, image):
        """Создание дивана в БД"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `sofas` (`name`, `price`, `image`) VALUES(?,?,?)", (name, price, image))

    def get_sofa(self, id_sofa) -> list:
        """Диван по ID"""
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM `sofas` WHERE `id` = ?", (id_sofa,)).fetchone()

    def all_id_sofa(self) -> list:
        """Получение списка id диванов"""
        with self.connection:
            data = self.cursor.execute("SELECT id FROM `sofas`").fetchall()
            return [id_sofa[0] for id_sofa in data]

    def count_sofa(self) -> int:
        """Количество диванов в базе данных"""
        with self.connection:
            return self.cursor.execute("SELECT Count(*) FROM `sofas`").fetchone()[0]

    def delete_sofa(self, id_sofa):
        with self.connection:
            return self.cursor.execute("DELETE FROM `sofas` WHERE `id`= ?", (id_sofa,))


if __name__ == '__main__':
    db = BotDB(":memory:")
