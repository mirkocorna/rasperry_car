#!/usr/bin/python
# Module: Sensori di distanza (HC-SR04) per auto con Buzzer 
#         e display (C216x01xxW00) 16X2 compatibile con Hitachi HD44780.
#         Il tutto comandato da un raspberry pi mod b (versione 2)

# importo le librerie time, RPi.GPIO e hd44780
import time
import RPi.GPIO as GPIO
import hd44780
import signal

############################
# Variabili globali
############################

# PIN per HC-SR04 e buzzer
pulsetrigger = 0.0001							# Imposto l'impulso per HC-SR04
trigger_list = [16,3]							# GPIO 23 e 3
echo_list = [[18,5],[18,5],[18,5],[18,5],[18,5],[18,5]]			# GPIO 24 e 2
buzzer  = 12               						# GPIO 18
scelta = 0								# Forse inutile

# PIN per HD44780
PINMAP = {
    'RS': 7,			# PIN 26
    'RW': 14,			# GND
    'E': 8,			# PIN 24
    'D4': 25,			# PIN 22
    'D5': 17,			# PIN 11
    'D6': 27,			# PIN 13
    'D7': 22,			# PIN 15
    'LED': 15,			# PIN 10 A che serve? Scollegato
}

CHARMAP = {
        0: (
                0b01110,
                0b10001,
                0b10111,
                0b11001,
                0b10111,
                0b10001,
                0b01110,
                0b00000,
        ),
        1: (
                0b10010,
                0b00100,
                0b01001,
                0b10010,
                0b00100,
                0b01001,
                0b10010,
                0b00100,
        ),
        2: (
                0b01001,
                0b00100,
                0b10010,
                0b01001,
                0b00100,
                0b10010,
                0b01001,
                0b00100,
        ),
        3: (
                0b10101,
                0b01010,
                0b10101,
                0b01010,
                0b10101,
                0b01010,
                0b10101,
                0b01010,
        ),
        4: (
                0b01010,
                0b10101,
                0b01010,
                0b10101,
                0b01010,
                0b10101,
                0b01010,
                0b10101,
        ),
        5: (
                0b11111,
                0b11111,
                0b11111,
                0b11111,
                0b11111,
                0b11111,
                0b11111,
                0b11111,
        ),
        6: (
                0b11111,
                0b10001,
                0b10101,
                0b10101,
                0b10101,
                0b10101,
                0b10001,
                0b11111,
        ),
        7: (
                0b00000,
                0b01110,
                0b01010,
                0b01010,
                0b01010,
                0b01010,
                0b01110,
                0b00000,
        ),
}

############################
# Generale
############################

def selection():
    print "Attiva i sensori in base alla modalita':"
    print "1) Anteriore; \n2) Posteriore; \n3) Sinistra;"
    print "4) Destra; \n5) Anteriore & Posteriore; \n6) Sinistra & Destra"
    scelta = int(raw_input("Scegli modalita' : "))
    init_display(scelta)
    try: 
        while (True):
            if scelta == 1:
                distance = distance_cm(16,18)
                print "Anteriore: " + str(distance)
                sound(distance)
		display_mode(scelta,distance)
            elif scelta == 2:
                distance = distance_cm(3,5)
                print "Posteriore: " + str(distance)
                sound(distance)
                display_mode(scelta,distance)
            elif scelta == 3:
                distance = distance_cm(16,18)
                print "Sinistra: " + str(distance)
                sound(distance)
                display_mode(scelta,distance)
            elif scelta == 4:
   	        distance = distance_cm(3,5)
                print "Destra: " + str(distance)
	        sound(distance)
                display_mode(scelta,distance)
            elif scelta == 5:
		distance1 = distance_cm(16,18)
		distance2 = distance_cm(3,5)
		sound(distance1)
		sound(distance2)
		display_mode(scelta,distance1,distance2)
                print "Anteriore: " + str(distance1)
                print "Posteriore: " + str(distance2)
            elif scelta == 6:
                distance1 = distance_cm(3,5)
                distance2 = distance_cm(16,18)
		sound(distance1)
		sound(distance2)
                display_mode(scelta,distance1,distance2)
                print "Sinistra: " + str(distance1)
                print "Destra: " + str(distance2)
            time.sleep(0.5)
    except KeyboardInterrupt:                                           # Eccezione da tastiera
        print "Stopping"                                                # Finsce il tutto
        GPIO.cleanup()                                                  # Pulisco le impostazioni dei PIN

def initialize():
    GPIO.setmode(GPIO.BOARD)
    GPIO.cleanup()
    GPIO.setwarnings(False)

def timeout_exception(signum, frame):
    raise Exception("s")

def configure_array():
    length = len(trigger_list)
    # Setto i trigger
    for a in range (0, length):
        GPIO.setup(trigger_list[a],GPIO.OUT)
    # Setto gli echo
    for i in range (0, len(echo_list)):
        for j in range (0, len(echo_list[i])):
            GPIO.setup(echo_list[i][j],GPIO.IN)
    GPIO.setup(buzzer, GPIO.OUT)                                        # Imposto il PIN per il Buzzer

############################
# HC-SR04
############################

def fire_trigger(trigger):
# Genero l'impulso per il trigger per 0.0001s
# Il trigger per tutti i sensori o ogni sensore ha un trigger?
    GPIO.output(trigger, True)
    time.sleep(pulsetrigger)
    GPIO.output(trigger, False)

def wait_for_echo(echo, desired_state, sleep):
# Attendo che il PIN ECHO sia del valore desiderato
    try:
        signal.signal(signal.SIGALRM, timeout_exception)		# Imposto il signal
        signal.setitimer(signal.ITIMER_REAL, sleep)			# Setto il timer del signal
        while (GPIO.input(echo) != desired_state):			# finche' non e' lo stato desiderato
            pass							# Non faccio particolari cose
        signal.setitimer(signal.ITIMER_REAL, 0)				# Resetto il timer
        return True							# Restituisco Vero
    except:								# Si attiva il timer
        signal.setitimer(signal.ITIMER_REAL, 0)				# Restituisco Falso
        return False

def measure_time(trigger, echo):
# Effettuo una singola misurazione
    fire_trigger(trigger)						# Impulso per il trigger
    if wait_for_echo(echo,1,0.5):					# Aspetto che ECHO diventi alto
        start = time.time()						# Parte il tempo
        if wait_for_echo(echo,0,0.0175):				# Attendo che ECHO ritorni basso
            stop = time.time()						# Fermo il tempo
	    return (stop - start)					# Resituisco la differenza dei tempi
        else:
            #print "Timeout 2"						# ECHO non e' tornato basso entro il timeout
            return -1							# Troppo distante o onda persa; restituisco -1
    else:
        #print "Timeout 1"						# ECHO non e' tornato alto entro il timeout
        return -1							# Ci impiega troppo a salire; perche'? restituisco -1

def measure_average_time(trigger,echo):
# Dopo 3 misurazioni faccio la media
# Se ottengo un timeout esco subito per non avere dati impuri?
    total_time = 0							# Tempo totale da dividere per le misurazioni
    count = 0								# Imposto la variabile di conteggio
    while(count < 3):  							# Attendo 3 misurazioni
        measure = measure_time(trigger,echo)					# Ricavo il tempo medio
	if measure >= 0:						# Se e' > 0
           total_time = total_time + measure				# Sommo il tempo totale
           count = count + 1						# Sommo il contatore
        else:								# Altrimenti
	   return -1							# Restituisco -1
        time.sleep(0.2)							# Aspetto 0.5 secondi per il prossimo tentativo
    return total_time / 3						# Quando ne ho 3 restituisco il risultato
        
def distance_cm(trigger, echo):
# Calcolo la distanza
    time = measure_average_time(trigger, echo)				# Ottengo time
    if time > 0:							# Se e' maggiore di 0
        return int(time * (1000000 / 58))				# Calcolo la distanza approssimata
    else:
        return 999

############################
# Set Buzzer
############################

def sound(distance):
# Emette un suono con il buzzer man mano che ci si avvicina all'ostacolo
# Ancora da ottimizzarte. Come imposto i BIP in modo che siano riconoscibili
# e allo stesso tempo non diano fastidio?     
    p = GPIO.PWM(buzzer, 1) #channel=12 frequency=1Hz
    p.start(0)
    if distance < 5:
        p.ChangeFrequency(10)
        p.ChangeDutyCycle(75)
        time.sleep(1)
    elif distance < 10:
        p.ChangeFrequency(1)
        p.ChangeDutyCycle(100)
        time.sleep(1)
    elif distance < 20:
        p.ChangeFrequency(1)
        p.ChangeDutyCycle(50)
        time.sleep(1)
    elif distance < 30:
        p.ChangeFrequency(2)
        p.ChangeDutyCycle(50)
        time.sleep(1)
    elif distance < 40:
        p.ChangeFrequency(3)
        p.ChangeDutyCycle(50)
        time.sleep(1)
    elif distance < 50:
        p.ChangeFrequency(4)
        p.ChangeDutyCycle(50)
        time.sleep(1)
    else: pass
    p.stop()

############################
# Set Display
############################
def welcome():
# Messaggio di benvenuto all'accensione
    display.clear()									# Pulisco lo schermo
    display.home()									# Mi posiziono in alto a sinistra
    time.sleep(0.1)									# Attesa forse inutile
    display.cycle_strings("BENVENUTO", delay = 0.1, count = 1, align='left')		# Una lettera alla volta (1 riga)
    display.set_cursor_position(0,1)							# Mi posiziono in basso
    display.cycle_strings("K O K O", delay = 0.1, count = 1, align='left')		# Una lettera alla volta (2 riga)
    time.sleep(0.5)									# Pausa per la visione
    display.clear()									# Pulisco lo schermo
    display.home()									# Mi posiziono in alto a sx
    display.cycle_strings("Distance Sensor", delay = 0.1, count = 1, align='left')	# Una lettera alla volta (1 riga)
    display.set_cursor_position(0,1)							# Mi posiziono in basso
    display.cycle_strings("Version 1.0", delay = 0.1, count = 1, align='left')		# Una lettera alla volta (2 riga)
    time.sleep(0.5)									# Pausa per la visione

def count_asterisks(distance1,distance2=0,mode=1):
# Conta il numero di quadrati neri da visualizzare nello schermo LCD (in base alla distanza)
# Es: una distanza di 40 cm restituira' 6 quadrati (10 - 4)
    d1 = 0								# Imposto le variabili
    d2 = 0
    r1 = 0
    r2 = 0
    if int(distance1) < 100:                                            # Se distanza e' < 100 metri
        d1 = 10 - (int(distance1)/10)					# Calcolo la prima distanza
        r1 = int(distance1 % 10)					# Calcolo il resto x la mezza misura
    if mode >= 5:							# Se e' mode = 5 o 6
        if int(distance2) < 100:                                        # Se distanza e' < 100 metri
            d2 = 10 - (int(distance2)/10)				# Calcolo la seconda distanza
            r2 = int(distance2 % 10)					# Calcolo il resto x la mezza misura
    return d1,r1,d2,r2							# Restituisco i 4 valori

def init_display(mode):
# Imposto la visualizzazione comune x tutte le modalita' (solo sx, solo dx, ...)
    display.clear()							# Comune per tutti
    display.home()							# Torno alla posizione iniziale
    row = [ "REAR ", "FRONT", "LEFT ", "RIGHT", "R", "L", "F", "R" ]	# Lista utile successivamente
    if (mode <=4):							# Se e' modalita' singola
	#display.write_value(0)
	#stop = int(raw_input("STOP"))
        display.write_string(row[mode-1] + "       cm") 		# Scrivo la prima riga
        display.set_cursor_position(2,1)				# Riga successiva
        display.write_string("|          |")				# Imposto il fondo scala
    else:								# Modalita' doppia
        for index in range(0,1):					# Devo scrivere su due righe
            display.write_string(row[mode-1] + "   cm          ")       # Prima riga; anteriore / sinistra
            display.set_cursor_position(0,1)                            # Riga successiva
            display.write_string(row[mode+1] + "   cm          ")       # Seconda riga; posteriore / destra

def display_mode(mode,distance1,distance2=-1):
# Visualizzo la distanza in modalita' singola o doppia
# Da ottimizzare
    d1, r1, d2, r2 = count_asterisks(distance1,distance1,mode)		# Ottengo i 4 valori necessari
    wait = 0                                                            # Inizializzo il tempo di attesa a 0
    if mode <= 4:
        display.set_cursor_position(8,0)                                # Modalita' 0,1,2,3
        if distance1 < 100:
            display.write_string(str(distance1).rjust(3))               # Scrivo la distanza giustificata a sinistra
        display.set_cursor_position(3,1)                                # Seconda riga
        display.write_string("          ")                              # Resetto caratteri precedenti dentro le |
        display.set_cursor_position(3,1)                                # Ritorno dentro le |

        if d1 > 5:                                                      # Se la distanza e' <= 50 cm
            wait = 0.05                                                 # Inizializzo il tempo di attesa a 0.1
            if r1 >= 5:                                                 # Se la distanza e' tra .5 e .9 -> cursore = blink
                d1 = d1 - 1                                             # L'ultimo quadrato e' lampeggiante (cursore)
                display.set_display_enable(cursor = True, cursor_blink = True)      # Abilito cursore
	
        for index in range(0,d1):                                       # Per ogni posizione
            display.write_value((255))                                  # Scrivo il quadrato
            time.sleep(wait)                                            # Attendo 0.1 secondi se e' attivo il flag
	
    else:								# Modalita' 5 e 6
        row = [ 0, distance1, 1, distance2 ]				# Imposto i valori necessari
        for index in range(0,4,2):					# 2 cicli mi servono
            display.set_cursor_position(1,row[index])                   # Scrivo la cifra a 2,0 & 2,1
 	    if row[index+1] < 100:
                display.write_string(str(row[index+1]).rjust(3))        # Scrivo la distanza giustificata a sinistra
            display.set_cursor_position(6,row[index])                   # Mi sposto a 6,0 & 6,1
            display.write_string("          ")                          # Resetto caratteri precedenti dentro le |
        row = [ 0, d1, r1, 1, d2, r2 ]					# Imposto i valori necessari
	for index in range (0,6,3):					# Mi servono 2 cicli
            display.set_cursor_position(6,row[index])                   # Imposto il cursore
 
            if row[index+1] > 5:                                        # Se la distanza e' <= 50 cm
                wait = 0.05                                             # Inizializzo il tempo di attesa a 0.1
                if row[index+2] >= 5:                                   # Se la distanza e' tra .5 e .9 -> cursore = blink
                    row[index+1] = row[index+1] - 1                     # Ultimo quadrato e' lampeggiante (cursore)
                    display.set_display_enable(cursor = True, cursor_blink = True)      # Abilito cursore
            for n in range(0,row[index+1]):                             # Per ogni posizione
                display.write_value((255))                              # Scrivo il quadrato
                time.sleep(wait)                                        # Attendo 0.1 secondi se e' attivo il flag

############################
# Set Main
############################

if __name__ == "__main__":
    print "Start ..."							# Si comincia
    initialize()							# Inizializzo
    configure_array()							# Configuro gli array per dopo
    display = hd44780.Display(backend = hd44780.GPIOBackend, pinmap = PINMAP, charmap = CHARMAP, lines = 2, columns = 16) #istanzio la classe
    #welcome()
    selection()
    time.sleep(1)
