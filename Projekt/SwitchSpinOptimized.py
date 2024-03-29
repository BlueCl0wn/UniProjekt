# Bibliotheken
import math
import numpy as np
import time

# Funktionen
from DetermineCharge import getAllCharge
from SaveGitter import saveGraphIMG
from getPosition import getPosition

"""Es gibt mehrere Versionen dieser Datei. V1, V2 und V3. Die Neueste ist jeweils schneller als die Vorherige."""
from  DeltaE.V3 import deltaE

import matplotlib.pyplot as plt

# beta = J/1.380649e-23*T


def switchSpin(conf, n, beta, r, distanz=0, akzeptanzrate=True, GraphE=True, Abbruchbedingung=(True, 100)) -> np.ndarray:
    """
    Wählt einen zufälligen Spin aus, wechselt diesen und überprüft, ob dieser Wechsel beibehalten oder rückgängig gemacht wird.
    Beinhaltet Code zum berechnen der Akzeptanzrate.

    returns Triple (conf_neu, my_graphE, my_akzeptanzVars)
    """

    ptp = None
    # Variabeln für Akzeptanzrate. ALle Codeblöcke, die mit der Akzeptanzrate zu tun haben, werden nur ausgeführt, wenn der Paramter 'akzeptanzrate' 'True' ist. Dieser ist standardmäßig 'False'.
    if akzeptanzrate:
        Versuche = 0
        akzeptiert = 0
        akzeptiertE = 0
        akzeptiertW = 0
        abgelehnt = 0

    # Erzeugt einen Array, in dem die Werte für E gespeichert werden, wenn GraphE 'True' ist
    if GraphE:
        yAxisGraphE = np.zeros(r)

    # Erzeugt einen Array, in dem die Werte für E für die Abbruchbedingung gespeichert werden, wenn Abbruchbedingung 'True' ist
    if Abbruchbedingung[0]:
        AbbruchArray = np.zeros((Abbruchbedingung[1]))

    # beta = 1/T
    T = 1/beta

    posAlt = (None, None)
    pos = None

    altE = getAllCharge(conf, n)


    i = 0
    while(i < r):

        # Position des Spinwechsel wird ausgewählt.
        pos = getPosition(posAlt, distanz, n)

        # Zähler für Akzeptanzrate wird erhöht.
        if akzeptanzrate:
            Versuche += 1

        # DeltaE wird als Zwischenvariable gespeichert.
        dE = deltaE(conf, altE, pos, -conf[pos[0]][pos[1]], n)
        # Vorher:
        # dE = DeltaE.deltaE(conf, altE, pos, -conf[pos[0]][pos[1]], n)

        # DeltaE ist kleiner als 0. Es wird also Energei freigesetzt und dammit ist die Wahrscheinlichkeit fürs Umdrehen 100%.
        if dE <= 0:
            conf[pos[0]][pos[1]] *= -1
            altE = altE + dE

            if akzeptanzrate:
                akzeptiert += 1
                akzeptiertE += 1

        # DeltaE ist größer als 0. Es wird Energie benötigt. Mit gewisser Wahrscheinlichkeit findest Spinwechsel trotzdem statt.
        elif np.random.rand() < math.exp(-beta*dE):
            conf[pos[0]][pos[1]] *= -1
            altE = altE + dE

            # für Akzeptanzrate
            if akzeptanzrate:
                akzeptiert += 1
                akzeptiertW += 1

        else:
            # für Akzeptanzrate
            if akzeptanzrate:
                abgelehnt += 1

            pass

        if GraphE:
            yAxisGraphE[i] = altE



        # Erhöht den Zähler für die While-Loop um 1.
        i += 1

        # Fügt neuen Wert in der AbbruchArray ein und überprüft, ob E über dessen Länge im Bereich von T konstant ist.

        if Abbruchbedingung[0]:
            AbbruchArray = np.concatenate(([altE], AbbruchArray[0:-1]))
            ptp = np.ptp(AbbruchArray)
            # Wenn die Energie nicht mehr stark schwankt, wird dem Zähler i der Wert r zugewiesen, damit die While-Loop beendet wird.
            if ptp < T and i > Abbruchbedingung[1]:
                # x = i
                r = i
                print("abgebrochen, weil E konstant")
                print(ptp)

    # While-Loop zuende

    # Ausgaben für Akzeptanzrate.
    if akzeptanzrate:
    #     print("Versuche = " + str(Versuche))
    #     print("akzeptiert = " + str(akzeptiert))
    #     print("\tdE < 0 = " + str(akzeptiertE))
    #     print("\tw < e = " + str(akzeptiertW))
    #     print("unaccepted = "  + str(abgelehnt))
    #     print("Akzeptanzrate (akzeptiert/Versuche): " + str(akzeptiert/Versuche))
        my_akzeptenzVars = np.array([Versuche, akzeptiert, akzeptiertE, akzeptiertW, abgelehnt, akzeptiert/Versuche])

    if GraphE:
        my_GraphE = yAxisGraphE[0:r]

        # saveGraphIMG(xAxis, np.fft.fft(yAxis), r, n, "EnergieGraphSMooth")
    infos = np.array([n, T, r, ptp])

    return np.array([conf, my_GraphE if GraphE else None, my_akzeptenzVars if akzeptanzrate else None, infos], dtype=object)
