# Czytnik RFID - Aplikacja kliencka

Aplikacja kliencka do obsługi czytnika RFID w systemie RCP. Umożliwia pracownikom odbijanie kart przy wejściu i wyjściu, z zapisem danych do głównego systemu RCP.

## Funkcjonalności

- Skanowanie kart RFID pracowników
- Obsługa zdarzeń wejścia/wyjścia
- Przesyłanie danych do głównego systemu RCP
- Podstawowa weryfikacja poprawności odbicia

## Użycie

Aby uruchomić aplikację, należy wykorzystać skrypt startowy:

```
startrcp.bat
```

## Struktura projektu

```
│
├── img/                  # Folder z grafikami (ignorowany w repo)
│
├── lib/                  # Biblioteki aplikacji
│   ├── __pycache__/
│   ├── checkentry.py     # Weryfikacja odbić
│   ├── drawing.py        # Interfejs graficzny
│   ├── init_envs.py      # Inicjalizacja zmiennych środowiskowych
│   ├── wake_pc.py        # Wybudzanie komputera
│   └── wake_pc.py.bak
│
├── params/               # Parametry konfiguracyjne
│   ├── __pycache__/
│   ├── serial.cpython-*.pyc  # Skompilowane pliki konfiguracji
│   ├── sql.cpython-*.pyc     # Skompilowane pliki SQL
│   ├── serial.py         # Konfiguracja portu szeregowego
│   ├── serial.py.bak
│   ├── sql.py            # Konfiguracja SQL (ignorowana w repo)
│   └── sql.py.bak
│
├── sql/                  # Funkcje bazy danych
│   ├── __pycache__/
│   ├── functions.py      # Funkcje SQL
│   └── functions.py.bak
│
├── .gitignore
├── RCP_Reworked.pyproj   # Plik projektu
├── readrs.py             # Obsługa czytnika
├── startrcp.bat          # Skrypt startowy
└── time_sync.bat         # Skrypt synchronizacji czasu
```

## Autor

PDA Serwis