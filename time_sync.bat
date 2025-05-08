@echo off
:: Skrypt synchronizacji czasu z serwerem dc1.pda.serwis
:: Uruchamiaj jako administrator!

echo Uruchamianie usługi Windows Time...
net start w32time

echo Konfiguracja serwera czasu...
w32tm /config /manualpeerlist:"dc1.pda.serwis" /syncfromflags:manual /update
timeout /t 2

echo Wymuszenie synchronizacji czasu...
w32tm /resync

echo Synchronizacja zakończona!