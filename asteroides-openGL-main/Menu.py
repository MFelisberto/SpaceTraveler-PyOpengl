from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

""" Classe Menu """
class Menu:
    
    def menuPrincipal(self):
        texto = "SPACE TRAVELER"
        texto2 = "[ 1 ] START GAME"
        texto3 = "[ ESC ] QUIT GAME"

        glColor3f(0.75, 0.75, 0.75)                                         # texto cor cinza
        glRasterPos2f(-20,50)                                               # posicao do texto na tela
        for i in range(len(texto)):                                         # percorre cada caractere do texto
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(texto[i]))  # imprime o texto

        glColor3f(0.75, 0.75, 0.75)                                         # texto2 cor cinza
        glRasterPos2f(-20,-50)                                              # posicao do texto2 na tela
        for i in range(len(texto2)):                                        # percorre cada caractere do texto
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(texto2[i])) # imprime o texto 

        glColor3f(0.75, 0.75, 0.75)                                         # texto3 cor cinza
        glRasterPos2f(-20,-60)                                              # posicao do texto3 na tela
        for i in range(len(texto3)):                                        # percorre cada caractere do texto
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(texto3[i])) # imprime o texto 

    
        # Faz uma moldura para o titulo
        glBegin(GL_LINE_LOOP)   # Desenha um quadrado
        glVertex2f(-30, 60)     # Vertice 1
        glVertex2f(50, 60)      # Vertice 2
        glVertex2f(50, 40)      # Vertice 3
        glVertex2f(-30, 40)     # Vertice 4
        glEnd()                 # Finaliza o desenho