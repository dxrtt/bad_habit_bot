import sqlite3


class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # Добавляем привычку в БД
    def add_habit(self, user_id, habitname, date):
        with self.connection:
            return self.cursor.execute("INSERT INTO `user_habits` (`user_id`, `habit`, `date`, `sriv`) VALUES(?,?,?,?)",
                                       (user_id, habitname, date, date))

    # Запрос для получения всех привычек пользователя
    def watch_habit(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `habit` FROM `user_habits` WHERE `user_id` = ?", (user_id,)).fetchall()

    # Запрос для регистрации срыва в БД
    def update_habit_date(self, habit_id, date, reason):
        with self.connection:
            return self.cursor.execute("UPDATE `user_habits` SET `sriv` = ?,`sriv_rsn` = ?, `sriv_cnt` = sriv_cnt + 1, "
                                       "`one_day_not` = 0 WHERE `id` = ?",
                                       (date, reason, habit_id)).fetchall()

    # Запрос для удаления привычки из БД
    def delete_habit(self, habit_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `user_habits` WHERE `id` = ?", (habit_id,)).fetchall()

    # Запрос для получения информации о привычке из БД
    def habit_info(self, user_id, habit_name):
        with self.connection:
            return self.cursor.execute(
                "SELECT `habit`, `date`,`id`, `sriv`, `sriv_rsn`, `sriv_cnt` FROM `user_habits` "
                "WHERE `user_id` = ? AND `habit` = ?",
                (user_id, habit_name)).fetchall()

    # Запрос для получения информации о статусе оповещения пользователей
    def habit_notifications(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT `id`, `user_id`, `habit`, `sriv`, `one_day_not`, `sevn_day_not`, `not_status` FROM "
                "`user_habits`").fetchall()

    # Запрос для получения информации о включенном/выключенном оповещении
    def habit_notifications_getstatus(self, id):
        with self.connection:
            return self.cursor.execute("SELECT `not_status` FROM `user_habits` WHERE `id` = ?", (id,)).fetchall()

    # Запрос для включения/отключения оповещений пользователя
    def habit_notifications_setstatus(self, id, status):
        with self.connection:
            return self.cursor.execute('UPDATE `user_habits` SET `not_status` = {} WHERE `id` = {}'.format(status, id))

    # Запрос для регистрации отправленных оповещений
    def habit_notifications_settrue(self, id, day):
        with self.connection:
            return self.cursor.execute('UPDATE `user_habits` SET `{}` = TRUE WHERE `id` = {}'.format(day, id))

    # Запрос для добавления пользователя в таблицу с достижениями
    def achievements_add_user(self, id):
        with self.connection:
            return self.cursor.execute("INSERT OR IGNORE INTO `user_achievements` (`user_id`) VALUES(?)",
                                       (id,)).fetchall()

    # Запрос для получения информации о достижениях пользователя
    def achievements_user(self, id):
        with self.connection:
            return self.cursor.execute("SELECT `one_day`, `seven_day` FROM `user_achievements` WHERE `user_id` = ?",
                                       (id,)).fetchall()

    # Запрос для регистрации достижения пользователя
    def achievements_settrue(self, id, achieve):
        with self.connection:
            return self.cursor.execute(
                'UPDATE `user_achievements` SET `{}` = TRUE WHERE `user_id` = {}'.format(achieve, id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
