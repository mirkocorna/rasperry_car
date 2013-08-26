rasperry_car
============
README sintetito

Il progetto iniziale prevede l'utilizzo di alcuni sensori HC-SR04 (sensori di sistanza) collegati alla scheda Raspberry ver. 2
L'impulso del trigger così come quello di echo dei sensori (2 al momento), vengono gestiti separatamente.
La successiva modifica riguarderà l'utilizzo di un singolo pin dedicato al trigger. La modifica dovrà quindi prevedere l'utilizzo di processi paralleli (non so se ciò è fattibile ma ci proverò).
Successivamente alla ricezione dell'echo, il sensore attiva il PIN del raspberry che a sua volta visualizzerà il valore rilevato su un display LCD 16X2 (compatibile con HD47780).
Per l'utilizzo del display LCD mi sono basato sulla classe hd44780 (disponibile tramite pip).
Al momento sussistono problemi con l'utilizzo dei caratteri CHARMAP. In sostituzione di quest'ultimi ho utilizzato il display del modulo LCD.
Contemporaneamente alla rilevazione della distanza, il buzzer emette un BIP. Il numero di BIP emessi dal buzzer dipende dal valore della distanza.

Ovviamente molte procedure sono allo stato embrionale e non sono ottimizzate.

All'interno del repository sono presenti due immagini relative ai collegamenti ed un file fritzing.
