import mysql.connector as database
from params.sql import *

def Get_EmployeeData(card_id, actual_date):
    try:
        conn = database.connect(
            user=sql_user,
            password=sql_password,
            host=sql_host,
            database=sql_database
        )
        employee_dict = {}
        get_sql = conn.cursor()
        
        #Get basic data about employee
        get_sql.execute("SELECT id, imie, nazwisko FROM pracownicy WHERE karta = '%s'" % card_id)
        result = get_sql.fetchall()[0]
        employee_dict['id'] = result[0]
        employee_dict['fname'] = result[1]
        employee_dict['lname'] = result[2]
        
        #Get employee computer
        get_sql.execute("SELECT devices.mac, DHCP.ip FROM pracownicy LEFT JOIN DHCP ON DHCP.pracownik = pracownicy.id LEFT JOIN devices ON DHCP.komputer = devices.id WHERE pracownicy.karta = '" + card_id + "'")
        employee_dict['mac'] = get_sql.fetchall()[0][0]
        
        #Get employee entries
        sql_query = "SELECT action FROM obecnosc WHERE pracownik = %s AND time LIKE '%s%%' ORDER BY time" % (employee_dict['id'], actual_date)
        get_sql.execute(sql_query)
        employee_dict['entry_list'] = []
        try:
            entry_list = get_sql.fetchall()
        except:
            entry_list = []
        for item in entry_list:
            employee_dict['entry_list'].append(item[0])
            
        # Sprawdź, czy pracownik wykorzystał już przerwę obiadową dzisiaj
        lunch_query = "SELECT COUNT(*) FROM obecnosc WHERE pracownik = %s AND action = 28 AND time LIKE '%s%%'" % (employee_dict['id'], actual_date)
        get_sql.execute(lunch_query)
        lunch_count = get_sql.fetchone()[0]
        employee_dict['lunch_used'] = lunch_count > 0
        
        # Sprawdź, czy pracownik jest obecnie na przerwie
        is_on_break_query = """
        SELECT 
            SUM(CASE WHEN action = 3 THEN 1 ELSE 0 END) - 
            SUM(CASE WHEN action = 4 THEN 1 ELSE 0 END) as break_balance,
            SUM(CASE WHEN action = 28 THEN 1 ELSE 0 END) - 
            SUM(CASE WHEN action = 29 THEN 1 ELSE 0 END) as lunch_balance
        FROM obecnosc 
        WHERE pracownik = %s 
        AND time LIKE '%s%%'
        """ % (employee_dict['id'], actual_date)
        
        get_sql.execute(is_on_break_query)
        break_balance = get_sql.fetchone()
        
        employee_dict['is_on_break'] = break_balance[0] > 0 if break_balance[0] is not None else False
        employee_dict['is_on_lunch'] = break_balance[1] > 0 if break_balance[1] is not None else False

        conn.close()
        return employee_dict
        
    except database.Error as e:
        print(f"Nie udalo sie polaczyc z baza danych MariaDB: {e}")
        sys.exit(1)
        
def Get_Actual_Breaks():
    try:
        conn = database.connect(
            user=sql_user,
            password=sql_password,
            host=sql_host,
            database=sql_database
        )
        get_sql = conn.cursor()
        
        breaks_dict = {}
        lunch_dict = {}
        
        #Get all employees on breaks
        get_sql.execute("SELECT id_emp, type FROM act_breaks")
        result = get_sql.fetchall()
        
        for item in result:
            get_sql.execute("SELECT imie, nazwisko FROM pracownicy WHERE id = %s" % item[0])
            fname_lname = get_sql.fetchall()
            fname = fname_lname[0][0]
            lname = fname_lname[0][1]
            i = len(lname)
            lname = lname[:1]
            j = 1
            while j < i:
                lname += "*"
                j+=1
            employee = fname + " " + lname
            
            # Dodaj pracownika do odpowiedniego słownika w zależności od typu przerwy
            if item[1] == 2:  # Przerwa obiadowa
                lunch_dict[item[0]] = employee
            else:  # Zwykła przerwa (typ 1 lub brak typu)
                breaks_dict[item[0]] = employee
        
        conn.close()
        return breaks_dict, lunch_dict
        
    except database.Error as e:
        print(f"Nie udalo sie polaczyc z baza danych MariaDB: {e}")
        sys.exit(1)
        
def Update_EmployeeData(emp_id, action, actual_time, emp_name):
    try:
        conn = database.connect(
            user=sql_user,
            password=sql_password,
            host=sql_host,
            database=sql_database
        )
        get_sql = conn.cursor()
        get_sql.execute("INSERT INTO obecnosc (pracownik, action) VALUES (%s, %s)", (emp_id, action))
        conn.commit()
        
        if action == 1:
            action_text = "WEJŚCIE "
        elif action == 2:
            action_text = "WYJŚCIE "
        elif action == 3:
            action_text = "PRZERWA "
            sql_check = "SELECT id FROM act_breaks WHERE id_emp = %s" % emp_id
            get_sql.execute(sql_check)
            result = get_sql.fetchall()
            if not result:
                get_sql.execute("INSERT INTO act_breaks (id_emp, type) VALUES (%s, 1)" % emp_id)
                conn.commit()
                print(f"Dodano pracownika {emp_id} do zwykłej przerwy (type=1)")
        elif action == 4:
            action_text = "KONIEC PRZERWY "
            sql_check = "SELECT id FROM act_breaks WHERE id_emp = %s AND type = 1" % emp_id
            get_sql.execute(sql_check)
            result = get_sql.fetchall()
            if result:
                get_sql.execute("DELETE FROM act_breaks WHERE id_emp = %s AND type = 1" % emp_id)
                conn.commit()
                print(f"Usunięto pracownika {emp_id} ze zwykłej przerwy")
        elif action == 28:
            action_text = "PRZERWA OBIADOWA "
            sql_check = "SELECT id FROM act_breaks WHERE id_emp = %s" % emp_id
            get_sql.execute(sql_check)
            result = get_sql.fetchall()
            if not result:
                get_sql.execute("INSERT INTO act_breaks (id_emp, type) VALUES (%s, 2)" % emp_id)
                conn.commit()
        elif action == 29:
            action_text = "KONIEC PRZERWY OBIADOWEJ "
            sql_check = "SELECT id FROM act_breaks WHERE id_emp = %s AND type = 2" % emp_id
            get_sql.execute(sql_check)
            result = get_sql.fetchall()
            if result:
                get_sql.execute("DELETE FROM act_breaks WHERE id_emp = %s AND type = 2" % emp_id)
                conn.commit()
        else:
            action_text = ""
        
        sql_check = "SELECT id FROM obecnosc WHERE action = " + str(action) + " AND pracownik = " + str(emp_id) + " AND time LIKE '" + actual_time + "%'"
        get_sql.execute(sql_check)
        result = get_sql.fetchall()
        if not result:
            text1 = "ERROR - Coś poszło nie tak"
            text2 = "Spróbuj jeszcze raz %s" % emp_name
            conn.close()
            return text1, text2, (165, 42, 42)
        else:
            text1 = "%s - SUKCES!" % action_text
            text2 = "Dobrego dnia %s" % emp_name
            conn.close()
            return text1, text2, (0, 158, 96)
        conn.close()
        
    except database.Error as e:
        print(f"Nie udalo sie polaczyc z baza danych MariaDB: {e}")
        text1 = "ERROR - Błąd bazy danych"
        text2 = "Skontaktuj się z administratorem"
        return text1, text2, (165, 42, 42)