import pygame
import random

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIS = (100, 100, 100)
MARRON = (139, 69, 19)

# Cargar sonidos
sonido_disparo = pygame.mixer.Sound("disparo.mp3")
sonido_gano = pygame.mixer.Sound("gano.mp3")
sonido_intro = pygame.mixer.Sound("intro.mp3")
sonido_perdio = pygame.mixer.Sound("perdio.mp3")
sonido_tanque = pygame.mixer.Sound("tanque.mp3")

# Crear la ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tank 2025 - Remake")
reloj = pygame.time.Clock()

# Cargar sonidos en la ventana correspondiente
# Función para manejar sonidos
def cargar_sonido(pista):
    pygame.mixer.stop()  # Detiene todos los sonidos antes de reproducir uno nuevo
    if pista == "intro":
        sonido_intro.play(-1)  # Reproducir en bucle
    elif pista == "tanque":
        sonido_tanque.play(-1)  # Reproducir en bucle durante el juego
        sonido_tanque.set_volume(0.07)
    elif pista == "disparo":
        sonido_disparo.play()
        sonido_tanque.play(-1)  # Reproducir en bucle durante el juego
        sonido_tanque.set_volume(0.07)
    elif pista == "gano":
        sonido_gano.play()
    elif pista == "perdio":
        sonido_perdio.play()

# Cargar imágenes o crearlas
def crear_imagen_tanque(color, tamaño):
    """Crear imagen para el tanque"""
    imagen = pygame.Surface((tamaño, tamaño))
    imagen.fill(NEGRO)
    imagen.set_colorkey(NEGRO)
    cargar_sonido("tanque")
    
    # Cuerpo del tanque
    pygame.draw.rect(imagen, color, (tamaño//4, tamaño//4, tamaño//2, tamaño//2))
    
    # Cañón del tanque
    pygame.draw.rect(imagen, color, (tamaño//2 - tamaño//8, 0, tamaño//4, tamaño//2))
    
    # Orugas del tanque
    pygame.draw.rect(imagen, GRIS, (0, tamaño//8, tamaño//8, tamaño*3//4))
    pygame.draw.rect(imagen, GRIS, (tamaño*7//8, tamaño//8, tamaño//8, tamaño*3//4))
    
    return imagen

def crear_imagen_bloque(color, tamaño):
    """Crear imagen para un bloque"""
    imagen = pygame.Surface((tamaño, tamaño))
    imagen.fill(color)
    return imagen

def crear_imagen_bala(tamaño):
    """Crear imagen para la bala"""
    imagen = pygame.Surface((tamaño, tamaño))
    imagen.fill(NEGRO)
    imagen.set_colorkey(NEGRO)
    pygame.draw.circle(imagen, ROJO, (tamaño//2, tamaño//2), tamaño//2)
    return imagen

# Clase para el jugador (tanque)
class Tanque(pygame.sprite.Sprite):
    def __init__(self, x, y, es_jugador=True):
        super().__init__()
        self.tamaño = 30
        self.es_jugador = es_jugador
        self.direccion = "arriba"
        
        if es_jugador:
            self.color = VERDE
            self.velocidad = 2
        else:
            self.color = ROJO
            self.velocidad = 2
            
        self.imagen_original = crear_imagen_tanque(self.color, self.tamaño)
        self.image = self.imagen_original
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ultimo_disparo = pygame.time.get_ticks()
        self.tiempo_entre_disparos = 500  # milisegundos
        self.vida = 3 if es_jugador else 1
        
    def update(self, teclas, bloques, tanques, balas_enemigos=None, jugador=None, todos_sprites=None):
        movimiento_x = 0
        movimiento_y = 0
        
        if self.es_jugador:
            # Controles del jugador
            if teclas[pygame.K_LEFT]:
                self.direccion = "izquierda"
                movimiento_x = -self.velocidad
            elif teclas[pygame.K_RIGHT]:
                self.direccion = "derecha"
                movimiento_x = self.velocidad
            elif teclas[pygame.K_UP]:
                self.direccion = "arriba"
                movimiento_y = -self.velocidad
            elif teclas[pygame.K_DOWN]:
                self.direccion = "abajo"
                movimiento_y = self.velocidad
        else:
            # IA para los enemigos
            if random.randint(0, 100) < 2:  # 3% de probabilidad de cambiar dirección
                direcciones = ["izquierda", "derecha", "arriba", "abajo"]
                self.direccion = random.choice(direcciones)
            
            if self.direccion == "izquierda":
                movimiento_x = -self.velocidad
            elif self.direccion == "derecha":
                movimiento_x = self.velocidad
            elif self.direccion == "arriba":
                movimiento_y = -self.velocidad
            elif self.direccion == "abajo":
                movimiento_y = self.velocidad
            
            if jugador:
                # Verificar si el jugador está en la línea de visión
                if self.en_linea_de_vision(jugador, bloques):
                    # Calcular la dirección hacia el jugador
                    dx = jugador.rect.centerx - self.rect.centerx
                    dy = jugador.rect.centery - self.rect.centery
                    
                    if abs(dx) > abs(dy):
                        self.direccion = "derecha" if dx > 0 else "izquierda"
                    else:
                        self.direccion = "abajo" if dy > 0 else "arriba"
                    
                    # Disparar si ha pasado el tiempo suficiente
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - self.ultimo_disparo > self.tiempo_entre_disparos:
                        bala = self.disparar()
                        balas_enemigos.add(bala)
                        todos_sprites.add(bala)  # Añadir al grupo de todos los sprites
                        self.ultimo_disparo = tiempo_actual
        
        # Rotar imagen según dirección
        if self.direccion == "izquierda":
            self.image = pygame.transform.rotate(self.imagen_original, 90)
        elif self.direccion == "derecha":
            self.image = pygame.transform.rotate(self.imagen_original, -90)
        elif self.direccion == "arriba":
            self.image = self.imagen_original
        elif self.direccion == "abajo":
            self.image = pygame.transform.rotate(self.imagen_original, 180)
        
        # Actualizar posición con colisiones
        rect_original = self.rect.copy()
        
        self.rect.x += movimiento_x
        self.rect.y += movimiento_y
        
        # Comprobar límites de pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO:
            self.rect.right = ANCHO
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTO:
            self.rect.bottom = ALTO
        
        # Comprobar colisiones con bloques
        for bloque in bloques:
            if self.rect.colliderect(bloque.rect):
                self.rect = rect_original
                
        # Comprobar colisiones con otros tanques
        for tanque in tanques:
            if tanque != self and self.rect.colliderect(tanque.rect):
                self.rect = rect_original
    
    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.centery, self.direccion, self.es_jugador)
        cargar_sonido("disparo")
        return bala
    
    def recibir_daño(self):
        self.vida -= 1
        return self.vida <= 0
    
    def en_linea_de_vision(self, jugador, bloques):
        """Verifica si el jugador está en la línea de visión del enemigo."""
        # Crear una línea recta entre el enemigo y el jugador
        linea = pygame.draw.line(pantalla, ROJO, self.rect.center, jugador.rect.center, 1)
        
        # Verificar colisiones con bloques
        for bloque in bloques:
            if linea.colliderect(bloque.rect):
                return False  # Hay un bloque en el camino
        return True  # No hay obstáculos

# Clase para las balas
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion, es_jugador):
        super().__init__()
        self.tamaño = 10
        self.velocidad = 5
        self.direccion = direccion
        self.es_jugador = es_jugador
        self.image = crear_imagen_bala(self.tamaño)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
    def update(self):
        if self.direccion == "izquierda":
            self.rect.x -= self.velocidad
        elif self.direccion == "derecha":
            self.rect.x += self.velocidad
        elif self.direccion == "arriba":
            self.rect.y -= self.velocidad
        elif self.direccion == "abajo":
            self.rect.y += self.velocidad
            
        # Eliminar si sale de la pantalla
        if (self.rect.right < 0 or self.rect.left > ANCHO or 
            self.rect.bottom < 0 or self.rect.top > ALTO):
            self.kill()

# Clase para los bloques (obstáculos)
class Bloque(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.tamaño = 40
        self.tipo = tipo
        
        if tipo == "ladrillo":
            self.color = MARRON
            self.destructible = True
        else:  # tipo == "acero"
            self.color = GRIS
            self.destructible = False
            
        self.image = crear_imagen_bloque(self.color, self.tamaño)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Clase para la base a defender
class Base(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.tamaño = 60
        self.image = pygame.Surface((self.tamaño, self.tamaño))
        self.image.fill(NEGRO)
        
        # Dibujar la bandera
        pygame.draw.rect(self.image, ROJO, (self.tamaño//4, self.tamaño//4, self.tamaño//2, self.tamaño//2))
        pygame.draw.rect(self.image, BLANCO, (self.tamaño//3, self.tamaño//3, self.tamaño//6, self.tamaño//6))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Función para crear nivel
def crear_nivel(nivel):
    bloques = pygame.sprite.Group()
    
    # Nivel 1: patrón simple
    if nivel == 1:
        # Crear bloques horizontales
        for i in range(0, ANCHO, 80):
            y = 150
            bloque = Bloque(i, y, "ladrillo")
            bloques.add(bloque)
            
        # Crear bloques verticales
        for i in range(200, ALTO, 80):
            x1 = 200
            x2 = 600
            bloque1 = Bloque(x1, i, "ladrillo")
            bloque2 = Bloque(x2, i, "ladrillo")
            bloques.add(bloque1, bloque2)
            
        # Añadir algunos bloques de acero
        posiciones_acero = [(100, 300), (300, 400), (500, 300), (700, 400)]
        for pos in posiciones_acero:
            bloque = Bloque(pos[0], pos[1], "acero")
            bloques.add(bloque)
    
    # Nivel 2: más complejo
    elif nivel == 2:
        # Crear mapa con caminos libres garantizados
        mapa = []
        for i in range(15):  # Filas
            fila = []
            for j in range(20):  # Columnas
                # Dejar espacio para el jugador y la base en la parte inferior
                if (i >= 10 and j >= 8 and j <= 11) or (i == 14 and j >= 7 and j <= 12):
                    fila.append(0)  # Espacio libre
                # Crear caminos garantizados
                elif i % 3 == 0 or j % 4 == 0:
                    fila.append(0)  # Camino libre
                else:
                    # 60% de probabilidad de bloque, 40% de espacio libre
                    if random.random() < 0.6:
                        fila.append(random.choice([1, 2]))  # 1=ladrillo, 2=acero
                    else:
                        fila.append(0)  # Espacio libre
            mapa.append(fila)
        
        # Convertir el mapa a bloques
        for i in range(len(mapa)):
            for j in range(len(mapa[i])):
                if mapa[i][j] == 1:  # Ladrillo
                    bloque = Bloque(j * 40, i * 40, "ladrillo")
                    bloques.add(bloque)
                elif mapa[i][j] == 2:  # Acero
                    bloque = Bloque(j * 40, i * 40, "acero")
                    bloques.add(bloque)
    
    return bloques

# Función para mostrar texto
def dibujar_texto(superficie, texto, tamaño, x, y, color=BLANCO):
    fuente = pygame.font.SysFont("Arial", tamaño)
    texto_superficie = fuente.render(texto, True, color)
    texto_rect = texto_superficie.get_rect()
    texto_rect.midtop = (x, y)
    superficie.blit(texto_superficie, texto_rect)

# Función para la pantalla de inicio
def mostrar_menu_inicio():
    pantalla.fill(NEGRO)
    dibujar_texto(pantalla, "TANK 2025 REMAKE", 64, ANCHO // 2, ALTO // 4)
    dibujar_texto(pantalla, "Flechas para moverse, Espacio para disparar", 22, ANCHO // 2, ALTO // 2)
    dibujar_texto(pantalla, "Presiona una tecla para comenzar", 18, ANCHO // 2, ALTO * 3/4)
    pygame.display.flip()
    cargar_sonido("intro")
    esperando = True
    while esperando:
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                
                pygame.quit()
                return False
            if evento.type == pygame.KEYUP:
                esperando = False
                return True

# Función para la pantalla de game over
def mostrar_game_over(victoria):
    pantalla.fill(NEGRO)
    if victoria:
        dibujar_texto(pantalla, "¡VICTORIA!", 64, ANCHO // 2, ALTO // 4, VERDE)
        cargar_sonido("gano")
    else:
        dibujar_texto(pantalla, "GAME OVER", 64, ANCHO // 2, ALTO // 4, ROJO)
        cargar_sonido("perdio")
    
    dibujar_texto(pantalla, "Presiona R para reiniciar o Q para salir", 22, ANCHO // 2, ALTO // 2)
    pygame.display.flip()
    
    esperando = True
    while esperando:
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return "salir"
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_r:
                    return "reiniciar"
                elif evento.key == pygame.K_q:
                    return "salir"

# Función para mostrar la pantalla de selección de nivel
def mostrar_seleccion_nivel():
    pantalla.fill(NEGRO)
    cargar_sonido("intro")
    dibujar_texto(pantalla, "SELECCIONA NIVEL", 64, ANCHO // 2, ALTO // 4)
    dibujar_texto(pantalla, "1 - Nivel 1 (Fácil)", 22, ANCHO // 2, ALTO // 2 - 30)
    dibujar_texto(pantalla, "2 - Nivel 2 (Difícil)", 22, ANCHO // 2, ALTO // 2 + 30)
    pygame.display.flip()
    
    esperando = True
    while esperando:
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return 0
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_1:
                    return 1
                elif evento.key == pygame.K_2:
                    return 2

# Función para mostrar información de juego
def mostrar_info(pantalla, vidas, enemigos_restantes, nivel):
    dibujar_texto(pantalla, f"Vidas: {vidas}", 20, 70, 10)
    dibujar_texto(pantalla, f"Enemigos: {enemigos_restantes}", 20, 220, 10)
    dibujar_texto(pantalla, f"Nivel: {nivel}", 20, 350, 10)

# Función principal del juego
def juego():
    # Variables de juego
    ejecutando = True
    
    # Mostrar pantalla de inicio
    if not mostrar_menu_inicio():
        return
    
    while ejecutando:
        # Seleccionar nivel
        nivel = mostrar_seleccion_nivel()
        if nivel == 0:
            break
            
        # Crear sprites
        jugador = Tanque(ANCHO // 2, ALTO - 100, True)
        todos_sprites = pygame.sprite.Group()
        todos_sprites.add(jugador)
        
        base = Base(ANCHO // 2 - 30, ALTO - 80)
        todos_sprites.add(base)
        
        bloques = crear_nivel(nivel)
        todos_sprites.add(bloques)
        
        # Crear enemigos según el nivel
        enemigos = pygame.sprite.Group()
        num_enemigos = 5 if nivel == 1 else 8
        
        for i in range(num_enemigos):
            # Asegurar que los enemigos no aparezcan encima del jugador, la base ni ningún bloque
            while True:
                x = random.randint(50, ANCHO - 50)
                y = random.randint(50, 150)
                
                # Crear un rectángulo temporal para el enemigo
                rect_temp = pygame.Rect(x, y, 40, 40)
                
                # Verificar que no colisione con el jugador, la base ni ningún bloque
                colision = False
                if rect_temp.colliderect(jugador.rect) or rect_temp.colliderect(base.rect):
                    colision = True
                else:
                    for bloque in bloques:
                        if rect_temp.colliderect(bloque.rect):
                            colision = True
                            break
                # Verificar colisión con otros enemigos
                for enemigo_existente in enemigos:
                    if rect_temp.colliderect(enemigo_existente.rect):
                        colision = True
                        break
                
                # Si no hay colisión, crear el enemigo
                if not colision:
                    enemigo = Tanque(x, y, False)
                    enemigos.add(enemigo)
                    todos_sprites.add(enemigo)
                    break
            
        balas_jugador = pygame.sprite.Group()
        balas_enemigos = pygame.sprite.Group()
        
        # Bucle principal del juego
        jugando = True
        while jugando:
            reloj.tick(FPS)
            
            # Procesar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    jugando = False
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        tiempo_actual = pygame.time.get_ticks()
                        if tiempo_actual - jugador.ultimo_disparo > jugador.tiempo_entre_disparos:
                            bala = jugador.disparar()
                            balas_jugador.add(bala)
                            todos_sprites.add(bala)
                            jugador.ultimo_disparo = tiempo_actual
                    
                    elif evento.key == pygame.K_ESCAPE:
                        jugando = False
            
            # Actualizar
            teclas = pygame.key.get_pressed()
            jugador.update(teclas, bloques, enemigos)
            
            for enemigo in enemigos:
                enemigo.update(teclas, bloques, enemigos, balas_enemigos, jugador, todos_sprites)
            
            balas_jugador.update()
            balas_enemigos.update()
            
            # Detectar colisiones bala-bloque
            for bala in balas_jugador:
                bloque_golpeado = pygame.sprite.spritecollideany(bala, bloques)
                if bloque_golpeado:
                    bala.kill()
                    if bloque_golpeado.destructible:
                        bloque_golpeado.kill()
            
            for bala in balas_enemigos:
                bloque_golpeado = pygame.sprite.spritecollideany(bala, bloques)
                if bloque_golpeado:
                    bala.kill()
                    if bloque_golpeado.destructible:
                        bloque_golpeado.kill()
            
            # Detectar colisiones bala-tanque
            for bala in balas_jugador:
                enemigo_golpeado = pygame.sprite.spritecollideany(bala, enemigos)
                if enemigo_golpeado:
                    bala.kill()
                    if enemigo_golpeado.recibir_daño():
                        enemigo_golpeado.kill()
            
            for bala in balas_enemigos:
                if pygame.sprite.collide_rect(bala, jugador):
                    bala.kill()
                    if jugador.recibir_daño():
                        jugando = False
                        resultado = mostrar_game_over(False)
                        if resultado == "salir":
                            ejecutando = False
                        break
            
            # Detectar colisiones bala-base
            for bala in balas_enemigos:
                if pygame.sprite.collide_rect(bala, base):
                    bala.kill()
                    jugando = False
                    resultado = mostrar_game_over(False)
                    if resultado == "salir":
                        ejecutando = False
                    break
            
            # Comprobar victoria (todos los enemigos eliminados)
            if not enemigos:
                jugando = False
                resultado = mostrar_game_over(True)
                if resultado == "salir":
                    ejecutando = False
            
            # Dibujar
            pantalla.fill(NEGRO)
            todos_sprites.draw(pantalla)
            mostrar_info(pantalla, jugador.vida, len(enemigos), nivel)
            pygame.display.flip()
    
    pygame.quit()

# Ejecutar el juego
if __name__ == "__main__":
    juego()