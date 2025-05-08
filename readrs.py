from datetime import datetime
import sys
from lib.init_envs import *
from lib.drawing import Draw_Text, Draw_Img
from lib.wake_pc import wake_computer_api
from sql.functions import Get_EmployeeData, Update_EmployeeData, Get_Actual_Breaks
from params.serial import ser
from lib.checkentry import Check_Entry

try:
    krzychu = sys.argv[1]
    krzychu_jest = krzychu
except:
    krzychu_jest = False

def Draw_MainScreen(db_counter, breaks_dict, lunch_dict):
    screen.fill((42, 42, 42))
    Draw_Text(datetime.now().strftime("%H:%M:%S"), screen, main_font, x // 2, y * 6/8)
    Draw_Text("Przyłóż kartę do czytnika", screen, main_font, x // 2, y * 5/8)
    Draw_Img(img_logo, screen, x //2, y * 3/10)
    if krzychu_jest == "krzychu":
        Draw_Img(img_krzychu_dir[img_rotation], screen, x * 17/20, y * 17/20)
    
    if db_counter == 0:
        breaks_dict, lunch_dict = Get_Actual_Breaks()
    
    # Rysuj pracowników na zwykłej przerwie po prawej stronie
    y_offset = 20
    for key, item in breaks_dict.items():
        y_offset += 22
        Draw_Text(item, screen, list_font, x-100, y-y_offset, color=(255, 178, 102))
    if len(breaks_dict) > 0:
        y_offset += 25
        Draw_Text("Na przerwie:", screen, list_font, x-100, y-y_offset)
    
    # Rysuj pracowników na przerwie obiadowej po lewej stronie
    y_offset = 20
    for key, item in lunch_dict.items():
        y_offset += 22
        Draw_Text(item, screen, list_font, 100, y-y_offset, color=(255, 51, 153))
    if len(lunch_dict) > 0:
        y_offset += 25
        Draw_Text("Na obiedzie:", screen, list_font, 100, y-y_offset)
    
    return breaks_dict, lunch_dict
            
        
def Draw_ChoiceScreen(name, employee_data):
    screen.fill((42, 42, 42))
    Draw_Text("Witaj", screen, name_font, x // 2, y * 2/20)
    Draw_Text(name, screen, name_font, x // 2, y * 3/20)
    
    # Sprawdź dostępne akcje na podstawie stanu pracownika w bazie danych
    available_actions = []
    
    # Wszystkie informacje o stanie pracownika są już pobrane z bazy danych
    # w funkcji Get_EmployeeData i przechowywane w słowniku employee_data
    
    if not employee_data['entry_list']:
        # Jeśli nie ma żadnych wpisów, to dostępne tylko wejście
        available_actions = [1]
    elif len(employee_data['entry_list']) > 0 and employee_data['entry_list'][-1] == 2:
        # Jeśli ostatnia akcja to wyjście - brak dostępnych akcji
        available_actions = []
    else:
        # Pracownik jest w pracy
        if employee_data['is_on_break']:
            # Jeśli jest na zwykłej przerwie, może ją tylko zakończyć
            available_actions = [4]
        elif employee_data['is_on_lunch']:
            # Jeśli jest na przerwie obiadowej, może ją tylko zakończyć
            available_actions = [29]
        else:
            # Jeśli nie jest na żadnej przerwie, może wyjść lub iść na przerwę
            available_actions = [2, 3]
            # Dodaj przerwę obiadową tylko jeśli nie została jeszcze wykorzystana
            if not employee_data['lunch_used']:
                available_actions.append(28)
    
    # Jeśli nie ma dostępnych akcji, pokaż komunikat i wróć
    if not available_actions:
        Draw_Text("Zakończono pracę", screen, button_font, x // 2, y * 10/20, color=(165, 42, 42))
        Draw_Text("Brak dostępnych opcji", screen, button_font, x // 2, y * 12/20, color=(165, 42, 42))
        Draw_Text("Jeśli to błąd, skontaktuj się z przełożonym", screen, list_font, x // 2, y * 14/20, color=(255, 255, 255))
        
        if screen_timeout < 290:
            Draw_Text(str(int(screen_timeout/60)), screen, main_font, x/4, y/9, color=(20,20,20))
            Draw_Img(img_wheel_dir[img_rotation], screen, x/4, y/9)
            Draw_Text(str(int(screen_timeout/60)), screen, main_font, x*3/4, y/9, color=(20,20,20))
            Draw_Img(img_wheel_dir[img_rotation_2], screen, x*3/4, y/9)
        
        # Automatyczny powrót po 3 sekundach
        if screen_timeout <= 0:
            return 5
        else:
            return 5
    
    # Rysuj dostępne przyciski
    buttons = []
    text_color = (20, 20, 20)
    
    # Definicje obszarów przycisków
    button_areas = {
        1: pygame.Rect(5, y * 5/20, x/2-10, y * 13/40),  # Wejście
        2: pygame.Rect(x/2+5, y * 5/20, x/2-10, y * 13/40),  # Wyjście
        3: pygame.Rect(5, y * 12/20+5, x/2-10, y * 13/40),  # Przerwa
        4: pygame.Rect(x/2+5, y * 12/20+5, x/2-10, y * 13/40),  # Po przerwie
        28: pygame.Rect(5, y * 5/20, x-10, y * 13/40),  # Przerwa obiadowa
        29: pygame.Rect(5, y * 12/20+5, x-10, y * 13/40)  # Koniec przerwy obiadowej
    }
    
    button_colors = {
        1: (0, 158, 96),    # zielony
        2: (165, 42, 42),   # czerwony
        3: (119, 136, 153), # szary
        4: (47, 79, 79),    # ciemny turkusowy
        28: (255, 165, 0),  # pomarańczowy
        29: (70, 130, 180)  # niebieski
    }
    
    button_labels = {
        1: "Wejście",
        2: "Wyjście",
        3: "Przerwa",
        4: "Koniec przerwy",
        28: "Przerwa obiadowa",
        29: "Koniec przerwy obiadowej"
    }
    
    # Dostosowanie pozycji i rozmiaru przycisków w zależności od liczby dostępnych akcji
    if len(available_actions) == 1:
        # Tylko jeden przycisk na środku
        button_areas[available_actions[0]] = pygame.Rect(5, y * 8/20, x-10, y * 13/40)
    elif len(available_actions) == 2:
        # Dwa przyciski obok siebie
        button_areas[available_actions[0]] = pygame.Rect(x/2+5, y * 8/20, x/2-10, y * 13/40)
        button_areas[available_actions[1]] = pygame.Rect(5, y * 8/20, x/2-10, y * 13/40)
    elif len(available_actions) == 3:
        # Trzy przyciski - dwa na górze, jeden na dole
        button_areas[available_actions[0]] = pygame.Rect(x/2+5, y * 5/20, x/2-10, y * 13/40)
        button_areas[available_actions[1]] = pygame.Rect(5, y * 5/20, x/2-10, y * 13/40)
        button_areas[available_actions[2]] = pygame.Rect(5, y * 12/20+5, x-10, y * 13/40)
    
    # Rysuj przyciski
    for action_id in available_actions:
        area = button_areas[action_id]
        color = button_colors[action_id]
        label = button_labels[action_id]
        
        button = pygame.draw.rect(screen, color, area, border_radius=30)
        Draw_Text(label, screen, button_font, area.center[0], area.center[1], color=text_color)
        buttons.append((button, action_id))
    
    # Wyświetl licznik czasu
    if screen_timeout < 290:
        Draw_Text(str(int(screen_timeout/60)), screen, main_font, x/4, y/9, color=(20,20,20))
        Draw_Img(img_wheel_dir[img_rotation], screen, x/4, y/9)
        Draw_Text(str(int(screen_timeout/60)), screen, main_font, x*3/4, y/9, color=(20,20,20))
        Draw_Img(img_wheel_dir[img_rotation_2], screen, x*3/4, y/9)
    
    # Obsługa kliknięć
    action = 5  # Domyślna akcja (brak)
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
        if event.type == pygame.FINGERDOWN:
            fingerx = event.x * screen.get_width()
            fingery = event.y * screen.get_height()
            event.pos = fingerx, fingery
        print(event.pos)
        
        for button, action_id in buttons:
            if button.collidepoint(event.pos):
                print(button_labels[action_id])
                action = action_id
                break
    
    return action
            
def Draw_SuccessErrorScreen(text1, text2, text_color):
    screen.fill((42, 42, 42))
    if screen_timeout < 180:
        Draw_Text(text1, screen, main_font, x/2, y*5/8, color=text_color)
        Draw_Text(text2, screen, main_font, x/2, y*6/8, color=text_color)
        Draw_Img(img_icon, screen, x/2, y*5/16)
        Draw_Img(img_wheel2_dir[img_rotation], screen, x/2, y*5/16)

#try:
#    ssh = SSH_Connect()
#except Exception as e:
#    print("Inicjalizacja SSH - błąd:\n%s" % e)
    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    if ser.inWaiting() > 3:
        card_id=str(ser.readline())[2:12]
        screen_state = 1
        screen_timeout = 290 #TEST
        
    if screen_state == 0:
        if 'lunch_dict' not in locals():
            lunch_dict = {}
        breaks_dict, lunch_dict = Draw_MainScreen(db_counter, breaks_dict, lunch_dict)
        db_counter+=1
        if db_counter >= 600:
            db_counter = 0
            
    elif screen_state == 1:
        if data_crawled == False:
            try:
                employee_data = Get_EmployeeData(card_id, datetime.today().strftime('%Y-%m-%d'))
                data_crawled = True
            except Exception as e:
                # Karta nie została znaleziona lub wystąpił inny błąd
                print(f"Błąd przy odczycie karty {card_id}: {e}")
                text1 = "Karta nie rozpoznana"
                text2 = "Skontaktuj się z przełożonym"
                text_color = (165, 42, 42)  # czerwony
                
                screen_timeout = 180
                screen_state = 2
                data_crawled = False
                continue
        # Automatyczne wejście jeśli to jedyna opcja
        if not employee_data['entry_list']:
            action = 1
            # Budzenie komputera
            try:
                wake_computer_api(employee_data['mac'])
                if card_id == "0004293363" or card_id == "0003472198" or card_id == "0004334804":
                    wake_computer_api("88:51:FB:67:91:55")
                    wake_computer_api("20:47:47:B5:00:C3")
                if card_id == "0004365562" or card_id == "0002002502" or card_id == "0004388356" or card_id == "0004427606" or card_id == "0004336582" or card_id == "0004176737" or card_id == "0002001285" or card_id == "0004328792" or card_id == "0004405307":
                    wake_computer_api("44:37:E6:6A:49:96")
                    wake_computer_api("44:37:E6:AE:69:4D")
                    wake_computer_api("44:37:E6:A3:8C:D9")
                    wake_computer_api("B8:27:EB:A2:31:4F")
            except Exception as e:
                print(e)
                try:
                    ssh = SSH_Connect()
                    if card_id != "0016323429":
                        WakeComputer(card_id, employee_data['mac'], ssh)
                except Exception as e:
                    print("Podtrzymanie SSH - błąd:\n%s" % e)
            
            # Sprawdzenie poprawności akcji i aktualizacja danych
            action_result = Check_Entry(action, employee_data)
            
            if action_result == "OK":
                # Aktualizacja danych pracownika
                entry_result = Update_EmployeeData(employee_data['id'], action, datetime.today().strftime('%Y-%m-%d'), employee_data['fname'])
                text1 = entry_result[0]
                text2 = entry_result[1]
                text_color = entry_result[2]
            else:
                text1 = action_result[0]
                text2 = action_result[1]
                text_color = (165, 42, 42)
            
            # Przejście do ekranu potwierdzenia
            screen_timeout = 180
            screen_state = 2
            data_crawled = False
        else:
            # Istniejąca logika dla innych przypadków
            screen_timeout-=1
            if screen_timeout <= 0:
                screen_timeout = 290
                db_counter = 0
                screen_state = 0
                data_crawled = False
            
            # Przekazanie danych pracownika do funkcji Draw_ChoiceScreen
            action = Draw_ChoiceScreen(employee_data['fname'] + " " + employee_data['lname'], employee_data)
            
            if action != 5:
                # Budzenie komputera jeśli akcja to wejście (1)
                if action == 1:
                    try:
                        wake_computer_api(employee_data['mac'])
                        if card_id == "0004293363" or card_id == "0003472198" or card_id == "0004334804":
                            wake_computer_api("88:51:FB:67:91:55")
                            wake_computer_api("20:47:47:B5:00:C3")
                        if card_id == "0004365562" or card_id == "0002002502" or card_id == "0004388356" or card_id == "0004427606" or card_id == "0004336582" or card_id == "0004176737" or card_id == "0002001285" or card_id == "0004328792" or card_id == "0004405307":
                            wake_computer_api("44:37:E6:6A:49:96")
                            wake_computer_api("44:37:E6:AE:69:4D")
                            wake_computer_api("44:37:E6:A3:8C:D9")
                            wake_computer_api("B8:27:EB:A2:31:4F")
                    except Exception as e:
                        print(e)
                        try:
                            ssh = SSH_Connect()
                            if card_id != "0016323429":
                                WakeComputer(card_id, employee_data['mac'], ssh)
                        except Exception as e:
                            print("Podtrzymanie SSH - błąd:\n%s" % e)
                            
                screen_timeout = 0
                screen_state = 2
                data_crawled = False
                
                # Sprawdzenie poprawności akcji wykorzystując nową funkcję z pełnymi danymi
                action_result = Check_Entry(action, employee_data)
                
                if action_result == "OK":
                    # Aktualizacja danych pracownika
                    entry_result = Update_EmployeeData(employee_data['id'], action, datetime.today().strftime('%Y-%m-%d'), employee_data['fname'])
                    text1 = entry_result[0]
                    text2 = entry_result[1]
                    text_color = entry_result[2]
                else:
                    text1 = action_result[0]
                    text2 = action_result[1]
                    text_color = (165, 42, 42)
                
                # W przypadku wyjścia ustaw krótszy czas powrotu do ekranu głównego
                if action == 2:
                    screen_timeout = 120
                else:
                    screen_timeout = 180
                
    elif screen_state == 2:
        screen_timeout-=1
        if screen_timeout <= 0:
            screen_timeout = 290
            db_counter = 0
            screen_state = 0
        Draw_SuccessErrorScreen(text1, text2, text_color)
    
    pygame.display.flip()
    clock.tick(60)
    
    if img_rotation < 360:
        img_rotation += 1
    else:
        img_rotation = 0
        
    if img_rotation_2 > 0:
        img_rotation_2 -= 1
    else:
        img_rotation_2 = 360