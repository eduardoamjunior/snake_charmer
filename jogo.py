import multiprocessing
import sys
import os
import time
import cobrinha  
#Importa especificadamente o hand_controller do gestos
from gestos import hand_controller  

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)

    comando_queue = multiprocessing.Queue()
    pausa_queue = multiprocessing.Queue()

    print("Iniciando o controle por gestos e o jogo da cobrinha...")

    p1 = multiprocessing.Process(target=hand_controller, args=(comando_queue,  pausa_queue))
    p2 = multiprocessing.Process(target=cobrinha.jogo, args=(comando_queue,  pausa_queue)) 

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Aplicação encerrada.")
