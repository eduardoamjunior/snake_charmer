import pygame
import time
import random
import sys
import os
import math  
from multiprocessing import Process, Queue

pygame.mixer.init()

#----------------------- ^ BIBLIOTECAS/DEPENDÊNCIAS ^ ------------------ #

#-------------------------------- CORES RGB ---------------------------- #
preto = (0, 0, 0)
branco = (255, 255, 255)
vermelho = (213, 50, 80)
verde_claro = (50, 205, 50)
verde_escuro = (34, 139, 34)
azul = (65, 105, 225)
roxo = (138, 43, 226)
amarelo = (255, 215, 0)
cinza = (40, 40, 40)
cinza_claro = (100, 100, 100)

#-------------------------------- CORES DESERT THEME ---------------------------- #

areia_claro = (238, 213, 183)  # Areia clara para o fundo
areia_escuro = (193, 154, 107)  # Areia escura para grade
cobra_marrom = (101, 67, 33)   # Marrom para a cobra
cobra_marrom_claro = (160, 120, 90)  # Marrom claro para gradiente da cobra
vermelho_cacto = (170, 50, 50)  # Vermelho para comida (fruta do cacto)
roxo_flor_deserto = (186, 85, 211)  # Roxo para comida especial (flor do deserto)
laranja_sol = (255, 140, 0)    # Laranja para o sol do deserto
ceu_deserto = (135, 206, 235)  # Azul claro para o céu do deserto
ceu_deserto_escuro = (70, 130, 180)  # Azul mais escuro para gradiente do céu

#-------------------------- CONFIGURAÇÃO DO JOGO ----------------------- #
clock = pygame.time.Clock()
tamanho_bloco = 20
velocidade_inicial = 4
dificuldade_maxima = 25
aumento_velocidade = 3


#---------------------------- EFEITOS SONOROS -------------------------- #
try:
    # Sons do jogo
    som_comida_normal = pygame.mixer.Sound("comida_normal.mp3")
    som_comida_especial = pygame.mixer.Sound("comida_especial.mp3")
    som_game_over = pygame.mixer.Sound("game_over.mp3")
    som_inicio_jogo = pygame.mixer.Sound("inicio_jogo.mp3")
    
    # Música de fundo
    pygame.mixer.music.load("musica_fundo.mp3")
    pygame.mixer.music.set_volume(0.3)  # Ajustar volume para não sobrepor os efeitos sonoros
except:
    # Se não conseguir carregar os arquivos de som, cria sons básicos
    print("Arquivos de som não encontrados. Usando sons básicos.")
    
    # Cria sons básicos usando pygame.mixer
    som_comida_normal = pygame.mixer.Sound(pygame.sndarray.make_sound(
        pygame.Surface((20, 1)).map_rgb(pygame.mixer.Sound.get_raw()) * 5000))
    som_comida_normal.set_volume(0.3)
    
    som_comida_especial = pygame.mixer.Sound(pygame.sndarray.make_sound(
        pygame.Surface((40, 1)).map_rgb(pygame.mixer.Sound.get_raw()) * 10000))
    som_comida_especial.set_volume(0.4)
    
    som_game_over = pygame.mixer.Sound(pygame.sndarray.make_sound(
        pygame.Surface((100, 1)).map_rgb(pygame.mixer.Sound.get_raw()) * 8000))
    som_game_over.set_volume(0.5)
    
    som_inicio_jogo = pygame.mixer.Sound(pygame.sndarray.make_sound(
        pygame.Surface((60, 1)).map_rgb(pygame.mixer.Sound.get_raw()) * 6000))
    som_inicio_jogo.set_volume(0.4)
    
    # Criar uma música de fundo básica
    try:
        pygame.mixer.music.load("musica_fundo.mp3")
    except:
        print("Música de fundo não encontrada.")


#-------------------------- FUNÇÕES -------------------------- #
def desenhar_fundo_gradiente():
    # Gradiente de céu do deserto para areia no topo
    cor_topo = ceu_deserto
    cor_meio = ceu_deserto_escuro
    cor_base = areia_claro
    
    # Proporção para transição céu -> areia
    # Mudando de 0.4 para 0.5 para que a areia ocupe metade da tela
    horizonte = altura * 0.5
    
    for y in range(altura):
        if y < horizonte:
            # Céu gradiente
            fator = y / horizonte
            r = cor_topo[0] * (1 - fator) + cor_meio[0] * fator
            g = cor_topo[1] * (1 - fator) + cor_meio[1] * fator
            b = cor_topo[2] * (1 - fator) + cor_meio[2] * fator
        else:
            # Areia gradiente - agora ocupando metade da tela
            # Garantindo que a areia seja a cor predominante na metade inferior
            cor_areia = areia_claro
            r, g, b = cor_areia
        
        pygame.draw.line(tela, (r, g, b), (0, y), (largura, y))
    
    # Adicionar sol
    pygame.draw.circle(tela, laranja_sol, (largura - 100, 80), 40)
    pygame.draw.circle(tela, (255, 200, 50), (largura - 100, 80), 30)
    
    # Adicionar algumas dunas de areia no horizonte
    pygame.draw.ellipse(tela, areia_escuro, [0, horizonte - 10, 300, 60])
    pygame.draw.ellipse(tela, areia_escuro, [250, horizonte - 5, 350, 40])
    pygame.draw.ellipse(tela, areia_escuro, [500, horizonte, 400, 50])
    
    # Adicionar alguns cactos no horizonte
    desenhar_cacto(100, int(horizonte) - 30, 30, 50)
    desenhar_cacto(400, int(horizonte) - 20, 25, 40)
    desenhar_cacto(650, int(horizonte) - 25, 35, 60)

def desenhar_cacto(x, y, largura_cacto, altura_cacto):
    # Tronco principal
    cor_cacto = (50, 120, 50)
    pygame.draw.rect(tela, cor_cacto, [x, y, largura_cacto, altura_cacto])
    
    # Braços do cacto
    pygame.draw.rect(tela, cor_cacto, [x - largura_cacto//2, y + altura_cacto//4, largura_cacto//2, largura_cacto])
    pygame.draw.rect(tela, cor_cacto, [x + largura_cacto, y + altura_cacto//3, largura_cacto//2, largura_cacto])
    
    # Detalhes do cacto
    cor_detalhe = (30, 100, 30)
    for i in range(3):
        pygame.draw.line(tela, cor_detalhe, 
                     (x + largura_cacto//4, y + i*altura_cacto//3), 
                     (x + largura_cacto//4, y + i*altura_cacto//3 + altura_cacto//6), 2)
        pygame.draw.line(tela, cor_detalhe, 
                     (x + largura_cacto*3//4, y + i*altura_cacto//3 + altura_cacto//8), 
                     (x + largura_cacto*3//4, y + i*altura_cacto//3 + altura_cacto//4), 2)

# Função para desenhar grade de fundo sutíl
def desenhar_grade():
    tamanho_grade = 20
    cor_grade = areia_escuro
    alpha_grade = 100  # Transparência para efeito de areia
    
    # Superfície com transparência
    s = pygame.Surface((largura, altura), pygame.SRCALPHA)
    
    # Linhas horizontais onduladas para simular dunas
    for y in range(0, altura, tamanho_grade):
        pontos = []
        for x in range(0, largura+10, 10):
            # Altura variável para ondulação sutil
            offset = math.sin(x/50) * 3
            pontos.append((x, y + offset))
        
        if len(pontos) > 1:
            pygame.draw.lines(s, (*cor_grade, alpha_grade), False, pontos, 1)
    
    # Linhas verticais com leve ondulação
    for x in range(0, largura, tamanho_grade):
        pontos = []
        for y in range(0, altura+10, 10):
            # Ondulação mais sutil nas verticais
            offset = math.sin(y/70) * 2
            pontos.append((x + offset, y))
        
        if len(pontos) > 1:
            pygame.draw.lines(s, (*cor_grade, alpha_grade), False, pontos, 1)
    
    tela.blit(s, (0, 0))

# Função para exibir mensagens na tela
def mensagem(msg, fonte, cor, pos, centralizado=False):
    texto = fonte.render(msg, True, cor)
    if centralizado:
        pos_texto = texto.get_rect(center=pos)
        tela.blit(texto, pos_texto)
    else:
        tela.blit(texto, pos)

# Função para desenhar a cobra com efeito de gradiente (com tema deserto)
def desenhar_cobra(lista_cobra):
    for i, bloco in enumerate(lista_cobra):
        fator = i / max(len(lista_cobra), 1)
        r = int(cobra_marrom_claro[0] * (1 - fator) + cobra_marrom[0] * fator)
        g = int(cobra_marrom_claro[1] * (1 - fator) + cobra_marrom[1] * fator)
        b = int(cobra_marrom_claro[2] * (1 - fator) + cobra_marrom[2] * fator)
        cor_segmento = (r, g, b)
        pygame.draw.rect(tela, cor_segmento, [bloco[0], bloco[1], tamanho_bloco, tamanho_bloco])
        
        # Adicionar detalhes de escamas com padrão de cobra do deserto
        if i % 3 == 0:  # Padrão de escamas a cada 3 segmentos
            pygame.draw.rect(tela, (r-30, g-30, b-30), 
                           [bloco[0]+2, bloco[1]+2, tamanho_bloco-4, tamanho_bloco-4], 1)
        
        # Adicionar olhos à cabeça
        if i == len(lista_cobra) - 1:
            meio_bloco = tamanho_bloco // 2
            olho_raio = tamanho_bloco // 5
            olho_x = bloco[0] + meio_bloco
            olho_y = bloco[1] + meio_bloco
            
            # Desenhar olhos amarelos (típico de cobras do deserto)
            pygame.draw.circle(tela, laranja_sol, (olho_x - meio_bloco//2, olho_y - meio_bloco//2), olho_raio)
            pygame.draw.circle(tela, laranja_sol, (olho_x + meio_bloco//2, olho_y - meio_bloco//2), olho_raio)
            
            # Pupila vertical (tipo cobra)
            pygame.draw.ellipse(tela, preto, 
                           [olho_x - meio_bloco//2 - olho_raio//4, 
                            olho_y - meio_bloco//2 - olho_raio//2,
                            olho_raio//2, olho_raio*1.5])
            pygame.draw.ellipse(tela, preto, 
                           [olho_x + meio_bloco//2 - olho_raio//4, 
                            olho_y - meio_bloco//2 - olho_raio//2,
                            olho_raio//2, olho_raio*1.5])

# Função para desenhar comida com efeito de fruta do deserto
def desenhar_comida(comida_x, comida_y, tipo_comida):
    if tipo_comida == "normal":
        # Fruta do cacto (vermelho)
        pygame.draw.circle(tela, vermelho_cacto, (comida_x + tamanho_bloco//2, comida_y + tamanho_bloco//2), tamanho_bloco//2)
        # Detalhes da fruta
        pygame.draw.circle(tela, (vermelho_cacto[0]+40, vermelho_cacto[1]+40, vermelho_cacto[2]+40),
                          (comida_x + tamanho_bloco//3, comida_y + tamanho_bloco//3), tamanho_bloco//6)
    else:  # Comida especial - flor do deserto
        # Base da flor
        pygame.draw.circle(tela, roxo_flor_deserto, (comida_x + tamanho_bloco//2, comida_y + tamanho_bloco//2), tamanho_bloco//2)
        
        # Pétalas da flor
        for i in range(5):
            angulo = i * (2 * math.pi / 5)
            px = comida_x + tamanho_bloco//2 + int(math.cos(angulo) * tamanho_bloco//3)
            py = comida_y + tamanho_bloco//2 + int(math.sin(angulo) * tamanho_bloco//3)
            pygame.draw.circle(tela, (roxo_flor_deserto[0]+50, roxo_flor_deserto[1]+50, roxo_flor_deserto[2]+50),
                              (px, py), tamanho_bloco//4)
        
        # Centro da flor
        pygame.draw.circle(tela, laranja_sol, (comida_x + tamanho_bloco//2, comida_y + tamanho_bloco//2), tamanho_bloco//4)

# Função para desenhar a área de jogo
def desenhar_area_jogo():
    # Desenhar borda da área de jogo com estilo desértico
    pygame.draw.rect(tela, areia_escuro, [0, 0, largura, altura], 3)

# Função para exibir a tela de menu
def tela_menu(comando_queue=None):
    menu_ativo = True
    opcao_selecionada = 0
    opcoes = ["JOGAR", "DIFICULDADE", "MÚSICA: ON", "SAIR"]
    dificuldade = "NORMAL"
    velocidade = velocidade_inicial
    musica_ativa = True
    
# Função para exibir a tela de menu
def tela_menu(comando_queue=None):
    menu_ativo = True
    opcao_selecionada = 0
    opcoes = ["JOGAR", "DIFICULDADE", "MÚSICA: ON", "SAIR"]
    dificuldade = "NORMAL"
    velocidade = velocidade_inicial
    musica_ativa = True
    
    # Iniciar música de fundo no menu
    try:
        pygame.mixer.music.play(-1)  # -1 significa loop infinito
    except:
        print("Não foi possível iniciar a música de fundo.")
    
    while menu_ativo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                elif evento.key == pygame.K_DOWN:
                    opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN:
                    if opcao_selecionada == 0:  # JOGAR
                        som_inicio_jogo.play()  # Toca som de início do jogo
                        return velocidade, musica_ativa
                    elif opcao_selecionada == 1:  # DIFICULDADE
                        if dificuldade == "NORMAL":
                            dificuldade = "DIFÍCIL"
                            velocidade = velocidade_inicial + 5
                        else:
                            dificuldade = "NORMAL"
                            velocidade = velocidade_inicial
                    elif opcao_selecionada == 2:  # MÚSICA
                        musica_ativa = not musica_ativa
                        opcoes[2] = f"MÚSICA: {'ON' if musica_ativa else 'OFF'}"
                        if musica_ativa:
                            try:
                                pygame.mixer.music.play(-1)
                            except:
                                print("Não foi possível retomar a música.")
                        else:
                            pygame.mixer.music.stop()
                    elif opcao_selecionada == 3:  # SAIR
                        pygame.quit()
                        sys.exit()
        #   Comando de mão
        if comando_queue is not None:
            try:
                if not comando_queue.empty():  
                    carlo = comando_queue.get_nowait()
                    print(f"Comando recebido: {carlo}")
                    
                    if carlo == "ENTER":
                         evento_tecla = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
                         pygame.event.post(evento_tecla)
                    if carlo =="UP":
                       opcao_selecionada = (opcao_selecionada - 1) % len(opcoes) 
                    if carlo =="DOWN":
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)

            except Exception as e:
                print(f"Erro ao processar comando: {e}")

        # Desenhar fundo
        desenhar_fundo_gradiente()
        desenhar_grade()
        
        # Título
        mensagem("SNAKE CHARMER", fonte_titulo, amarelo, (largura//2, 100), True)
        
        # Desenhar opções do menu
        for i, opcao in enumerate(opcoes):
            cor = amarelo if i == opcao_selecionada else branco
            
            if i == 1:
                texto = f"{opcao}: {dificuldade}"
            else:
                texto = opcao
                
            mensagem(texto, fonte_menu, cor, (largura//2, 250 + i*60), True)
        
        tempo = pygame.time.get_ticks() / 1000
        pos_x = int(largura//2 + 150 * math.cos(tempo))
        pos_y = int(altura//2 + 100 * math.sin(tempo*1.5))
        
        pygame.draw.circle(tela, verde_claro, (pos_x, pos_y), 15)
        
        pygame.display.update()
        clock.tick(60)


def jogo(comando_queue, pausa_queue):
    global largura,altura,tela,fonte_titulo,fonte_score,fonte_menu,fonte_game_over

    pygame.init() 

    largura = 800
    altura = 600
    tela = pygame.display.set_mode((largura, altura))  
    pygame.display.set_caption("Snake Charmer 🎵🐍")

    fonte_titulo = pygame.font.Font(None, 74)
    fonte_score = pygame.font.Font(None, 36)
    fonte_menu = pygame.font.Font(None, 40)
    fonte_game_over = pygame.font.Font(None, 90)
    

    # Pegar velocidade e estado da música do menu
    velocidade, musica_ativa = tela_menu(comando_queue)
    
    fim_jogo = False
    game_over = False
    pausado = False

    # Posição inicial da cobra
    x = largura / 2
    y = altura / 2
    x_mudanca = 0
    y_mudanca = 0
    direcao_anterior = None

    proximo_movimento = None
    contador_movimento = 0
    intervalo_movimento = 3

    lista_cobra = []
    comprimento_cobra = 1
    pontuacao = 0
    
    # Posição inicial da comida
    comida_x = round(random.randrange(20, largura - 40) / 20.0) * 20.0
    comida_y = round(random.randrange(70, altura - 40) / 20.0) * 20.0
    
    # Comida especial (aparece ocasionalmente)
    comida_especial_x = -100
    comida_especial_y = -100
    comida_especial_ativa = False
    comida_especial_contador = 0
    
    # Fator de escurecimento para efeito de pausa
    fator_pausa = 0
    
    # Efeitos de partículas
    particulas = []
    
    while not fim_jogo:
        # Tela de game over
        while game_over:
            # Pausar a música de fundo quando o jogo termina
            pygame.mixer.music.stop()
            
            desenhar_fundo_gradiente()
            
            # Escurecer a tela
            s = pygame.Surface((largura, altura))
            s.set_alpha(180)
            s.fill(preto)
            tela.blit(s, (0, 0))
            
            # TELA MORTE
            mensagem("GAME OVER", fonte_game_over, vermelho, (largura//2, altura//2 - 100), True)
            mensagem(f"Pontuação Final: {pontuacao}", fonte_score, branco, (largura//2, altura//2), True)
            mensagem("Pressione C para jogar novamente", fonte_menu, branco, (largura//2, altura//2 + 80), True)
            mensagem("Pressione Q para sair", fonte_menu, branco, (largura//2, altura//2 + 130), True)
            
            pygame.display.update()
            #Comando de mão para resetar
            if not comando_queue.empty():
                roberto = comando_queue.get_nowait()
                if roberto == "ENTER":
                    return jogo(comando_queue, pausa_queue)
                
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    fim_jogo = True
                    game_over = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_q:
                        fim_jogo = True
                        game_over = False
                    if evento.key == pygame.K_c:
                        return jogo(comando_queue, pausa_queue)
                        



        #-------------------------- SEÇÃO FILA DE COMANDOS --------------------------#
        try:
            if not pausa_queue.empty():
                jogo_pausado = pausa_queue.get_nowait()
                if jogo_pausado:
                    pausado = True
                    fator_pausa = 0
                    # Pausar a música quando o jogo é pausado
                    if musica_ativa:
                        pygame.mixer.music.pause()
                else:
                    pausado = False
                    # Retomar a música quando o jogo é despausado
                    if musica_ativa:
                        pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Erro na fila de pausa: {e}")
        
        #-------------------------- SEÇÃO COMANDOS DE MOVIMENTO DO MEDIAPIPE --------------------------#
        if not pausado:
            try:
                if not comando_queue.empty():
                    current_direction = comando_queue.get_nowait()
                    
                    if current_direction == "LEFT" and direcao_anterior != "RIGHT":
                        x_mudanca = -tamanho_bloco
                        y_mudanca = 0
                        direcao_anterior = "LEFT"

                    elif current_direction == "RIGHT" and direcao_anterior != "LEFT":
                        x_mudanca = tamanho_bloco
                        y_mudanca = 0
                        direcao_anterior = "RIGHT"

                    elif current_direction == "UP" and direcao_anterior != "DOWN":
                        x_mudanca = 0
                        y_mudanca = -tamanho_bloco
                        direcao_anterior = "UP"

                    elif current_direction == "DOWN" and direcao_anterior != "UP":
                        x_mudanca = 0
                        y_mudanca = tamanho_bloco
                        direcao_anterior = "DOWN"

                    # Comandos Duplos para gestos
                    elif current_direction == "RIGHT_UP" and direcao_anterior!= "DOWN" and direcao_anterior !="LEFT" and direcao_anterior !="RIGHT_DOWN":
                        x_mudanca = tamanho_bloco
                        y_mudanca = -tamanho_bloco
                        direcao_anterior = "RIGHT_UP"

                    elif current_direction =="LEFT_UP" and direcao_anterior != "DOWN" and direcao_anterior !="RIGHT" and direcao_anterior !="LEFT_DOWN":
                        x_mudanca = -tamanho_bloco
                        y_mudanca = -tamanho_bloco
                        direcao_anterior = "LEFT_UP"

                    elif current_direction =="RIGHT_DOWN" and direcao_anterior != "UP" and direcao_anterior !="LEFT" and direcao_anterior !="RIGHT_UP":
                        x_mudanca = tamanho_bloco
                        y_mudanca = tamanho_bloco
                        direcao_anterior = "RIGHT_DOWN"

                    elif current_direction =="LEFT_DOWN" and direcao_anterior != "UP" and direcao_anterior !="RIGHT" and direcao_anterior !="LEFT_UP":
                        x_mudanca = -tamanho_bloco
                        y_mudanca = tamanho_bloco
                        direcao_anterior = "LEFT_DOWN"

            except Exception as e:
                print(f"Erro ao ler da fila de comandos: {e}")

                #-------------------------- SEÇÃO COMANDOS DE MOVIMENTO DO TECLADO --------------------------#
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                fim_jogo = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and direcao_anterior != "RIGHT":
                    x_mudanca = -tamanho_bloco
                    y_mudanca = 0
                    direcao_anterior = "LEFT"
                elif evento.key == pygame.K_RIGHT and direcao_anterior != "LEFT":
                    x_mudanca = tamanho_bloco
                    y_mudanca = 0
                    direcao_anterior = "RIGHT"
                elif evento.key == pygame.K_UP and direcao_anterior != "DOWN":
                    y_mudanca = -tamanho_bloco
                    x_mudanca = 0
                    direcao_anterior = "UP"
                elif evento.key == pygame.K_DOWN and direcao_anterior != "UP":
                    y_mudanca = tamanho_bloco
                    x_mudanca = 0
                    direcao_anterior = "DOWN"
                elif evento.key == pygame.K_p:
                    pausado = not pausado
                    fator_pausa = 0
                    # Pausar/retomar música quando o jogo é pausado/despausado
                    if musica_ativa:
                        if pausado:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                elif evento.key == pygame.K_m:
                    # Alternar música ligada/desligada
                    musica_ativa = not musica_ativa
                    if musica_ativa:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
        
        # Tela de pausa
        if pausado:
            # Efeito de escurecimento gradual
            if fator_pausa < 150:
                fator_pausa += 10
            
            s = pygame.Surface((largura, altura))
            s.set_alpha(fator_pausa)
            s.fill(preto)
            tela.blit(s, (0, 0))
            
            mensagem("JOGO PAUSADO", fonte_titulo, branco, (largura//2, altura//2 -30), True)
            mensagem("Pressione P para continuar", fonte_menu, branco, (largura//2, altura//2 + 60), True)
            mensagem("Abra mão para continuar", fonte_menu, branco, (largura//2, altura//2 + 100), True)
            mensagem(f"Música: {'ON' if musica_ativa else 'OFF'} (Pressione M)", fonte_menu, branco, (largura//2, altura//2 + 140), True)
            
            pygame.display.update()
            clock.tick(60)
            continue

        # Verificação de colisão com bordas
        if x < 10 or x >= largura-10-tamanho_bloco or y < 50 or y >= altura-10-tamanho_bloco:
            som_game_over.play()  # Som de game over quando colide com as bordas
            game_over = True

        # Atualização da posição da cobra
        x += x_mudanca
        y += y_mudanca
        
        # Desenhar elementos visuais
        desenhar_fundo_gradiente()
        desenhar_grade()
        desenhar_area_jogo()
        
        # Desenhar comida
        desenhar_comida(comida_x, comida_y, "normal")
        
        # Comida especial (com temporizador)
        if not comida_especial_ativa:
            comida_especial_contador += 1
            if comida_especial_contador >= 100:  # Aparecer a cada 100 ticks
                comida_especial_ativa = True
                comida_especial_x = round(random.randrange(20, largura - 40) / 20.0) * 20.0
                comida_especial_y = round(random.randrange(70, altura - 40) / 20.0) * 20.0
                comida_especial_contador = 0
        else:
            comida_especial_contador += 1
            if comida_especial_contador < 50:  # Permanece por 50 ticks
                desenhar_comida(comida_especial_x, comida_especial_y, "especial")
            else:
                comida_especial_ativa = False
                comida_especial_contador = 0
                comida_especial_x = -100
                comida_especial_y = -100

        # Atualizar a lista da cobra com a nova posição
        cabeca_cobra = [x, y]
        lista_cobra.append(cabeca_cobra)

        # Garantir que o comprimento da cobra está correto
        if len(lista_cobra) > comprimento_cobra:
            del lista_cobra[0]

        # Verificar se a cobra colidiu com si mesma
        for segmento in lista_cobra[:-1]:
            if segmento == cabeca_cobra:
                # Adicionar partículas de explosão
                for _ in range(20):
                    ang = random.uniform(0, 6.28)
                    vel = random.uniform(2, 5)
                    vx = vel * math.cos(ang)
                    vy = vel * math.sin(ang)
                    particulas.append({
                        'x': x, 'y': y,
                        'vx': vx, 'vy': vy,
                        'cor': verde_claro,
                        'vida': 30
                    })
                som_game_over.play()  # Som de game over quando colide consigo mesma
                game_over = True

        # Desenhar a cobra
        desenhar_cobra(lista_cobra)
        
        # Atualizar e desenhar partículas
        novas_particulas = []
        for p in particulas:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vida'] -= 1
            
            if p['vida'] > 0:
                alpha = min(255, p['vida'] * 8)
                raio = max(1, p['vida'] // 5)
                s = pygame.Surface((raio*2, raio*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p['cor'], alpha), (raio, raio), raio)
                tela.blit(s, (p['x'] - raio, p['y'] - raio))
                novas_particulas.append(p)
        
        particulas = novas_particulas
        
        # Interface de pontuação
        pygame.draw.rect(tela, cinza, [0, 0, largura, 40])
        mensagem(f"Pontuação: {pontuacao}", fonte_score, amarelo, (20, 10))
        
        # Velocidade do jogo
        vel_atual = min(dificuldade_maxima, velocidade + (pontuacao // 5))
        mensagem(f"Velocidade: {vel_atual}", fonte_score, amarelo, (largura - 200, 10))
        
        # Status da música
        mensagem(f"M: Música {'ON' if musica_ativa else 'OFF'}", fonte_score, amarelo, (largura - 400, 10))

        pygame.display.update()

        # Detectar colisão com a comida normal
        if x == comida_x and y == comida_y:
            # Tocar som de comida normal
            som_comida_normal.play()
            
            # Adicionar partículas quando a comida é consumida
            for _ in range(10):
                ang = random.uniform(0, 6.28)
                vel = random.uniform(1, 3)
                vx = vel * math.cos(ang)
                vy = vel * math.sin(ang)
                particulas.append({
                    'x': comida_x, 'y': comida_y,
                    'vx': vx, 'vy': vy,
                    'cor': vermelho,
                    'vida': 20
                })
                
            comida_x = round(random.randrange(20, largura - 40) / 20.0) * 20.0
            comida_y = round(random.randrange(70, altura - 40) / 20.0) * 20.0
            comprimento_cobra += 1
            pontuacao += 1
        
        # Detectar colisão com comida especial
        if comida_especial_ativa and x == comida_especial_x and y == comida_especial_y:
            # Tocar som de comida especial
            som_comida_especial.play()
            
            # Adicionar partículas quando a comida especial é consumida
            for _ in range(15):
                ang = random.uniform(0, 6.28)
                vel = random.uniform(1, 4)
                vx = vel * math.cos(ang)
                vy = vel * math.sin(ang)
                particulas.append({
                    'x': comida_especial_x, 'y': comida_especial_y,
                    'vx': vx, 'vy': vy,
                    'cor': roxo,
                    'vida': 25
                })
                
            comida_especial_ativa = False
            comida_especial_contador = 0
            comida_especial_x = -100
            comida_especial_y = -100
            comprimento_cobra += 2
            pontuacao += 3
        
        # Velocidade aumenta com a pontuação
        vel_atual = min(dificuldade_maxima, velocidade + (pontuacao // 5))
        clock.tick(vel_atual)

    pygame.quit()
    quit()

# Inicia o jogo
#if __name__ == "__main__":
#    jogo()