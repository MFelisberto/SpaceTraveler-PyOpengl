from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

""" Classe Hud """
class Hud:

    def __init__(self):     # Construtor da classe
        self.vida = 100     # Vida do jogador
        self.pontos = 0     # Pontos do jogador
    
    def mostraHud(self, tempo): # Mostra o HUD na tela
        
        glColor3f(0.75, 0.75, 0.75)                                              # texto cor cinza

        textoVida = "Life: " + str(self.vida) + "%"                              # texto da vida 
        glRasterPos2f(-145,140)                                                  # posicao do texto na tela 
        for i in range(len(textoVida)):                                          # percorre cada caractere do texto
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(textoVida[i]))   # imprime o texto

        textoPontos = "Score: " + str(int(self.pontos))                          # texto dos pontos
        glRasterPos2f(-145,130)                                                  # posicao do texto na tela 
        for i in range(len(textoPontos)):                                        # percorre cada caractere do texto
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(textoPontos[i])) # imprime o texto

        textoTempo = "Time: " + str(tempo)                                       # texto do tempo                    
        glRasterPos2f(-75,140)                                                   # posicao do texto na tela                    
        for i in range(len(textoTempo)):                                         # percorre cada caractere do texto       
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(textoTempo[i]))  # imprime o texto

        
    def perdeVida(self, dano):                                          # Função que diminui a vida do jogador
        self.vida -= dano                                               # Diminui a vida do jogador dado o dano

    def ganhaVida(self, cura):                                          # Função que aumenta a vida do jogador          
        self.vida += cura                                               # Aumenta a vida do jogador dado a cura

    def ganhaPontos(self, pontos):                                      # Função que aumenta os pontos do jogador
        self.pontos += pontos                                           # Aumenta os pontos do jogador dado os pontos