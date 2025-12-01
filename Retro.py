# juego retro: avioncitos

# caracteristicas:
# -. Pantalla de Incio(Titulo, enter para comenzar y lista de 3 mayores higscore)
# -. Pantalla GameOver(Titulo, puntaje, high score, reintentar con 'ENTER' o salir'ESC')
# -. mover cañon con flechas
# -. disparar con espacio
# -. 3 vidas (pierde vida si un avion choca con el cañon, lo cual implica que los aviones deben intentar chocar con el cañon)
# -. 3 niveles (aunmenta velocidad de aviones)
# -. 10 pts por avion derribado
# -. fin del juego si se pierden las 3 vidas
# -. 10 aviones derribados para el siguiente nivel
# -. mostrar puntaje y vidas
# -.  high score (lista de 3 puntajes mas altos y sus nicknames, si logro un high score  mayor al maximo pedir nickname)
# - sonido de disparo y explosion
# -. musica de fondo(midi)
# -. el cañon debe moverse por el lateral izquierdo con las teclas ariba y abajo, y los aviones salen de la derecha

# multijugador(2 pantallas)

# juego retro: avioncitos (Modo Solo y Multijugador)

import random
import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def load_asset(name):
    return pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()

def asset_path(name):
    return os.path.join(ASSETS_DIR, name)

ANCHO = 1000
ALTO = 700
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 60, 60)
AZUL = (60, 60, 255)

HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscores.txt")

# ---------------- Highscores ----------------
def cargar_highscores():
    scores = []
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        name, s = line.split(",")
                        scores.append((name, int(s)))
                    except: continue
        except: return []
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:3]

def guardar_highscores(nickname, nuevo_score):
    scores = cargar_highscores()
    scores = [s for s in scores if s[0] != nickname]
    scores.append((nickname, int(nuevo_score)))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:3]
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            for name, sc in scores:
                f.write(f"{name},{sc}\n")
    except Exception as e:
        print("Error guardando highscores:", e)

def pedir_nickname(pantalla, fuente, small_font):
    nickname = ""
    scores_actuales = cargar_highscores()
    nombres_ocupados = [dato[0] for dato in scores_actuales]
    confirmando_reescritura = False

    while True:
        pantalla.fill(NEGRO)
        if confirmando_reescritura:
            aviso = fuente.render(f"¡'{nickname}' ya existe!", True, ROJO)
            pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, 150))
            pregunta = small_font.render("¿Quieres reescribir su puntaje?", True, BLANCO)
            pantalla.blit(pregunta, (ANCHO//2 - pregunta.get_width()//2, 220))
            opciones = small_font.render("S - SÍ (Guardar)   /   N - NO (Cambiar nombre)", True, BLANCO)
            pantalla.blit(opciones, (ANCHO//2 - opciones.get_width()//2, 300))
        else:
            texto = fuente.render("Nuevo High Score!", True, BLANCO)
            pantalla.blit(texto, (ANCHO//2 - texto.get_width()//2, 150))
            sub = small_font.render("Ingresa tu nickname:", True, BLANCO)
            pantalla.blit(sub, (ANCHO//2 - sub.get_width()//2, 220))
            nick_render = fuente.render(nickname, True, ROJO)
            pantalla.blit(nick_render, (ANCHO//2 - nick_render.get_width()//2, 300))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "Anon"
            if event.type == pygame.KEYDOWN:
                if confirmando_reescritura:
                    if event.key == pygame.K_s: return nickname
                    elif event.key == pygame.K_n:
                        confirmando_reescritura = False
                        nickname = ""
                else:
                    if event.key == pygame.K_RETURN:
                        nombre_limpio = nickname.strip() or "Anon"
                        if nombre_limpio in nombres_ocupados: confirmando_reescritura = True
                        else: return nombre_limpio
                    elif event.key == pygame.K_BACKSPACE: nickname = nickname[:-1]
                    else:
                        if len(nickname) < 12: nickname += event.unicode

# ============================================================
#                 CLASES
# ============================================================
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vida = 15  # Duración de la explosión en frames
        self.radio = 5
        self.color_centro = BLANCO

    def update(self):
        self.vida -= 1
        self.radio += 3  # La explosión crece
        
        # Efecto de cambio de color
        if self.vida > 10: self.color = BLANCO
        elif self.vida > 5: self.color = (255, 255, 0) # Amarillo
        else: self.color = ROJO

    def dibujar(self, pantalla):
        if self.vida > 0:
            pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(pantalla, self.color_centro, (int(self.x), int(self.y)), int(self.radio/2))

class EstadoJugador:
    def __init__(self, id_jugador):
        self.id = id_jugador
        self.vidas = 3
        self.puntaje = 0
        self.nivel = 1
        self.aviones_derribados = 0
        self.velocidad_enemigos = 1
        self.muerto = False

class Avion:
    def __init__(self, velocidad, sprite, min_y, max_y, target_idx):
        self.sprite = sprite
        self.width = 50
        self.height = sprite.get_height()
        self.x = ANCHO + 50
        self.y = random.randint(min_y, max_y - self.height)
        self.vel = velocidad
        self.target_idx = target_idx

    def mover(self, objetivo_y=None):
        self.x -= self.vel
        if objetivo_y is not None:
            velocidad_vertical = 0.3
            centro_avion = self.y + self.height / 2
            if centro_avion < objetivo_y - 2: self.y += velocidad_vertical
            elif centro_avion > objetivo_y + 2: self.y -= velocidad_vertical

    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bala:
    def __init__(self, x, y, sprite=None, owner_idx=0):
        self.sprite = sprite
        self.x = x
        self.y = y
        self.vel = 7
        self.owner_idx = owner_idx
        self.width = sprite.get_width() if sprite else 10
        self.height = sprite.get_height() if sprite else 4

    def mover(self):
        self.x += self.vel

    def dibujar(self, pantalla):
        if self.sprite: pantalla.blit(self.sprite, (self.x, self.y))
        else: pygame.draw.rect(pantalla, BLANCO, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Canon:
    def __init__(self, sprite, x_inicial, y_inicial, up_key, down_key, min_y, max_y):
        self.sprite = sprite
        self.width = sprite.get_width()
        self.height = sprite.get_height()
        self.x = x_inicial
        self.y = y_inicial
        self.vel = 5
        self.up_key = up_key
        self.down_key = down_key
        self.min_y = min_y
        self.max_y = max_y

    def mover(self, teclas):
        if teclas[self.up_key] and self.y > self.min_y: self.y -= self.vel
        if teclas[self.down_key] and self.y < self.max_y - self.height: self.y += self.vel

    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (self.x, self.y))

    def centro_disparo(self):
        return self.x + self.width, self.y + self.height // 2
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ============================================================
#             PANTALLAS DE GAME OVER (MODIFICADAS)
# ============================================================

def game_over(puntaje, top_scores, pantalla, fuente, small_font):
    while True:
        pantalla.fill(NEGRO)
        texto = fuente.render("GAME OVER", True, ROJO)
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 120))
        
        pantalla.blit(small_font.render(f"Puntaje Final: {puntaje}", True, BLANCO), (ANCHO // 2 - 100, 200))

        y = 270
        pantalla.blit(small_font.render("Highscores:", True, BLANCO), (ANCHO // 2 - 100, y))
        y += 40
        for idx, (name, sc) in enumerate(top_scores, start=1):
            linea = small_font.render(f"{idx}. {name} - {sc}", True, BLANCO)
            pantalla.blit(linea, (ANCHO//2 - linea.get_width()//2, y))
            y += 35

        # --- OPCIONES ---
        pantalla.blit(small_font.render("ENTER - Reintentar", True, BLANCO), (ANCHO // 2 - 140, 440))
        pantalla.blit(small_font.render("ESC - Menú Principal", True, BLANCO), (ANCHO // 2 - 140, 470))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return "salir_escritorio"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN: return "jugar"
                if evento.key == pygame.K_ESCAPE: return "menu"

def game_over_multi(mensaje_ganador, puntaje_ganador, top_scores, pantalla, fuente, small_font):
    while True:
        pantalla.fill(NEGRO)
        texto = fuente.render("FIN DEL JUEGO", True, ROJO)
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 100))
        
        ganador = fuente.render(mensaje_ganador, True, AZUL)
        pantalla.blit(ganador, (ANCHO // 2 - ganador.get_width() // 2, 180))

        # mostrar puntaje del ganador
        texto_pts = small_font.render(f"Puntaje Final: {puntaje_ganador}", True, BLANCO)
        pantalla.blit(texto_pts, (ANCHO // 2 - texto_pts.get_width() // 2, 210))

        # mostrar highsccore
        y = 270
        encabezado = small_font.render("Highscores:", True, BLANCO)
        pantalla.blit(encabezado, (ANCHO // 2 - encabezado.get_width() // 2, y))
        y += 40

        if not top_scores:
             nada = small_font.render("Aún no hay registros", True, BLANCO)
             pantalla.blit(nada, (ANCHO // 2 - nada.get_width() // 2, y))
        else:
            for idx, (name, sc) in enumerate(top_scores, start=1):
                linea = small_font.render(f"{idx}. {name} - {sc}", True, BLANCO)
                pantalla.blit(linea, (ANCHO//2 - linea.get_width()//2, y))
                y += 35

        # --- OPCIONES ---
        pantalla.blit(small_font.render("ENTER - Revancha", True, BLANCO), (ANCHO // 2 - 140, 400))
        pantalla.blit(small_font.render("ESC - Menú Principal", True, BLANCO), (ANCHO // 2 - 140, 450))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return "salir_escritorio"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN: return "jugar"
                if evento.key == pygame.K_ESCAPE: return "menu"

# ============================================================
#                     FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print(os.getcwd())
    pygame.init()
    try: pygame.mixer.init()
    except Exception: pass

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Avioncitos Retro")
    clock = pygame.time.Clock()

    img_canon = pygame.transform.scale(load_asset("canon.png"), (50, 30))
    img_avion = pygame.transform.scale(load_asset("jet.png"), (50, 47))

    sonido_disparo = None
    sonido_explosion = None
    try:
        if os.path.exists(asset_path("shoot.mp3")):
            sonido_disparo = pygame.mixer.Sound(asset_path("shoot.mp3"))
            sonido_disparo.set_volume(0.5)
        if os.path.exists(asset_path("explosion.mp3")):
            sonido_explosion = pygame.mixer.Sound(asset_path("explosion.mp3"))
            sonido_explosion.set_volume(0.5)
        ruta_musica = asset_path("musica.mp3") 
        if os.path.exists(ruta_musica):
            pygame.mixer.music.load(ruta_musica)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
    except Exception as e:
        print(f"Error cargando sonidos: {e}")

    fuente = pygame.font.SysFont("pixel", 40)
    small_font = pygame.font.SysFont("pixel", 28)
    
    # ------------------ BUCLE DEL MENÚ ------------------
    while True:
        def pantalla_inicio():
            top_scores = cargar_highscores()
            while True:
                pantalla.fill(NEGRO)
                titulo = fuente.render("AVIONCITOS RETRO", True, BLANCO)
                txt_solo = small_font.render("ENTER - 1 Jugador", True, BLANCO)
                txt_multi = small_font.render("M - 2 Jugadores (Co-op)", True, AZUL)
                txt_salir = small_font.render("ESC - Salir", True, BLANCO)

                pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 100))
                pantalla.blit(txt_solo, (ANCHO // 2 - txt_solo.get_width() // 2, 180))
                pantalla.blit(txt_multi, (ANCHO // 2 - txt_multi.get_width() // 2, 220))
                pantalla.blit(txt_salir, (ANCHO // 2 - txt_salir.get_width() // 2, 500))

                encabezado = small_font.render("Highscores:", True, BLANCO)
                pantalla.blit(encabezado, (ANCHO // 2 - encabezado.get_width() // 2, 300))
                if not top_scores:
                    nada = small_font.render("Aún no hay registros", True, BLANCO)
                    pantalla.blit(nada, (ANCHO // 2 - nada.get_width() // 2, 260))
                else:
                    y = 340
                    for idx, (name, sc) in enumerate(top_scores, start=1):
                        linea = small_font.render(f"{idx}. {name} - {sc}", True, BLANCO)
                        pantalla.blit(linea, (ANCHO//2 - linea.get_width()//2, y))
                        y += 36

                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return None
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN: return "solo"
                        if event.key == pygame.K_m: return "multi"
                        if event.key == pygame.K_ESCAPE: return None

        modo_juego = pantalla_inicio()
        if not modo_juego: return # Salir del programa si ESC en menú

        # ------------------ BUCLE DE PARTIDA (Reintentos) ------------------
        regresar_al_menu = False
        
        while not regresar_al_menu:
            # Reiniciar variables
            MITAD_ALTO = ALTO // 2
            stats = [EstadoJugador(0), EstadoJugador(1)]
            canones = []
            limite_p1_y = ALTO if modo_juego == "solo" else MITAD_ALTO
            p1 = Canon(img_canon, 0, ALTO // 2 -50, pygame.K_UP, pygame.K_DOWN, 0, limite_p1_y)
            canones.append(p1)
            if modo_juego == "multi":
                p2 = Canon(img_canon, 0, MITAD_ALTO + (MITAD_ALTO // 2) -50, pygame.K_w, pygame.K_s, MITAD_ALTO, ALTO)
                canones.append(p2)
            else: stats[1].muerto = True

            explosiones = []
            balas = []
            aviones = []
            top_scores = cargar_highscores()

            ejecutando = True
            
            # ------------------ BUCLE DE FRAMES (Juego Activo) ------------------
            while ejecutando:
                clock.tick(60)
                teclas = pygame.key.get_pressed()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return # Cierre total

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and not stats[0].muerto:
                            x, y = canones[0].centro_disparo()
                            balas.append(Bala(x, y, owner_idx=0))
                            if sonido_disparo: sonido_disparo.play()
                        if modo_juego == "multi" and event.key == pygame.K_LCTRL and not stats[1].muerto:
                            x, y = canones[1].centro_disparo()
                            balas.append(Bala(x, y, owner_idx=1))
                            if sonido_disparo: sonido_disparo.play()

                # Mover cañones
                if not stats[0].muerto: canones[0].mover(teclas)
                if modo_juego == "multi" and not stats[1].muerto: canones[1].mover(teclas)

                # Generar aviones P1
                aviones_p1 = [a for a in aviones if a.target_idx == 0]
                if not stats[0].muerto and len(aviones_p1) < stats[0].nivel + 2:
                    limite_y = ALTO if modo_juego == "solo" else MITAD_ALTO
                    aviones.append(Avion(stats[0].velocidad_enemigos, img_avion, 0, limite_y, 0))

                # Generar aviones P2
                if modo_juego == "multi" and not stats[1].muerto:
                    aviones_p2 = [a for a in aviones if a.target_idx == 1]
                    if len(aviones_p2) < stats[1].nivel + 2:
                        aviones.append(Avion(stats[1].velocidad_enemigos, img_avion, MITAD_ALTO, ALTO, 1))

                # Actualizar aviones
                for avion in aviones[:]:
                    idx = avion.target_idx
                    if stats[idx].muerto:
                        avion.x -= 8
                        if avion.x < -100: aviones.remove(avion)
                        continue

                    canon_obj = canones[idx]
                    avion.mover(canon_obj.y + canon_obj.height / 2)
                    rect_avion = avion.get_rect()

                    destruido = False
                    for bala in balas[:]:
                        if bala.owner_idx == idx and rect_avion.colliderect(bala.get_rect()):
                            stats[idx].puntaje += 10
                            stats[idx].aviones_derribados += 1
                            if stats[idx].aviones_derribados >= 10:
                                stats[idx].nivel += 1
                                stats[idx].velocidad_enemigos += 0.5
                                stats[idx].aviones_derribados = 0
                                if stats[idx].nivel > 3: stats[idx].nivel = 3
                            aviones.remove(avion)
                            balas.remove(bala)
                            explosiones.append(Explosion(avion.x + avion.width//2, avion.y + avion.height//2))
                            if sonido_explosion: sonido_explosion.play()
                            destruido = True
                            break
                    
                    if destruido: continue

                    if rect_avion.colliderect(canon_obj.get_rect()):
                        stats[idx].vidas -= 1
                        aviones.remove(avion)
                        explosiones.append(Explosion(canon_obj.x + canon_obj.width//2, canon_obj.y + canon_obj.height//2))
                        if sonido_explosion: sonido_explosion.play()
                        if stats[idx].vidas <= 0: stats[idx].muerto = True
                        continue

                    if avion.x < -50:
                        aviones.remove(avion) # Escapó

                for bala in balas[:]:
                    bala.mover()
                    if bala.x > ANCHO + 20: balas.remove(bala)

                # ---------------- GAME OVER CHECK ----------------
                accion_final = None
                
                if modo_juego == "solo":
                    if stats[0].muerto:
                        highscore_logrado = False
                        if not top_scores or len(top_scores) < 1 or stats[0].puntaje > top_scores[0][1]:
                            nick = pedir_nickname(pantalla, fuente, small_font)
                            guardar_highscores(nick, stats[0].puntaje)
                            top_scores = cargar_highscores()
                        
                        accion_final = game_over(stats[0].puntaje, top_scores, pantalla, fuente, small_font)

                else: # Multi
                    if stats[0].muerto and stats[1].muerto:
                        # Determinar ganador
                        ganador_txt = "¡EMPATE!"
                        puntaje_ganador = stats[0].puntaje

                        if stats[0].puntaje > stats[1].puntaje:
                            ganador_txt = "¡JUGADOR 1 GANA!"
                            puntaje_ganador = stats[0].puntaje
                        elif stats[1].puntaje > stats[0].puntaje:
                            ganador_txt = "¡JUGADOR 2 GANA!"
                            puntaje_ganador = stats[1].puntaje
                        
                        accion_final = game_over_multi(ganador_txt, puntaje_ganador, top_scores, pantalla, fuente, small_font)

                # Manejar acción post-juego
                if accion_final:
                    if accion_final == "jugar":
                        ejecutando = False # Repetir 'while not regresar_al_menu'
                    elif accion_final == "menu":
                        ejecutando = False
                        regresar_al_menu = True # Romper 'while not regresar_al_menu' -> ir a 'while True' (menú)
                    elif accion_final == "salir_escritorio":
                        pygame.quit()
                        return

                # ---------------- DIBUJO ----------------
                pantalla.fill(NEGRO)
                if modo_juego == "multi":
                    pygame.draw.line(pantalla, BLANCO, (0, MITAD_ALTO), (ANCHO, MITAD_ALTO), 5)

                if not stats[0].muerto: canones[0].dibujar(pantalla)
                else: pantalla.blit(small_font.render("P1 ELIMINADO", True, ROJO), (100, ALTO//4))

                if modo_juego == "multi":
                    if not stats[1].muerto: canones[1].dibujar(pantalla)
                    else: pantalla.blit(small_font.render("P2 ELIMINADO", True, ROJO), (100, 3*ALTO//4))

                for b in balas: b.dibujar(pantalla)
                for a in aviones: a.dibujar(pantalla)

                info_p1 = f"P1 | Pts: {stats[0].puntaje} | Vida: {stats[0].vidas} | Nvl: {stats[0].nivel}"
                pantalla.blit(small_font.render(info_p1, True, BLANCO), (10, 10))
                if modo_juego == "multi":
                    info_p2 = f"P2 | Pts: {stats[1].puntaje} | Vida: {stats[1].vidas} | Nvl: {stats[1].nivel}"
                    pantalla.blit(small_font.render(info_p2, True, AZUL), (10, MITAD_ALTO + 10))

                for exp in explosiones[:]:
                    exp.update()
                    exp.dibujar(pantalla)
                    if exp.vida <= 0:
                        explosiones.remove(exp)

                pygame.display.update()

if __name__ == "__main__":
    main()