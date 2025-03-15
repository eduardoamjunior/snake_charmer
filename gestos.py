import cv2
import mediapipe as mp
import numpy as np
import time
import multiprocessing

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Para ajustar a imagem do vídeo, procure por "image = cv2.flip(image, 1)" e comente caso queira tirar o flip da imagem

def hand_controller(comando_queue, pausa_queue):
    cap = cv2.VideoCapture(0)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    center_x, center_y = width // 2, height // 2
    
    #Estado do jogo
    jogo_pausado = False
    comando_enviado = False

    ultimo_envio = 0  # Marca o tempo do último envio
    cooldown = 0.3
    
    # Setup do mediapipe
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1) as hands:
        
        # Para organizar os comandos
        current_direction = "NONE"
        last_sent_direction = "NONE"  # Última direção enviada
        
        # tamanho deadzone
        dead_zone_radius = 80  # Pixels
        
        # define a distancia minima em pixel que a mao precisa mover para executar o comando
        movement_threshold = 90 #horizontal
        vertical_threshold = 70  #vertical
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Failed to capture frame.")
                continue
            
            # Processo de imagem
            image.flags.writeable = False
            image = cv2.flip(image,1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            # Preparing for drawing
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # DESENHO DA TELA
            # Ponto Central fixo
            cv2.circle(image, (center_x, center_y), 10, (255, 255, 255), -1)
            # Zona morta
            cv2.circle(image, (center_x, center_y), dead_zone_radius, (0, 255, 255), 2)

            # ---- FAZ OS PONTOS DA MAO EM COORDENADA ---
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # DESENHA AS JUNTAS DA MAO
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Pega a coordenada do pulso
                palm_center = hand_landmarks.landmark[0]
                cx, cy = int(palm_center.x * width), int(palm_center.y * height)
                cv2.circle(image, (cx, cy), 10, (0, 255, 0), -1)
                
                dx = cx - center_x
                dy = cy - center_y
                
                # acha a distancia entre os pontos x e y em relação ao ponto 0
                distance = np.sqrt(dx**2 + dy**2)
                
                # Create a list of points for finger counting
                pontos = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    px, py = int(lm.x * width), int(lm.y * height)
                    pontos.append((px, py))
                
                # ------ Contador de dedo ---------- #
                dedos = [8, 12, 16, 20]
                contador = 0
                
                for x in dedos:
                    if pontos[x][1] < pontos[x-2][1]:  
                        contador += 1
                        cv2.circle(image, pontos[x], 8, (0, 255, 255), -1)
                
                # Verifica o polegar
                if pontos[4][0] < pontos[3][0]:  
                    contador += 1
                    cv2.circle(image, pontos[4], 8, (0, 255, 255), -1)
                    if contador == 1 and (time.time() - ultimo_envio) >= cooldown:
                        current_direction = "ENTER"
                        comando_queue.put("ENTER")
                        comando_enviado = True
                        ultimo_envio = time.time()
                
                
                
                # CHECAGEM DA DEAD ZONE
                novo_estado_pausa = contador == 0
                if novo_estado_pausa != jogo_pausado:
                    jogo_pausado = novo_estado_pausa
                    pausa_queue.put(jogo_pausado)
                    
                #----------------------- DEBUG TEXTO -----------------------#
                #cv2.putText(image, f"Dedos: {contador}", (10, 130), 
                           #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                #estado = "PAUSADO" if jogo_pausado else "ATIVO"
                #cv2.putText(image, f"Estado: {estado}", (10, 160), 
                           #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                #Tipo de comando
                #Ultimo comando
                cv2.putText(image, f"Comando: {current_direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                #cv2.putText(image, f"Ultimo Comando: {last_sent_direction}", (10, 190), 
                       #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                #reset_status = "Pronto para novo comando" if not comando_enviado else "Volte ao centro para resetar"
                #cv2.putText(image, reset_status, (10, 220), 
                #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)#
                

                # Check if in dead zone
                if distance < dead_zone_radius:
                    current_direction = "NONE"
                    comando_enviado = False 
                else:
                    # Se nao, faz calculo dos movimentos
                    angle = np.arctan2(dy, dx) * 180 / np.pi
                    is_vertical = abs(angle) > 60 and abs(angle) < 120
                    threshold_to_use = vertical_threshold if is_vertical else movement_threshold
                    
                    if distance >= threshold_to_use:
                        # Corta a tela em 8 partes como se fosse um circulo para o movimento
                        if -22.5 <= angle < 22.5:
                            current_direction = "DIREITA"
                        elif 67.5 <= angle < 112.5:
                            current_direction = "BAIXO"
                        elif 112.5 <= angle < 157.5:
                            current_direction = "ESQUERDA_BAIXO"
                        elif 22.5 <= angle < 67.5:
                            current_direction = "DIREITA_BAIXO"
                        elif 157.5 <= angle <= 180 or -180 <= angle < -157.5:
                            current_direction = "ESQUERDA"
                        elif -157.5 <= angle < -112.5:
                            current_direction = "ESQUERDA_CIMA"
                        elif -67.5 <= angle < -22.5:
                            current_direction = "DIREITA_CIMA"
                        elif -112.5 <= angle < -67.5:
                            current_direction = "CIMA"
                            
            # Mostra a imagem
            cv2.imshow('Hand Motion Control', image)
            
            #Envia os comandos
            if current_direction != "NONE" and not jogo_pausado and not comando_enviado:
                if current_direction == "DIREITA":
                    comando_queue.put("RIGHT")
                    #print(f"Comando enviado: DIREITA")
                elif current_direction == "ESQUERDA":
                    comando_queue.put("LEFT")
                    #print(f"Comando enviado: ESQUERDA")
                elif current_direction == "CIMA":
                    comando_queue.put("UP")
                    #print(f"Comando enviado: CIMA")
                elif current_direction == "BAIXO":
                    comando_queue.put("DOWN")
                    #print(f"Comando enviado:: BAIXO")
                elif current_direction == "DIREITA_CIMA":
                    comando_queue.put("RIGHT_UP")
                    #print(f"Comando enviado: DIREITA CIMA")
                elif current_direction == "DIREITA_BAIXO":
                    comando_queue.put("RIGHT_DOWN")
                    #print(f"Comando enviado: BAIXO DIREITA")
                elif current_direction == "ESQUERDA_CIMA":
                    comando_queue.put("LEFT_UP")
                    #print(f"Comando enviado: CIMA ESQUERDA")
                elif current_direction == "ESQUERDA_BAIXO":
                    comando_queue.put("LEFT_DOWN")
                    #print(f"Comando enviado: BAIXO ESQUERDA")
                
                comando_enviado = True
            if cv2.waitKey(5) & 0xFF == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    hand_controller()