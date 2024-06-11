import sqlite3



def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def create_student_table(conn, create_table_sql_student):
    try:
        c = conn.cursor()
        c.execute(create_table_sql_student)
    except sqlite3.Error as e:
        print(e)

def insert_textbook(conn, textbook):
    sql = ''' INSERT INTO textbooks(textbookname, author, grade, education_board, subject, pdf_file)
              VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, (textbook[0], textbook[1], textbook[2], textbook[3], textbook[4], sqlite3.Binary(textbook[5])))
    conn.commit()
    return cur.lastrowid

def insert_student(conn, student):
    sql = ''' INSERT INTO student(studentname, grade, education_board, email, phone_no)
              VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, student)
    conn.commit()
    return cur.lastrowid




def main():
    database = "textbooks.db"

    sql_create_textbooks_table = """ CREATE TABLE IF NOT EXISTS textbooks (
                                        textbookname TEXT NOT NULL,
                                        author TEXT,
                                        grade TEXT PRIMARY KEY NOT NULL,
                                        education_board TEXT,
                                        subject TEXT,
                                        pdf_file BLOB
                                    ); """
    
    sql_create_student_table = """ CREATE TABLE IF NOT EXISTS student (
                                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        studentname TEXT NOT NULL,
                                        grade TEXT NOT NULL,
                                        education_board TEXT,
                                        email TEXT NOT NULL,
                                        phone_no TEXT NOT NULL

                                    );"""

    # create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create textbooks table
        create_table(conn, sql_create_textbooks_table)
        create_student_table(conn, sql_create_student_table)
        print("Database and textbooks table created successfully!")
        print("student table created successfully!")

        # textbook = ("Science", "Rupamanjari Ghosh", "10", "State Board", "science", open("C:/Users/Eshwar Prasad/Documents/AIVA Code/textbooks/10th-english-science-1.pdf", "rb").read())
        # insert_textbook(conn, textbook)
        print("Textbook record inserted successfully!")

    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
