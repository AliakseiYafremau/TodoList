import psycopg2


def test_database_connection():
    try:
        conn = psycopg2.connect(
            dbname="tod_db",
            user="todo_user",
            password="todo_password",
            host="localhost",
            port="5432",
        )
        print("Коннект :)")
        conn.close()
    except psycopg2.Error as e:
        print(f"Не коннект;( : {e}")


if __name__ == "__main__":
    test_database_connection()
