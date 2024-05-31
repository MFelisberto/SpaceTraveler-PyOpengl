from os import system, name
from collections import defaultdict
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from Instancia import *
from ModeloMatricial import *
from ListaDeCoresRGB import *
from datetime import datetime
from queue import Queue
import time
import random
import math
from Menu import *
from Hud import *
from PIL import Image

# Menu e Hud 
menu = Menu()
menuAtivado = True
hud = Hud()
background_texture = None  

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens e area de backup
Personagens = [Instancia() for x in range(1000)]
AREA_DE_BACKUP = 500  

# lista de modelos
Modelos = []

# Variaveis de controle
angulo = 0.0
PersonagemAtual = -1
nInstancias = 0
nTiros = 0
imprimeEnvelope = False
LarguraDoUniverso = 100
dict = defaultdict(list)
idx_inimigos = []
inimigos_ocultos = set()
inimigos_mortos = Queue()
inimigoAtingiuDisparador = False
cont = 0

# Configuracoes do jogo
NUM_INIMIGOS = 30
# quantidade máxima de tiros em sequência dos inimigos
NUM_MAX_TIROS = 1
# quantidade máxima de tiros em sequência do disparador
NUM_MAX_TIROS_DISPARADOR = 5
# quantidade inicial de inimigos na tela
num_inicial_inimigos = 1

# Variaveis de tempo
TempoInicial = time.time()
TempoTotal = time.time()
TempoAnterior = time.time()
jogo = True
tempoPonto = time.time()
DiferencaDeTempo1 = 0
contador = 0
segundoCompleto = 0

# define uma funcao de limpeza de tela
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
        print("*******************")
        print("PWD: ", os.getcwd())


# Função que desenha um quadrado com a textura de fundo
def load_texture(path):
    img = Image.open(path)                    # abre a imagem
    img_data = img.convert("RGBA").tobytes()  # converter a imagem para RGBA e armazena os bytes

    width, height = img.size                  # pega a largura e altura da imagem

    texture_id = glGenTextures(1)             # gera um id para a textura
    glBindTexture(GL_TEXTURE_2D, texture_id)  # faz o bind da textura
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data) # carrega a textura

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR) # define o filtro de minificação
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # define o filtro de magnificação

    return texture_id                          # retorna o id da textura


# Função que rotaciona um ponto em torno de outro ponto
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0, 0, 1)
    glTranslatef(-P.x, -P.y, -P.z)


# Função reshape que é chamada toda vez que a janela é redimensionada
def reshape(w, h):
    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# Função que testa a colisão
def TestaColisao(P1, P2) -> bool:
    for i in range(4):
        A = Personagens[P1].Envelope[i]
        B = Personagens[P1].Envelope[(i+1) % 4]
        for j in range(4):
            C = Personagens[P2].Envelope[j]
            D = Personagens[P2].Envelope[(j+1) % 4]
            if HaInterseccao(A, B, C, D):
                return True
    return False


# Função que atualiza o envelope
def AtualizaEnvelope(i):
    global Personagens
    id = Personagens[i].IdDoModelo
    MM = Modelos[id]
    P = Personagens[i]
    V = P.Direcao * (MM.nColunas/2.0)
    V.rotacionaZ(90)
    A = P.PosicaoDoPersonagem + V
    B = A + P.Direcao*MM.nLinhas
    V = P.Direcao * MM.nColunas
    V.rotacionaZ(-90)
    C = B + V
    V = P.Direcao * -1 * MM.nLinhas
    D = C + V
      
    Personagens[i].Envelope[0] = A
    Personagens[i].Envelope[1] = B
    Personagens[i].Envelope[2] = C
    Personagens[i].Envelope[3] = D

# Função que gera uma posição aleatória (x, y)
def GeraPosicaoAleatoria():
    x = random.uniform(-LarguraDoUniverso, LarguraDoUniverso)
    y = random.uniform(-LarguraDoUniverso, LarguraDoUniverso)
    return Ponto(x, y)

# Função que carrega inimigos ocultos
def CarregaInimigosOcultos():
    inimigo = inimigos_ocultos.pop()
    Personagens[inimigo].Visivel = True
    Personagens[inimigo].Velocidade = 30

# Função que conta meio segundo
def contadorMeioSegundo(TempoAtual):
    global contador 
    contador += TempoAtual - TempoAnterior
    if contador>0.5:
        contador = 0
        return True
    return False

# Função que faz o personagem piscar quando atingido
# efeito de dano na colisao do disparador com o proprio inimigo
def PersonagemAtingidoPisca(id):
    Personagens[id].Visivel = not Personagens[id].Visivel

def AtualizaJogo():
    global imprimeEnvelope, nInstancias, Personagens, atirou,t, inimigos_ocultos, dif, inimigoAtingiuDisparador, cont, tempo, segundoCompleto
    TempoAtual = time.time()

    if segundoCompleto != int(TempoTotal):
        # a cada 2 segundos, é carregado um inimigo que estava oculto
        if inimigos_ocultos and segundoCompleto % 2 ==0 and segundoCompleto!=0:
            CarregaInimigosOcultos()
        segundoCompleto = int(TempoTotal)
        
    if contadorMeioSegundo(TempoAtual):
        AtiraInimigos()
        # a cada meio segundo, são limpados da tela os inimigos mortos (que se transformam em explosão)
        if not inimigos_mortos.empty():
            inimigo_morto = inimigos_mortos.get()
            Personagens[inimigo_morto].Visivel = False
            
    if inimigoAtingiuDisparador:
        if cont < 3:
            PersonagemAtingidoPisca(0)
            cont += TempoAtual - TempoAnterior
        else:
            inimigoAtingiuDisparador = False
            Personagens[0].Visivel = True
            cont = 0

    for i in range(0, nInstancias):
        posx = Personagens[i].Posicao.getX()
        posy = Personagens[i].Posicao.getY()
        if (Personagens[i].Tipo == TipoInstancia.DISPARADOR):
                if (posx > LarguraDoUniverso):
                    Personagens[i].Posicao.set(-LarguraDoUniverso, posy)

                if (posx < -LarguraDoUniverso):
                    Personagens[i].Posicao.set(LarguraDoUniverso, posy)

                if (posy > LarguraDoUniverso):
                    Personagens[i].Posicao.set(posx, -LarguraDoUniverso)

                if (posy < -LarguraDoUniverso):
                    Personagens[i].Posicao.set(posx, LarguraDoUniverso)

        elif (Personagens[i].Tipo == TipoInstancia.INIMIGO):
                if (posx > LarguraDoUniverso-11 or posx < (-LarguraDoUniverso+11)
                or posy > LarguraDoUniverso-11 or posy < (-LarguraDoUniverso+11)):
                    r = random.randint(1, 20)
                    ang = math.degrees(math.atan2(posy, posx)) + 90
                    Personagens[i].Rotacao = ang + r
                    Personagens[i].Direcao = Ponto(0, 1)
                    Personagens[i].Direcao.rotacionaZ(ang + r)

        elif (Personagens[i].Tipo == TipoInstancia.TIRO):
                atirador = Personagens[i].Id
                if (posx > LarguraDoUniverso or posx < -LarguraDoUniverso or posy > LarguraDoUniverso or posy < -LarguraDoUniverso):
                    tiros_atirador = dict[Personagens[atirador].Id]
                    idx = tiros_atirador.index(-i)
                    tiros_atirador[idx] = tiros_atirador[idx] * -1
                    Personagens[i].Posicao = Ponto(LarguraDoUniverso, LarguraDoUniverso)
                    Personagens[i].Visivel = False
                    Personagens[i].Velocidade = 0

    # verifica se há colisão entre o disparador e os tiros inimigos e entre o disparador e os inimigos
    for i in range(1, nInstancias):
        if Personagens[i].Visivel and not inimigoAtingiuDisparador and TestaColisao(0, i):
            if Personagens[i].Tipo == TipoInstancia.TIRO and -i not in dict[0]:
                Personagens[i].Visivel = False
                hud.perdeVida(5)

            elif Personagens[i].Tipo == TipoInstancia.INIMIGO:
                hud.perdeVida(20)
                inimigoAtingiuDisparador = True
    
    # atualiza envelope
    for i in range (0, nInstancias):
        AtualizaEnvelope(i)


    # tiros do disparador contra inimigos
    nInstanciasNTiro = NUM_INIMIGOS + 1
    idx_final_tiros_disparador = nInstanciasNTiro + NUM_MAX_TIROS_DISPARADOR
    for i in range(nInstanciasNTiro, idx_final_tiros_disparador):
        if Personagens[i].Visivel:
            for idx_inimigo in idx_inimigos:
                if Personagens[idx_inimigo].Visivel and TestaColisao(i, idx_inimigo):
                    Personagens[i].Visivel = False
                    Personagens[idx_inimigo].IdDoModelo = 7
                    idx_inimigos.remove(idx_inimigo)
                    inimigos_mortos.put(idx_inimigo)
                    Personagens[idx_inimigo].Velocidade = 0
                    Personagens[idx_inimigo].Tipo = TipoInstancia.EXPLOSAO
                    hud.ganhaPontos(10)

     
def AtualizaPersonagens(tempoDecorrido):
    global nInstancias, menuAtivado
    for i in range(0, nInstancias):
        Personagens[i].AtualizaPosicao(tempoDecorrido)  # (tempoDecorrido)
    AtualizaJogo()


def DesenhaPersonagens():
    global PersonagemAtual, nInstancias

    for i in range(0, nInstancias):
        PersonagemAtual = i
        if Personagens[i].Visivel:
            Personagens[i].Desenha()

              # retorna o id da textura

def draw_background():
    global background_texture

    if background_texture: # se a textura foi carregada
        glBindTexture(GL_TEXTURE_2D, background_texture) # faz o bind da textura
        glEnable(GL_TEXTURE_2D) # habilita a textura
        
        glBegin(GL_QUADS) # desenha um quadrado com a textura
        glTexCoord2f(0.0, 0.0) # coordenadas da textura
        glVertex2f(Min.x, Min.y) # vértice 1
        
        glTexCoord2f(1.0, 0.0) # coordenadas da textura
        glVertex2f(Max.x, Min.y) # vértice 2
        
        glTexCoord2f(1.0, 1.0) # coordenadas da textura
        glVertex2f(Max.x, Max.y) # vértice 3
        
        glTexCoord2f(0.0, 1.0) # coordenadas da textura
        glVertex2f(Min.x, Max.y) # vértice 4
        glEnd()  # finaliza o desenho do quadrado
        
        glDisable(GL_TEXTURE_2D)    # desabilita a textura


def display():
    global TempoInicial, TempoTotal, TempoAnterior, PersonagemAtual, nInstancias, jogo, menuAtivado, Personagens
    
    TempoAtual = time.time()                        # pega o tempo atual
    TempoTotal = TempoAtual - TempoInicial          # calcula o tempo total
    DiferencaDeTempo = TempoAtual - TempoAnterior   # calcula a diferença de tempo

    # desenha o background
    draw_background()

    # Desenha o menu
    if menuAtivado:                                 # se o menu estiver ativo
        menu.menuPrincipal()                        # desenha o menu principal

    if not menuAtivado:                             # se o menu não estiver ativo
        
        # zera o tempo de execução 
        if jogo:
            TempoInicial = time.time()              # zerando o tempo de execução
    
        hud.mostraHud(int(TempoTotal))              # mostra o hud do jogo
        DesenhaPersonagens()                        # desenha os personagens
        AtualizaPersonagens(DiferencaDeTempo)       # atualiza os personagens

        # se vida <= 0, fim de jogo
        if hud.vida <= 0:

            # limpa a tela
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            draw_background()                       # desenha o background
            
            Personagens[0].Visivel = False          # esconde o disparador
            glColor3f(0.75, 0.75, 0.75)             # cor cinza para o texto  
            
            texto = "G A M E   O V E R"             # texto de fim de jogo
            glRasterPos2f(-20,50)                   # posição do texto
            for i in range(len(texto)):             # loop para desenhar o texto
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(texto[i])) 

            texto = "S C O R E : " + str(hud.pontos)    # texto de pontuação
            glRasterPos2f(-20, 40)                      # posição do texto
            for i in range(len(texto)):                 # loop para desenhar o texto
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(texto[i]))
  
        jogo = False                                    # fim de jogo


    glutSwapBuffers()                                   # troca os buffers
    TempoAnterior = TempoAtual                          # atualiza o tempo anterior


# ***********************************************************************************
# The function called whenever a key is pressed.
# Note the use of Python tuples to pass in: (key, x, y)
# ESCAPE = '\033'
ESCAPE = b'\x1b'


def keyboard(*args):
    global imprimeEnvelope, menuAtivado
    print(args)
    # If escape is pressed, kill everything.
    if args[0] == b'1':
        menuAtivado = False
        glutDisplayFunc(display)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'e':
        imprimeEnvelope = True
    if args[0] == b' ':
        Atira(Personagens[0])
    glutPostRedisplay()

def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP acelera para velocidade normal
        Personagens[0].Velocidade = 50
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN desacelera
        Personagens[0].Velocidade = 20
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        Personagens[0].Rotacao += 5
        Personagens[0].Direcao.rotacionaZ(+5)
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        Personagens[0].Rotacao -= 5
        Personagens[0].Direcao.rotacionaZ(-5)
    glutPostRedisplay()



def CarregaModelos():

    # Modelo personagem
    Modelos.append(ModeloMatricial())
    Modelos[0].leModelo("Modelos/Personagem.txt")

    # Modelos inimigos e tiros
    Modelos.append(ModeloMatricial())
    Modelos[1].leModelo("Modelos/Inimigo1.txt")
    Modelos.append(ModeloMatricial())
    Modelos[2].leModelo("Modelos/Inimigo2.txt")
    Modelos.append(ModeloMatricial())
    Modelos[3].leModelo("Modelos/Inimigo3.txt")
    Modelos.append(ModeloMatricial())
    Modelos[4].leModelo("Modelos/Inimigo4.txt")
    Modelos.append(ModeloMatricial())
    Modelos[5].leModelo("Modelos/Tiro.txt")
    Modelos.append(ModeloMatricial())
    Modelos[6].leModelo("Modelos/TiroDisparador.txt")
    Modelos.append(ModeloMatricial())
    Modelos[7].leModelo("Modelos/Explosao.txt")

def DesenhaCelula():
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(0, 1)
    glVertex2f(1, 1)
    glVertex2f(1, 0)
    glEnd()
    pass


def CalculaPivot(nroModelo):
    global Modelos
    MM = Modelos[nroModelo]
    return Ponto(MM.nColunas/2.0, 0)


def DesenhaPersonagemMatricial():
    global PersonagemAtual, count

    MM = ModeloMatricial()

    ModeloDoPersonagem = Personagens[PersonagemAtual].IdDoModelo

    MM = Modelos[ModeloDoPersonagem]
    # MM.Imprime("Matriz:")

    glPushMatrix()
    larg = MM.nColunas
    alt = MM.nLinhas
    # print (alt, " LINHAS e ", larg, " COLUNAS")
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt-1-i, j)
            if cor != -1:  # nao desenha celulas com -1 (transparentes)
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                # DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()


# Esta função deve instanciar todos os personagens do cenário
def CriaInstancias():
    global Personagens, nInstancias, nTiros, idx_inimigos, NUM_INIMIGOS

    # disparador
    ang = -90.0
    Personagens[0].Posicao = Ponto(0, 0)
    Personagens[0].Escala = Ponto(1, 1)
    Personagens[0].Rotacao = ang
    Personagens[0].Id = 0
    Personagens[0].IdDoModelo = 0
    Personagens[0].Modelo = DesenhaPersonagemMatricial
    Personagens[0].Pivot = Ponto(8, 0)
    Personagens[0].Direcao = Ponto(0, 1)  # direcao do movimento para a cima
    Personagens[0].Direcao.rotacionaZ(ang)  # direcao alterada para a direita
    Personagens[0].Velocidade = 0
    Personagens[0+AREA_DE_BACKUP] = copy.deepcopy(Personagens[0])
    nInstancias += 1

    # inimigos
    id_modelo = 1
    for i in range(1, NUM_INIMIGOS+1):
        if id_modelo>4:
            id_modelo = 1
        ang = random.randint(0, 361)
        Personagens[i].Tipo = TipoInstancia.INIMIGO
        Personagens[i].Visivel = True if i<num_inicial_inimigos+1 else False
        Personagens[i].PosicaoDoPersonagem = Ponto(300,300)
        Personagens[i].Posicao = GeraPosicaoAleatoria()
        Personagens[i].Escala = Ponto(1, 1)
        Personagens[i].Rotacao = ang
        Personagens[i].Id = i
        Personagens[i].IdDoModelo = id_modelo
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = CalculaPivot(id_modelo)
        Personagens[i].Direcao = Ponto(0, 1)
        Personagens[i].Direcao.rotacionaZ(ang)
        Personagens[i].Velocidade =  30
        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])
        nInstancias += 1
        idx_inimigos.append(i)
        if i>num_inicial_inimigos:
            inimigos_ocultos.add(i)
        id_modelo += 1
    

    # tiros
    #pos_tiros_vet = nInstancias * (NUM_MAX_TIROS + 1)
    pos_tiros_vet = NUM_INIMIGOS * NUM_MAX_TIROS + NUM_MAX_TIROS_DISPARADOR + NUM_INIMIGOS + 1
    count = 0
    id_atirador = 1
    for i in range(NUM_INIMIGOS+1, pos_tiros_vet):
        ang = random.randint(0, 361)
        Personagens[i].Tipo = TipoInstancia.TIRO
        Personagens[i].Visivel = False
        Personagens[i].Escala = Ponto(1, 1)
        if i - (NUM_INIMIGOS+1) < NUM_MAX_TIROS_DISPARADOR:
            Personagens[i].Id = 0
        else:
            if count>=NUM_MAX_TIROS:
                count = 0
                id_atirador+=1
            Personagens[i].Id = id_atirador
            count+=1
        Personagens[i].IdDoModelo = 6 if i - (NUM_INIMIGOS+1) < NUM_MAX_TIROS_DISPARADOR else 5
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = CalculaPivot(5)
        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])
        nInstancias += 1
        nTiros += 1
        # print("tiro {}, id {}".format(i, Personagens[i].Id))

    GeraVetorTiros()



def Atira(instancia):
    
    id_instancia = instancia.Id     # id da instancia
    tiros = dict[id_instancia]      # vetor de tiros
    
    for tiro in tiros:                           # para cada tiro  
        if tiro > 0:                             # se o tiro estiver disponivel
            idx = tiros.index(tiro)              # pega o indice do tiro
            dict[id_instancia][idx] = -tiro      # marca o tiro como indisponivel             
            Personagens[tiro].Visivel = True     # torna o tiro visivel
            Personagens[tiro].Posicao = (instancia.Envelope[1] + instancia.Envelope[2])*0.5 # posicao do tiro
            Personagens[tiro].Velocidade = 160                          # velocidade do tiro
            Personagens[tiro].Rotacao = instancia.Rotacao               # rotacao do tiro
            Personagens[tiro].Direcao = instancia.Direcao.getPonto()    # direcao do tiro
            break   # sai do loop
    
def AtiraInimigos():
    for idx in idx_inimigos:               # para cada inimigo
        if Personagens[idx].Visivel:       # se o inimigo estiver visivel
            Atira(Personagens[idx])        # atira

def GeraVetorTiros():
    global dict, NUM_MAX_TIROS
    tirosDisponiveis = nInstancias - nTiros                                # tiros disponiveis
    instanciasNTiros = nInstancias - nTiros                                # instancias com tiros
    for i in range(0, instanciasNTiros):                                   # para cada instancia com tiros
        max_tiros = NUM_MAX_TIROS_DISPARADOR if i == 0 else NUM_MAX_TIROS  # quantidade de tiros
        for x in range(0, max_tiros):                                      # para cada tiro
            dict[Personagens[i].Id].append(tirosDisponiveis)               # adiciona o tiro ao vetor
            tirosDisponiveis += 1                                          # incrementa o tiro disponivel



def init():
    global Min, Max, background_texture, TempoInicial, LarguraDoUniverso
    
    clear()  # limpa o console
    CarregaModelos()
    CriaInstancias()
 
    LarguraDoUniverso = 150
    Min = Ponto(-LarguraDoUniverso, -LarguraDoUniverso)
    Max = Ponto(LarguraDoUniverso, LarguraDoUniverso)
    
    background_texture = load_texture("background.jpg")

    TempoInicial = time.time()
    print("Inicio: ", datetime.now())
    print("TempoInicial", TempoInicial)


def animate():
    global angulo, TempoInicial, TempoTotal, TempoAnterior, DiferencaDeTempo1
    angulo = angulo + 1
    glutPostRedisplay()

    TempoAtual = time.time()
    TempoTotal = TempoAtual - TempoInicial
    DiferencaDeTempo1 += TempoAtual - TempoAnterior

    if DiferencaDeTempo1 >= 5 and hud.vida > 0:
        hud.ganhaPontos(100)
        DiferencaDeTempo1 = 0


   

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1083,901)
glutInitWindowPosition(100, 0)
wind = glutCreateWindow("Asteroids 2024 - Mateus Charloto e Marcelo Martins")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
init()



try:
    glutMainLoop()
except SystemExit:
    pass
