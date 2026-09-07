import tkinter as tk
import random
import math
import time
import sys
import tempfile
import wave
import struct
from pathlib import Path

# ============================================================
# JUEGO DE LA VIBORITA — UNNECESSARY PROJECT #001
# ============================================================

# ------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------

TAMANO_CELDA = 20

COLUMNAS_INICIALES = 30
FILAS_INICIALES = 30

COLUMNAS_MINIMAS = 8
FILAS_MINIMAS = 8

VELOCIDAD_JUEGO_MS = 105
ALTURA_HUD = 108

TIEMPO_DERROTA_MS = 2500
DURACION_ENCOGIMIENTO_MS = 800
INTERVALO_RENDER_MS = 20

INTRO_MINIMO_MS = 900
VENTANA_COMBO_SEGUNDOS = 1.65
MAX_COLA_ENTRADAS = 2

# ------------------------------------------------------------
# PALETA
# ------------------------------------------------------------

FONDO_SUPERIOR = "#070910"
FONDO_INFERIOR = "#170d1c"

FONDO_HUD = "#080a10"

CUADRICULA_MENOR = "#171a24"
CUADRICULA_MAYOR = "#252a38"

BLANCO = "#f7f8ff"
TEXTO_SECUNDARIO = "#81879a"
TEXTO_TENUE = "#545a6c"

VERDE = "#73ff8c"
VERDE_CABEZA = "#baffc4"
BRILLO_VERDE_1 = "#285f39"
BRILLO_VERDE_2 = "#102b19"

CIAN = "#55dfff"
MAGENTA = "#ff45c8"

ROJO = "#ff3d61"
ROJO_OSCURO = "#65172a"
BRILLO_ROJO = "#2d0d18"

NARANJA = "#ff914d"
DORADO = "#ffd166"

ROJO_MANZANA = "#ff4262"
ROJO_MANZANA_OSCURO = "#b91f3e"
VERDE_HOJA = "#63e878"

NEGRO = "#050507"

# ------------------------------------------------------------
# BURLAS
# ------------------------------------------------------------

BURLAS_SUAVES = [
    "¿Eso fue todo?",
    "Bueno... todos empezamos por algún lado.",
    "Tranqui, todavía puedes fingir que fue lag.",
    "La viborita confiaba en ti.",
    "Primera advertencia: las paredes hacen daño.",
    "No pasa nada... todavía.",
    "Fue calentamiento, ¿verdad?",
    "Te doy otra oportunidad. No la desperdicies.",
]

BURLAS_MEDIAS = [
    "¿Otra vez?",
    "La viborita empieza a sospechar de ti.",
    "Te estoy quitando espacio y tú cooperas.",
    "¿Seguro que conoces las flechas del teclado?",
    "Empiezo a pensar que el problema no era el tablero.",
    "No quiero decir que seas malo... pero tengo evidencia.",
    "Ese muro llevaba ahí toda la partida.",
    "La manzana está empezando a sentirse bastante segura.",
    "¿Quieres que te marque dónde NO chocar?",
    "Curiosa estrategia.",
]

BURLAS_DURAS = [
    "El tablero se hizo más pequeño. Igual que tus posibilidades.",
    "Estoy empezando a sentir pena por la viborita.",
    "Hermano...",
    "Ya no sé cómo ayudarte.",
    "Te juro que el juego sí funciona.",
    "La viborita merece otro jugador.",
    "¿Otra derrota? Qué inesperado.",
    "Tu estrategia parece ser eliminar el tablero.",
    "A este punto yo también estoy nervioso.",
    "Cada vez tienes menos espacio y sigues encontrando la pared.",
    "Debo admitirlo: eres consistente.",
]

BURLAS_BRUTALES = [
    "El problema definitivamente ya no es el tablero.",
    "¿Quieres que juegue yo?",
    "Esto ya empieza a ser personal.",
    "A este ritmo terminamos jugando en un píxel.",
    "La viborita está redactando su carta de renuncia.",
    "No sabía que perder podía convertirse en una habilidad.",
    "Estamos presenciando historia. Mala, pero historia.",
    "Tengo malas noticias: todavía quedan paredes.",
    "La inteligencia artificial no era necesaria para ganarte.",
    "Yo también fingiría que esto es parte del video.",
    "La manzana tiene más posibilidades de sobrevivir que tú.",
    "¿Cobras por demostración o esto es gratis?",
]

BURLAS_FINALES = [
    "Ya casi no queda tablero. Impresionante.",
    "Has convertido la Viborita en un juego de interiores.",
    "¿Cómo sigues encontrando maneras de perder?",
    "Tu enemigo natural es cualquier superficie sólida.",
    "El tablero está pidiendo misericordia.",
    "Lo único que estás completando es mi colección de derrotas.",
    "Ni reduciendo el mapa logro reducir tus errores.",
    "Esto dejó de ser la Viborita y se convirtió en una investigación.",
    "Voy a necesitar documentar este comportamiento.",
    "A este punto la viborita ya sabe cómo termina esto.",
    "No queda espacio, pero de alguna manera sí quedan errores.",
    "La ciencia debería estudiar esto.",
]


# ============================================================
# UTILIDADES
# ============================================================

def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


def interpolar(inicio, fin, proporcion):
    return inicio + (fin - inicio) * proporcion


def hex_a_rgb(color):
    color = color.lstrip("#")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )


def rgb_a_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        limitar(int(rgb[0]), 0, 255),
        limitar(int(rgb[1]), 0, 255),
        limitar(int(rgb[2]), 0, 255),
    )


def mezclar_color(color_origen, color_destino, proporcion):
    proporcion = limitar(proporcion, 0, 1)
    origen = hex_a_rgb(color_origen)
    destino = hex_a_rgb(color_destino)

    return rgb_a_hex((
        interpolar(origen[0], destino[0], proporcion),
        interpolar(origen[1], destino[1], proporcion),
        interpolar(origen[2], destino[2], proporcion),
    ))


def suavizado_cubico(proporcion):
    if proporcion < 0.5:
        return 4 * proporcion * proporcion * proporcion
    return 1 - pow(-2 * proporcion + 2, 3) / 2


# ============================================================
# AUDIO PROCEDURAL — SIN ASSETS EXTERNOS
# ============================================================

class AudioProcedural:
    """
    Genera pequeños WAV en la carpeta temporal del sistema.
    No requiere archivos de audio incluidos en el repo.

    En Windows usa winsound de la librería estándar.
    En otras plataformas simplemente queda en silencio.
    """

    FRECUENCIA_MUESTREO = 22050

    def __init__(self):
        self.habilitado = sys.platform.startswith("win")
        self.carpeta_temporal = None
        self.sonidos = {}

        if not self.habilitado:
            return

        try:
            import winsound
            self.winsound = winsound

            self.carpeta_temporal = Path(
                tempfile.mkdtemp(prefix="juego_viborita_audio_")
            )

            self._crear_sonidos()

        except Exception:
            self.habilitado = False

    def _escribir_wave(self, nombre, duracion, generador):
        ruta = self.carpeta_temporal / f"{nombre}.wav"
        total_muestras = max(
            1,
            int(duracion * self.FRECUENCIA_MUESTREO)
        )

        with wave.open(str(ruta), "w") as archivo_wave:
            archivo_wave.setnchannels(1)
            archivo_wave.setsampwidth(2)
            archivo_wave.setframerate(self.FRECUENCIA_MUESTREO)

            datos = bytearray()

            for indice in range(total_muestras):
                tiempo = indice / self.FRECUENCIA_MUESTREO
                muestra = limitar(
                    generador(tiempo, duracion),
                    -1.0,
                    1.0
                )
                datos.extend(
                    struct.pack(
                        "<h",
                        int(muestra * 32767)
                    )
                )

            archivo_wave.writeframes(datos)

        self.sonidos[nombre] = str(ruta)

    @staticmethod
    def _envolvente(
        tiempo,
        duracion,
        ataque=0.02,
        liberacion=0.12
    ):
        if tiempo < ataque:
            return tiempo / max(ataque, 1e-6)

        if tiempo > duracion - liberacion:
            return max(
                0.0,
                (duracion - tiempo)
                / max(liberacion, 1e-6)
            )

        return 1.0

    def _crear_sonidos(self):
        # Comer: chirrido ascendente corto.
        def comer(tiempo, duracion):
            frecuencia = (
                620
                + 620 * (tiempo / duracion)
            )
            envolvente = self._envolvente(
                tiempo,
                duracion,
                0.008,
                0.07
            )
            return (
                math.sin(
                    math.tau
                    * frecuencia
                    * tiempo
                )
                * envolvente
                * 0.34
            )

        # Combo: más brillante/agudo.
        def combo(tiempo, duracion):
            frecuencia = (
                900
                + 1100 * (tiempo / duracion)
            )
            envolvente = self._envolvente(
                tiempo,
                duracion,
                0.005,
                0.08
            )
            portadora = math.sin(
                math.tau
                * frecuencia
                * tiempo
            )
            armonico = (
                math.sin(
                    math.tau
                    * frecuencia
                    * 2
                    * tiempo
                )
                * 0.25
            )
            return (
                (portadora + armonico)
                * envolvente
                * 0.26
            )

        # Derrota: caída de frecuencia con distorsión ligera.
        def derrota(tiempo, duracion):
            progreso = tiempo / duracion
            frecuencia = (
                260
                - 180 * progreso
            )
            envolvente = self._envolvente(
                tiempo,
                duracion,
                0.005,
                0.20
            )
            onda = (
                math.sin(
                    math.tau
                    * frecuencia
                    * tiempo
                )
                + 0.38
                * math.sin(
                    math.tau
                    * frecuencia
                    * 0.5
                    * tiempo
                )
            )
            return (
                math.tanh(onda * 1.8)
                * envolvente
                * 0.38
            )

        # Contracción: sonido grave tipo "crunch".
        def encoger(tiempo, duracion):
            progreso = tiempo / duracion
            frecuencia = (
                130
                + 90
                * math.sin(
                    progreso * math.pi
                )
            )
            envolvente = self._envolvente(
                tiempo,
                duracion,
                0.015,
                0.12
            )
            oscilacion = (
                math.sin(
                    math.tau
                    * 17
                    * tiempo
                )
                * 0.18
            )
            return (
                math.sin(
                    math.tau
                    * frecuencia
                    * tiempo
                    + oscilacion
                )
                * envolvente
                * 0.30
            )

        # Inicio / reinicio.
        def inicio(tiempo, duracion):
            frecuencia = (
                350
                + 950 * (tiempo / duracion)
            )
            envolvente = self._envolvente(
                tiempo,
                duracion,
                0.01,
                0.10
            )
            return (
                math.sin(
                    math.tau
                    * frecuencia
                    * tiempo
                )
                * envolvente
                * 0.25
            )

        self._escribir_wave(
            "comer",
            0.12,
            comer
        )
        self._escribir_wave(
            "combo",
            0.16,
            combo
        )
        self._escribir_wave(
            "derrota",
            0.44,
            derrota
        )
        self._escribir_wave(
            "encoger",
            0.50,
            encoger
        )
        self._escribir_wave(
            "inicio",
            0.25,
            inicio
        )

    def reproducir(self, nombre):
        if not self.habilitado:
            return

        ruta = self.sonidos.get(nombre)

        if not ruta:
            return

        try:
            banderas = (
                self.winsound.SND_FILENAME
                | self.winsound.SND_ASYNC
                | self.winsound.SND_NODEFAULT
            )
            self.winsound.PlaySound(
                ruta,
                banderas
            )

        except Exception:
            pass

    def cerrar(self):
        if not self.habilitado:
            return

        try:
            self.winsound.PlaySound(None, self.winsound.SND_PURGE)
        except Exception:
            pass

        if self.carpeta_temporal is not None:
            try:
                for file in self.carpeta_temporal.glob("*"):
                    file.unlink(missing_ok=True)
                self.carpeta_temporal.rmdir()
            except Exception:
                pass


# ============================================================
# JUEGO
# ============================================================

class JuegoDeLaViborita:

    def __init__(self, raiz):
        self.raiz = raiz

        self.raiz.title("Juego de la Viborita")
        self.raiz.configure(bg=FONDO_HUD)
        self.raiz.resizable(False, False)

        # ----------------------------------------------------
        # Audio
        # ----------------------------------------------------

        self.audio = AudioProcedural()

        # ----------------------------------------------------
        # Estado del tablero
        # ----------------------------------------------------

        self.columnas = COLUMNAS_INICIALES
        self.filas = FILAS_INICIALES

        self.ancho_tablero_actual = self.columnas * TAMANO_CELDA
        self.alto_tablero_actual = self.filas * TAMANO_CELDA

        # ----------------------------------------------------
        # Estado de partida
        # ----------------------------------------------------

        self.derrotas = 0
        self.puntos = 0
        self.mejor_puntaje = 0

        self.viborita = []
        self.manzana = None

        self.direccion = "Derecha"

        # FIX V5:
        # La dirección ya NO cambia varias veces dentro del mismo tick.
        # Las entradas rápidas se guardan aquí y se consumen una por tick.
        self.cola_direcciones = []

        self.tiempo_aparicion_manzana = time.perf_counter()

        # ----------------------------------------------------
        # Combo
        # ----------------------------------------------------

        self.combo = 0
        self.combo_maximo = 0
        self.tiempo_ultima_manzana = None
        self.flash_combo_hasta = 0

        # ----------------------------------------------------
        # Estado visual / escenas
        # ----------------------------------------------------

        self.escena = "intro"

        self.inicio_intro = time.perf_counter()

        self.particulas = []
        self.textos_flotantes = []

        self.tiempo_ultimo_frame = time.perf_counter()

        self.pulso_cabeza_hasta = 0

        self.inicio_derrota = 0
        self.burla_derrota = ""

        self.inicio_encogimiento = 0
        self.progreso_encogimiento = 0

        self.ancho_inicio_encogimiento = 0
        self.alto_inicio_encogimiento = 0

        self.ancho_objetivo_encogimiento = 0
        self.alto_objetivo_encogimiento = 0

        self.columnas_nuevas_encogimiento = 0
        self.filas_nuevas_encogimiento = 0

        self.ultima_burla = None

        self.id_temporizador_juego = None

        # ----------------------------------------------------
        # Partículas ambientales
        # ----------------------------------------------------

        self.polvo_ambiental = []

        for _ in range(55):
            self.polvo_ambiental.append({
                "x": random.random(),
                "y": random.random(),
                "size": random.choice([1, 1, 1, 2]),
                "phase": random.random() * math.tau,
                "speed": random.uniform(0.4, 1.25),
            })

        # ----------------------------------------------------
        # Canvas
        # ----------------------------------------------------

        self.lienzo = tk.Canvas(
            self.raiz,
            bg=FONDO_SUPERIOR,
            highlightthickness=0,
            bd=0
        )
        self.lienzo.pack()

        self.vincular_teclas()
        self.redimensionar_ventana()

        self.raiz.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_juego
        )

        self.renderizar_frame()

    # ========================================================
    # CONTROLES
    # ========================================================

    def vincular_teclas(self):
        controles = {
            "<Up>": "Arriba",
            "<Down>": "Abajo",
            "<Left>": "Izquierda",
            "<Right>": "Derecha",

            "<w>": "Arriba",
            "<W>": "Arriba",
            "<s>": "Abajo",
            "<S>": "Abajo",
            "<a>": "Izquierda",
            "<A>": "Izquierda",
            "<d>": "Derecha",
            "<D>": "Derecha",
        }

        for tecla, direccion in controles.items():
            self.raiz.bind(
                tecla,
                lambda evento, d=direccion: self.encolar_direccion(d)
            )

        self.raiz.bind("<space>", self.manejar_tecla_accion)
        self.raiz.bind("<Return>", self.manejar_tecla_accion)

        self.raiz.bind("<r>", self.intentar_reiniciar)
        self.raiz.bind("<R>", self.intentar_reiniciar)

        self.raiz.bind(
            "<Escape>",
            lambda evento: self.cerrar_juego()
        )

    def manejar_tecla_accion(self, evento=None):
        if self.escena == "intro":
            transcurrido_ms = (
                time.perf_counter() - self.inicio_intro
            ) * 1000

            if transcurrido_ms >= INTRO_MINIMO_MS:
                self.iniciar_desde_intro()

        elif self.escena == "final":
            self.reiniciar_todo()

    def intentar_reiniciar(self, evento=None):
        if self.escena == "final":
            self.reiniciar_todo()

    def encolar_direccion(self, nueva_direccion):
        """
        FIX DEL GIRO RÁPIDO:
        --------------------
        Antes dos teclas dentro del mismo tick podían producir:
            Derecha -> Arriba -> Izquierda
        y el juego terminaba aplicando Izquierda directamente mientras la
        viborita todavía se movía hacia la Derecha, provocando una auto-colisión.

        Ahora:
        - se guardan hasta 2 giros;
        - se valida cada entrada respecto al último giro pendiente;
        - sólo se consume UN giro por tick.

        Derecha -> Arriba -> Izquierda se convierte en:
            tick 1: Arriba
            tick 2: Izquierda

        Nunca en un giro instantáneo de 180°.
        """

        if self.escena != "jugando":
            return

        if len(self.cola_direcciones) >= MAX_COLA_ENTRADAS:
            return

        direccion_referencia = (
            self.cola_direcciones[-1]
            if self.cola_direcciones
            else self.direccion
        )

        opuestos = {
            "Arriba": "Abajo",
            "Abajo": "Arriba",
            "Izquierda": "Derecha",
            "Derecha": "Izquierda",
        }

        # Repetir la misma dirección no aporta nada.
        if nueva_direccion == direccion_referencia:
            return

        # Nunca permitimos reversa directa.
        if nueva_direccion == opuestos[direccion_referencia]:
            return

        self.cola_direcciones.append(nueva_direccion)

    # ========================================================
    # INTRO
    # ========================================================

    def iniciar_desde_intro(self):
        if self.escena != "intro":
            return

        self.audio.reproducir("inicio")

        cx = self.ancho_tablero_actual / 2
        cy = ALTURA_HUD + self.alto_tablero_actual / 2

        self.generar_explosion(
            cx,
            cy,
            VERDE,
            count=48,
            speed=170
        )

        self.generar_explosion(
            cx,
            cy,
            CIAN,
            count=22,
            speed=130
        )

        self.iniciar_ronda()

    # ========================================================
    # GEOMETRÍA
    # ========================================================

    def establecer_tamano_ventana(self, ancho_tablero, alto_tablero):
        ancho_tablero = max(120, int(ancho_tablero))
        alto_tablero = max(100, int(alto_tablero))

        alto_total = alto_tablero + ALTURA_HUD

        self.lienzo.config(
            width=ancho_tablero,
            height=alto_total
        )

        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()

        x = (ancho_pantalla - ancho_tablero) // 2
        y = (alto_pantalla - alto_total) // 2

        self.raiz.geometry(
            f"{ancho_tablero}x{alto_total}+{x}+{y}"
        )

        self.ancho_tablero_actual = ancho_tablero
        self.alto_tablero_actual = alto_tablero

    def redimensionar_ventana(self):
        self.establecer_tamano_ventana(
            self.columnas * TAMANO_CELDA,
            self.filas * TAMANO_CELDA
        )

    # ========================================================
    # NUEVA RONDA
    # ========================================================

    def iniciar_ronda(self):
        self.escena = "jugando"

        self.puntos = 0
        self.combo = 0
        self.tiempo_ultima_manzana = None

        self.direccion = "Derecha"
        self.cola_direcciones.clear()

        centro_x = self.columnas // 2
        centro_y = self.filas // 2

        self.viborita = [
            (centro_x, centro_y),
            (centro_x - 1, centro_y),
            (centro_x - 2, centro_y),
        ]

        self.redimensionar_ventana()
        self.generar_manzana()

        if self.id_temporizador_juego is not None:
            try:
                self.raiz.after_cancel(self.id_temporizador_juego)
            except tk.TclError:
                pass

        self.id_temporizador_juego = self.raiz.after(
            420,
            self.tick_juego
        )

    # ========================================================
    # LOOP DEL JUEGO
    # ========================================================

    def tick_juego(self):
        self.id_temporizador_juego = None

        if self.escena != "jugando":
            return

        # ----------------------------------------------------
        # FIX V5:
        # Aplicar como máximo UNA entrada por tick.
        # ----------------------------------------------------

        if self.cola_direcciones:
            self.direccion = self.cola_direcciones.pop(0)

        cabeza_x, cabeza_y = self.viborita[0]

        if self.direccion == "Arriba":
            cabeza_y -= 1
        elif self.direccion == "Abajo":
            cabeza_y += 1
        elif self.direccion == "Izquierda":
            cabeza_x -= 1
        elif self.direccion == "Derecha":
            cabeza_x += 1

        nueva_cabeza = (cabeza_x, cabeza_y)

        # ----------------------------------------------------
        # Colisión con pared
        # ----------------------------------------------------

        if (
            cabeza_x < 0
            or cabeza_x >= self.columnas
            or cabeza_y < 0
            or cabeza_y >= self.filas
        ):
            self.perder()
            return

        va_a_comer = nueva_cabeza == self.manzana

        cuerpo_colision = (
            self.viborita
            if va_a_comer
            else self.viborita[:-1]
        )

        # ----------------------------------------------------
        # Auto-colisión
        # ----------------------------------------------------

        if nueva_cabeza in cuerpo_colision:
            self.perder()
            return

        # ----------------------------------------------------
        # Movimiento
        # ----------------------------------------------------

        self.viborita.insert(0, nueva_cabeza)

        if va_a_comer:
            self.manejar_manzana_comida()
        else:
            self.viborita.pop()

        self.id_temporizador_juego = self.raiz.after(
            VELOCIDAD_JUEGO_MS,
            self.tick_juego
        )

    # ========================================================
    # MANZANA / COMBO
    # ========================================================

    def generar_manzana(self):
        ocupadas = set(self.viborita)

        disponibles = [
            (x, y)
            for y in range(self.filas)
            for x in range(self.columnas)
            if (x, y) not in ocupadas
        ]

        if not disponibles:
            self.manzana = None
            return

        self.manzana = random.choice(disponibles)
        self.tiempo_aparicion_manzana = time.perf_counter()

    def manejar_manzana_comida(self):
        if self.manzana is None:
            return

        now = time.perf_counter()

        manzana_x, manzana_y = self.manzana

        self.puntos += 1
        self.mejor_puntaje = max(self.mejor_puntaje, self.puntos)

        # ----------------------------------------------------
        # Combo
        # ----------------------------------------------------

        if (
            self.tiempo_ultima_manzana is not None
            and now - self.tiempo_ultima_manzana <= VENTANA_COMBO_SEGUNDOS
        ):
            self.combo += 1
        else:
            self.combo = 1

        self.tiempo_ultima_manzana = now
        self.combo_maximo = max(self.combo_maximo, self.combo)

        if self.combo >= 2:
            self.flash_combo_hasta = now + 0.55
            self.audio.reproducir("combo")
        else:
            self.audio.reproducir("comer")

        self.pulso_cabeza_hasta = now + 0.22

        px = (
            manzana_x * TAMANO_CELDA
            + TAMANO_CELDA / 2
        )

        py = (
            ALTURA_HUD
            + manzana_y * TAMANO_CELDA
            + TAMANO_CELDA / 2
        )

        # Más espectáculo cuanto mayor sea el combo.
        burst_count = min(52, 20 + self.combo * 5)
        burst_speed = min(230, 110 + self.combo * 18)

        primary_color = (
            DORADO
            if self.combo >= 3
            else VERDE
        )

        self.generar_explosion(
            px,
            py,
            primary_color,
            count=burst_count,
            speed=burst_speed
        )

        if self.combo >= 2:
            self.generar_explosion(
                px,
                py,
                CIAN,
                count=min(18, 5 + self.combo * 2),
                speed=100 + self.combo * 8
            )

        popup_text = (
            f"COMBO x{self.combo}"
            if self.combo >= 2
            else "+1"
        )

        popup_color = (
            DORADO
            if self.combo >= 2
            else VERDE
        )

        self.textos_flotantes.append({
            "x": px,
            "y": py - 10,
            "text": popup_text,
            "life": 0.82,
            "max_life": 0.82,
            "color": popup_color,
        })

        self.generar_manzana()

    def actualizar_tiempo_combo(self, now):
        if (
            self.escena == "jugando"
            and self.combo > 1
            and self.tiempo_ultima_manzana is not None
            and now - self.tiempo_ultima_manzana > VENTANA_COMBO_SEGUNDOS
        ):
            self.combo = 0
            self.tiempo_ultima_manzana = None

    # ========================================================
    # DERROTA
    # ========================================================

    def perder(self):
        if self.escena != "jugando":
            return

        self.escena = "derrota"
        self.cola_direcciones.clear()

        self.derrotas += 1

        self.mejor_puntaje = max(
            self.mejor_puntaje,
            self.puntos
        )

        self.inicio_derrota = time.perf_counter()
        self.burla_derrota = self.obtener_burla()

        self.audio.reproducir("derrota")

        if self.viborita:
            cabeza_x, cabeza_y = self.viborita[0]

            px = (
                cabeza_x * TAMANO_CELDA
                + TAMANO_CELDA / 2
            )

            py = (
                ALTURA_HUD
                + cabeza_y * TAMANO_CELDA
                + TAMANO_CELDA / 2
            )

            self.generar_explosion(
                px,
                py,
                ROJO,
                count=48,
                speed=195
            )

            self.generar_explosion(
                px,
                py,
                CIAN,
                count=14,
                speed=125
            )

            self.generar_explosion(
                px,
                py,
                MAGENTA,
                count=10,
                speed=100
            )

        self.raiz.after(
            TIEMPO_DERROTA_MS,
            self.iniciar_encogimiento
        )

    # ========================================================
    # BURLAS
    # ========================================================

    def obtener_burla(self):
        if self.derrotas <= 2:
            pool = BURLAS_SUAVES
        elif self.derrotas <= 4:
            pool = BURLAS_MEDIAS
        elif self.derrotas <= 7:
            pool = BURLAS_DURAS
        elif self.derrotas <= 10:
            pool = BURLAS_BRUTALES
        else:
            pool = BURLAS_FINALES

        possible = [
            taunt
            for taunt in pool
            if taunt != self.ultima_burla
        ]

        if not possible:
            possible = pool

        taunt = random.choice(possible)
        self.ultima_burla = taunt

        return taunt

    # ========================================================
    # CONTRACCIÓN
    # ========================================================

    def iniciar_encogimiento(self):
        if self.escena != "derrota":
            return

        nuevas_columnas = self.columnas - 2
        nuevas_filas = self.filas - 2

        if (
            nuevas_columnas < COLUMNAS_MINIMAS
            or nuevas_filas < FILAS_MINIMAS
        ):
            self.derrota_final()
            return

        self.audio.reproducir("encoger")

        self.escena = "encogiendo"

        self.inicio_encogimiento = time.perf_counter()
        self.progreso_encogimiento = 0

        self.ancho_inicio_encogimiento = self.columnas * TAMANO_CELDA
        self.alto_inicio_encogimiento = self.filas * TAMANO_CELDA

        self.columnas_nuevas_encogimiento = nuevas_columnas
        self.filas_nuevas_encogimiento = nuevas_filas

        self.ancho_objetivo_encogimiento = nuevas_columnas * TAMANO_CELDA
        self.alto_objetivo_encogimiento = nuevas_filas * TAMANO_CELDA

        for _ in range(28):
            y = random.uniform(
                ALTURA_HUD,
                ALTURA_HUD + self.alto_tablero_actual
            )

            self.particulas.append({
                "x": random.choice([
                    5,
                    self.ancho_tablero_actual - 5
                ]),
                "y": y,
                "vx": random.uniform(-95, 95),
                "vy": random.uniform(-85, 85),
                "life": random.uniform(0.35, 0.85),
                "max_life": 0.85,
                "size": random.uniform(2, 5),
                "color": random.choice([ROJO, NARANJA, MAGENTA]),
            })

    def actualizar_encogimiento(self):
        if self.escena != "encogiendo":
            return

        transcurrido = (
            time.perf_counter()
            - self.inicio_encogimiento
        )

        progreso = limitar(
            transcurrido / (DURACION_ENCOGIMIENTO_MS / 1000),
            0,
            1
        )

        self.progreso_encogimiento = progreso
        suavizado = suavizado_cubico(progreso)

        ancho = interpolar(
            self.ancho_inicio_encogimiento,
            self.ancho_objetivo_encogimiento,
            suavizado
        )

        alto = interpolar(
            self.alto_inicio_encogimiento,
            self.alto_objetivo_encogimiento,
            suavizado
        )

        self.establecer_tamano_ventana(
            ancho,
            alto
        )

        if progreso >= 1:
            self.columnas = self.columnas_nuevas_encogimiento
            self.filas = self.filas_nuevas_encogimiento
            self.iniciar_ronda()

    # ========================================================
    # DERROTA FINAL
    # ========================================================

    def derrota_final(self):
        self.escena = "final"
        self.cola_direcciones.clear()

        centro_x = self.ancho_tablero_actual / 2
        centro_y = ALTURA_HUD + self.alto_tablero_actual / 2

        self.generar_explosion(
            centro_x,
            centro_y,
            ROJO,
            count=90,
            speed=230
        )

        self.generar_explosion(
            centro_x,
            centro_y,
            CIAN,
            count=38,
            speed=155
        )

        self.generar_explosion(
            centro_x,
            centro_y,
            MAGENTA,
            count=32,
            speed=145
        )

        self.audio.reproducir("derrota")

    def reiniciar_todo(self):
        self.derrotas = 0
        self.puntos = 0
        self.mejor_puntaje = 0

        self.combo = 0
        self.combo_maximo = 0
        self.tiempo_ultima_manzana = None

        self.columnas = COLUMNAS_INICIALES
        self.filas = FILAS_INICIALES

        self.particulas.clear()
        self.textos_flotantes.clear()
        self.cola_direcciones.clear()

        self.audio.reproducir("inicio")

        self.iniciar_ronda()

    # ========================================================
    # PARTÍCULAS
    # ========================================================

    def generar_explosion(
        self,
        x,
        y,
        color,
        count=20,
        speed=120
    ):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            velocity = random.uniform(
                speed * 0.35,
                speed
            )

            life = random.uniform(
                0.30,
                0.85
            )

            self.particulas.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * velocity,
                "vy": math.sin(angle) * velocity,
                "life": life,
                "max_life": life,
                "size": random.uniform(2, 5),
                "color": color,
            })

    def actualizar_particulas(self, dt):
        vivos = []

        for particula in self.particulas:
            particula["life"] -= dt

            if particula["life"] <= 0:
                continue

            particula["x"] += particula["vx"] * dt
            particula["y"] += particula["vy"] * dt

            particula["vx"] *= 0.985 ** (dt * 60)
            particula["vy"] *= 0.985 ** (dt * 60)

            particula["vy"] += 35 * dt

            vivos.append(particula)

        self.particulas = vivos

    # ========================================================
    # TEXTOS FLOTANTES
    # ========================================================

    def actualizar_textos_flotantes(self, dt):
        vivos = []

        for texto_flotante in self.textos_flotantes:
            texto_flotante["life"] -= dt

            if texto_flotante["life"] <= 0:
                continue

            texto_flotante["y"] -= 38 * dt

            vivos.append(texto_flotante)

        self.textos_flotantes = vivos

    # ========================================================
    # RENDER LOOP
    # ========================================================

    def renderizar_frame(self):
        if not self.raiz.winfo_exists():
            return

        now = time.perf_counter()

        dt = limitar(
            now - self.tiempo_ultimo_frame,
            0,
            0.05
        )

        self.tiempo_ultimo_frame = now

        if self.escena == "encogiendo":
            self.actualizar_encogimiento()

        self.actualizar_tiempo_combo(now)
        self.actualizar_particulas(dt)
        self.actualizar_textos_flotantes(dt)

        self.dibujar_escena(now)

        try:
            self.raiz.after(
                INTERVALO_RENDER_MS,
                self.renderizar_frame
            )
        except tk.TclError:
            pass

    # ========================================================
    # ESCENA COMPLETA
    # ========================================================

    def dibujar_escena(self, now):
        self.lienzo.delete("all")

        ancho = self.ancho_tablero_actual
        alto = self.alto_tablero_actual

        self.dibujar_fondo(
            ancho,
            alto,
            now
        )

        self.dibujar_hud(
            ancho,
            now
        )

        shake_x = 0
        shake_y = 0

        if self.escena == "derrota":
            transcurrido = now - self.inicio_derrota

            if transcurrido < 0.40:
                intensity = 1 - transcurrido / 0.40
                amplitude = 11 * intensity

                shake_x = random.uniform(
                    -amplitude,
                    amplitude
                )

                shake_y = random.uniform(
                    -amplitude,
                    amplitude
                )

        self.dibujar_cuadricula(
            ancho,
            alto,
            shake_x,
            shake_y
        )

        self.dibujar_polvo_ambiental(
            ancho,
            alto,
            now
        )

        if self.escena != "intro":
            if self.manzana is not None:
                self.dibujar_manzana(
                    ancho,
                    alto,
                    now,
                    shake_x,
                    shake_y
                )

            self.dibujar_viborita(
                ancho,
                alto,
                now,
                shake_x,
                shake_y
            )

        self.dibujar_particulas()
        self.dibujar_textos_flotantes()

        if self.escena == "intro":
            self.dibujar_intro(
                ancho,
                alto,
                now
            )

        elif self.escena == "derrota":
            self.dibujar_derrota(
                ancho,
                alto,
                now
            )

        elif self.escena == "encogiendo":
            self.dibujar_encogimiento(
                ancho,
                alto,
                now
            )

        elif self.escena == "final":
            self.dibujar_final(
                ancho,
                alto,
                now
            )

        elif self.escena == "jugando":
            self.dibujar_combo(
                ancho,
                alto,
                now
            )

        self.dibujar_borde_neon(
            ancho,
            alto,
            now
        )

    # ========================================================
    # FONDO
    # ========================================================

    def dibujar_fondo(
        self,
        ancho,
        alto,
        now
    ):
        alto_total = alto + ALTURA_HUD

        self.lienzo.create_rectangle(
            0,
            0,
            ancho,
            alto_total,
            fill=FONDO_SUPERIOR,
            outline=""
        )

        nivel_peligro = limitar(
            self.derrotas / 11,
            0,
            1
        )

        color_inferior = mezclar_color(
            FONDO_INFERIOR,
            "#290b16",
            nivel_peligro * 0.55
        )

        bandas = 26

        for i in range(bandas):
            t = i / max(1, bandas - 1)

            color = mezclar_color(
                FONDO_SUPERIOR,
                color_inferior,
                t
            )

            y1 = (
                ALTURA_HUD
                + alto * i / bandas
            )

            y2 = (
                ALTURA_HUD
                + alto * (i + 1) / bandas
            )

            self.lienzo.create_rectangle(
                0,
                y1,
                ancho,
                y2,
                fill=color,
                outline=""
            )

        # Scanlines animadas
        desfase = int(now * 22) % 12

        for y in range(
            ALTURA_HUD + desfase,
            int(ALTURA_HUD + alto),
            12
        ):
            self.lienzo.create_line(
                0,
                y,
                ancho,
                y,
                fill="#0b0d13"
            )


    # ========================================================
    # HUD
    # ========================================================

    def dibujar_hud(self, ancho, now):
        self.lienzo.create_rectangle(
            0,
            0,
            ancho,
            ALTURA_HUD,
            fill=FONDO_HUD,
            outline=""
        )

        glitch_strength = (
            2.5
            if self.escena in ("derrota", "encogiendo", "final")
            else 0.8
        )

        glitch = math.sin(now * 10.5) * glitch_strength

        titulo = (
            "JUEGO DE LA VIBORITA"
            if ancho >= 300
            else "VIBORITA"
        )

        tamano_titulo = (
            18
            if ancho >= 450
            else 15
            if ancho >= 250
            else 12
        )

        self.lienzo.create_text(
            ancho / 2 - 1.5 + glitch,
            24,
            text=titulo,
            fill=MAGENTA,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            ancho / 2 + 1.5 - glitch,
            24,
            text=titulo,
            fill=CIAN,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            ancho / 2,
            24,
            text=titulo,
            fill=BLANCO,
            font=("Consolas", tamano_titulo, "bold")
        )

        if ancho >= 420:
            self.lienzo.create_text(
                ancho / 2,
                46,
                text="UNNECESSARY PROJECT #001  //  BECAUSE I CAN",
                fill=TEXTO_TENUE,
                font=("Consolas", 7, "bold")
            )

        # ----------------------------------------------------
        # HUD adaptativo
        # ----------------------------------------------------

        if ancho >= 500:
            data = [
                ("PTS", self.puntos),
                ("MEJOR", self.mejor_puntaje),
                ("CAÍDAS", self.derrotas),
                ("MAPA", f"{self.columnas}x{self.filas}"),
            ]

            gap = 7
            margen = 16

            chip_width = (
                ancho
                - margen * 2
                - gap * 3
            ) / 4

            y1 = 61
            y2 = 91

            for index, (label, value) in enumerate(data):
                x1 = (
                    margen
                    + index * (chip_width + gap)
                )

                x2 = x1 + chip_width

                self.dibujar_indicador(
                    x1,
                    y1,
                    x2,
                    y2,
                    label,
                    value
                )

            if self.combo >= 2:
                combo_color = (
                    DORADO
                    if now < self.flash_combo_hasta
                    else NARANJA
                )

                self.lienzo.create_text(
                    ancho / 2,
                    100,
                    text=f"COMBO x{self.combo}",
                    fill=combo_color,
                    font=("Consolas", 7, "bold")
                )

        elif ancho >= 300:
            text = (
                f"PTS {self.puntos}"
                f"   |   MEJOR {self.mejor_puntaje}"
                f"   |   X {self.derrotas}"
            )

            self.lienzo.create_text(
                ancho / 2,
                70,
                text=text,
                fill=TEXTO_SECUNDARIO,
                font=("Consolas", 8, "bold")
            )

            secondary = (
                f"{self.columnas} x {self.filas}"
            )

            if self.combo >= 2:
                secondary += f"   //   COMBO x{self.combo}"

            self.lienzo.create_text(
                ancho / 2,
                88,
                text=secondary,
                fill=(
                    DORADO
                    if self.combo >= 2
                    else VERDE
                ),
                font=("Consolas", 7, "bold")
            )

        else:
            self.lienzo.create_text(
                ancho / 2,
                70,
                text=(
                    f"X {self.derrotas}"
                    f"   {self.columnas}x{self.filas}"
                ),
                fill=ROJO,
                font=("Consolas", 8, "bold")
            )

        color_linea = (
            ROJO
            if self.escena in (
                "derrota",
                "encogiendo",
                "final"
            )
            else VERDE
        )

        self.lienzo.create_rectangle(
            0,
            ALTURA_HUD - 2,
            ancho,
            ALTURA_HUD,
            fill=color_linea,
            outline=""
        )

    def dibujar_indicador(
        self,
        x1,
        y1,
        x2,
        y2,
        label,
        value
    ):
        self.rectangulo_redondeado(
            x1,
            y1,
            x2,
            y2,
            7,
            fill="#11131c",
            outline="#242838"
        )

        self.lienzo.create_text(
            x1 + 10,
            (y1 + y2) / 2,
            text=label,
            anchor="w",
            fill=TEXTO_TENUE,
            font=("Consolas", 7, "bold")
        )

        self.lienzo.create_text(
            x2 - 10,
            (y1 + y2) / 2,
            text=str(value),
            anchor="e",
            fill=BLANCO,
            font=("Consolas", 8, "bold")
        )

    # ========================================================
    # CUADRÍCULA
    # ========================================================

    def dibujar_cuadricula(
        self,
        ancho,
        alto,
        offset_x=0,
        offset_y=0
    ):
        ancho_celda = ancho / self.columnas
        alto_celda = alto / self.filas

        nivel_peligro = limitar(
            self.derrotas / 11,
            0,
            1
        )

        color_mayor = mezclar_color(
            CUADRICULA_MAYOR,
            "#46202d",
            nivel_peligro * 0.45
        )

        for x in range(self.columnas + 1):
            px = x * ancho_celda + offset_x

            color = (
                color_mayor
                if x % 5 == 0
                else CUADRICULA_MENOR
            )

            self.lienzo.create_line(
                px,
                ALTURA_HUD + offset_y,
                px,
                ALTURA_HUD + alto + offset_y,
                fill=color
            )

        for y in range(self.filas + 1):
            py = (
                ALTURA_HUD
                + y * alto_celda
                + offset_y
            )

            color = (
                color_mayor
                if y % 5 == 0
                else CUADRICULA_MENOR
            )

            self.lienzo.create_line(
                offset_x,
                py,
                ancho + offset_x,
                py,
                fill=color
            )

    # ========================================================
    # POLVO AMBIENTAL
    # ========================================================

    def dibujar_polvo_ambiental(
        self,
        ancho,
        alto,
        now
    ):
        for star in self.polvo_ambiental:
            pulso = (
                math.sin(
                    now * star["speed"]
                    + star["phase"]
                )
                + 1
            ) / 2

            if pulso < 0.35:
                continue

            x = star["x"] * ancho

            y = (
                ALTURA_HUD
                + star["y"] * alto
            )

            size = star["size"]

            color = (
                "#272d39"
                if pulso < 0.72
                else "#384253"
            )

            self.lienzo.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill=color,
                outline=""
            )

    # ========================================================
    # INTRO
    # ========================================================

    def dibujar_intro(
        self,
        ancho,
        alto,
        now
    ):
        top = ALTURA_HUD
        bottom = ALTURA_HUD + alto

        centro_x = ancho / 2
        centro_y = top + alto / 2

        transcurrido = now - self.inicio_intro

        pulso = (
            math.sin(now * 3.2)
            + 1
        ) / 2

        # Panel
        margen_panel = max(16, ancho * 0.08)

        self.rectangulo_redondeado(
            margen_panel,
            centro_y - 105,
            ancho - margen_panel,
            centro_y + 105,
            18,
            fill="#090b12",
            outline="#23293a"
        )

        # Símbolo
        self.lienzo.create_text(
            centro_x,
            centro_y - 68,
            text="◆",
            fill=VERDE,
            font=("Consolas", 24, "bold")
        )

        tamano_titulo = (
            24
            if ancho >= 430
            else 17
        )

        jitter = math.sin(now * 16) * 1.2

        self.lienzo.create_text(
            centro_x - 2 + jitter,
            centro_y - 26,
            text="JUEGO DE LA VIBORITA",
            fill=MAGENTA,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x + 2 - jitter,
            centro_y - 26,
            text="JUEGO DE LA VIBORITA",
            fill=CIAN,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            centro_y - 26,
            text="JUEGO DE LA VIBORITA",
            fill=BLANCO,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            centro_y + 10,
            text="COME. CRECE. PIERDE. ENCOGE.",
            fill=TEXTO_SECUNDARIO,
            font=("Consolas", 8, "bold")
        )

        if transcurrido * 1000 >= INTRO_MINIMO_MS:
            color_indicacion = mezclar_color(
                TEXTO_TENUE,
                VERDE,
                pulso
            )

            self.lienzo.create_text(
                centro_x,
                centro_y + 57,
                text="[ ESPACIO ]  JUGAR",
                fill=color_indicacion,
                font=("Consolas", 10, "bold")
            )
        else:
            self.lienzo.create_text(
                centro_x,
                centro_y + 57,
                text="INICIALIZANDO...",
                fill=TEXTO_TENUE,
                font=("Consolas", 8, "bold")
            )

        self.lienzo.create_text(
            centro_x,
            centro_y + 87,
            text="FLECHAS / WASD   •   ESC SALIR",
            fill="#3f4557",
            font=("Consolas", 7)
        )

    # ========================================================
    # MANZANA
    # ========================================================

    def dibujar_manzana(
        self,
        ancho,
        alto,
        now,
        offset_x,
        offset_y
    ):
        if self.manzana is None:
            return

        x, y = self.manzana

        ancho_celda = ancho / self.columnas
        alto_celda = alto / self.filas

        cx = (
            (x + 0.5)
            * ancho_celda
            + offset_x
        )

        cy = (
            ALTURA_HUD
            + (y + 0.5)
            * alto_celda
            + offset_y
        )

        transcurrido = (
            now - self.tiempo_aparicion_manzana
        )

        pulso = (
            math.sin(transcurrido * 5)
            + 1
        ) / 2

        radio = (
            min(ancho_celda, alto_celda)
            * (0.30 + pulso * 0.045)
        )

        # Halo pulsante
        halo = radio * (
            1.8 + pulso * 0.25
        )

        self.lienzo.create_oval(
            cx - halo,
            cy - halo,
            cx + halo,
            cy + halo,
            fill="#261019",
            outline=""
        )

        self.lienzo.create_oval(
            cx - radio * 1.42,
            cy - radio * 1.42,
            cx + radio * 1.42,
            cy + radio * 1.42,
            fill="#5c1728",
            outline=""
        )

        self.lienzo.create_oval(
            cx - radio,
            cy - radio * 0.85,
            cx + radio,
            cy + radio,
            fill=ROJO_MANZANA,
            outline=ROJO_MANZANA_OSCURO,
            width=1
        )

        self.lienzo.create_oval(
            cx - radio * 0.45,
            cy - radio * 0.55,
            cx - radio * 0.1,
            cy - radio * 0.2,
            fill="#ffafbd",
            outline=""
        )

        self.lienzo.create_line(
            cx,
            cy - radio * 0.8,
            cx + radio * 0.15,
            cy - radio * 1.35,
            fill="#9b7458",
            width=2
        )

        self.lienzo.create_oval(
            cx + radio * 0.05,
            cy - radio * 1.45,
            cx + radio * 0.75,
            cy - radio * 0.85,
            fill=VERDE_HOJA,
            outline=""
        )

    # ========================================================
    # SERPIENTE
    # ========================================================

    def dibujar_viborita(
        self,
        ancho,
        alto,
        now,
        offset_x,
        offset_y
    ):
        if not self.viborita:
            return

        ancho_celda = ancho / self.columnas
        alto_celda = alto / self.filas

        nivel_peligro = limitar(
            self.derrotas / 11,
            0,
            1
        )

        for index in range(
            len(self.viborita) - 1,
            -1,
            -1
        ):
            x, y = self.viborita[index]

            cx = (
                (x + 0.5)
                * ancho_celda
                + offset_x
            )

            cy = (
                ALTURA_HUD
                + (y + 0.5)
                * alto_celda
                + offset_y
            )

            size = (
                min(ancho_celda, alto_celda)
                * 0.72
            )

            es_cabeza = index == 0

            if (
                es_cabeza
                and now < self.pulso_cabeza_hasta
            ):
                restante = (
                    self.pulso_cabeza_hasta
                    - now
                )

                size *= (
                    1 + restante * 0.82
                )

            if es_cabeza:
                self.dibujar_cabeza_viborita(
                    cx,
                    cy,
                    size,
                    nivel_peligro,
                    now
                )
            else:
                self.dibujar_cuerpo_viborita(
                    cx,
                    cy,
                    size,
                    index,
                    nivel_peligro
                )

    def dibujar_cuerpo_viborita(
        self,
        cx,
        cy,
        size,
        index,
        nivel_peligro
    ):
        mitad = size / 2

        glow_dark = mezclar_color(
            BRILLO_VERDE_2,
            "#3a1a10",
            nivel_peligro * 0.45
        )

        glow_mid = mezclar_color(
            BRILLO_VERDE_1,
            "#7a3720",
            nivel_peligro * 0.32
        )

        self.rectangulo_redondeado(
            cx - mitad - 4,
            cy - mitad - 4,
            cx + mitad + 4,
            cy + mitad + 4,
            6,
            fill=glow_dark,
            outline=""
        )

        self.rectangulo_redondeado(
            cx - mitad - 2,
            cy - mitad - 2,
            cx + mitad + 2,
            cy + mitad + 2,
            5,
            fill=glow_mid,
            outline=""
        )

        color_cuerpo = mezclar_color(
            VERDE,
            NARANJA,
            nivel_peligro * 0.42
        )

        color_cuerpo = mezclar_color(
            color_cuerpo,
            "#42d96a",
            min(index * 0.018, 0.35)
        )

        self.rectangulo_redondeado(
            cx - mitad,
            cy - mitad,
            cx + mitad,
            cy + mitad,
            4,
            fill=color_cuerpo,
            outline=""
        )

        self.lienzo.create_line(
            cx - mitad * 0.48,
            cy - mitad * 0.45,
            cx + mitad * 0.3,
            cy - mitad * 0.45,
            fill="#d4ffd8",
            width=1
        )

    def dibujar_cabeza_viborita(
        self,
        cx,
        cy,
        size,
        nivel_peligro,
        now
    ):
        mitad = size / 2

        outer_glow = mezclar_color(
            "#102a18",
            "#4a160f",
            nivel_peligro * 0.72
        )

        mid_glow = mezclar_color(
            "#28683a",
            "#94422b",
            nivel_peligro * 0.50
        )

        color_cabeza = mezclar_color(
            VERDE_CABEZA,
            "#ffe08a",
            nivel_peligro * 0.40
        )

        self.rectangulo_redondeado(
            cx - mitad - 6,
            cy - mitad - 6,
            cx + mitad + 6,
            cy + mitad + 6,
            8,
            fill=outer_glow,
            outline=""
        )

        self.rectangulo_redondeado(
            cx - mitad - 3,
            cy - mitad - 3,
            cx + mitad + 3,
            cy + mitad + 3,
            7,
            fill=mid_glow,
            outline=""
        )

        self.rectangulo_redondeado(
            cx - mitad,
            cy - mitad,
            cx + mitad,
            cy + mitad,
            5,
            fill=color_cabeza,
            outline=""
        )

        # ----------------------------------------------------
        # Ojos / expresión
        # ----------------------------------------------------

        desfase_ojos = size * 0.19
        frente = size * 0.20

        if self.direccion == "Derecha":
            ojos = [
                (cx + frente, cy - desfase_ojos),
                (cx + frente, cy + desfase_ojos),
            ]
        elif self.direccion == "Izquierda":
            ojos = [
                (cx - frente, cy - desfase_ojos),
                (cx - frente, cy + desfase_ojos),
            ]
        elif self.direccion == "Arriba":
            ojos = [
                (cx - desfase_ojos, cy - frente),
                (cx + desfase_ojos, cy - frente),
            ]
        else:
            ojos = [
                (cx - desfase_ojos, cy + frente),
                (cx + desfase_ojos, cy + frente),
            ]

        radio_ojo = max(
            2,
            size * 0.085
        )

        panico = nivel_peligro > 0.62

        for ex, ey in ojos:
            if panico:
                # Ojos más abiertos cuando ya casi no queda tablero.
                r = radio_ojo * (
                    1.15
                    + 0.12 * math.sin(now * 12)
                )
                relleno_ojo = "#fff3f3"
            else:
                r = radio_ojo
                relleno_ojo = BLANCO

            self.lienzo.create_oval(
                ex - r,
                ey - r,
                ex + r,
                ey + r,
                fill=relleno_ojo,
                outline=""
            )

            pupila = r * (
                0.42
                if panico
                else 0.50
            )

            self.lienzo.create_oval(
                ex - pupila,
                ey - pupila,
                ex + pupila,
                ey + pupila,
                fill=NEGRO,
                outline=""
            )

        # Boca de pánico cerca del final
        if nivel_peligro > 0.72:
            tamano_boca = max(2, size * 0.08)

            boca_x = cx
            boca_y = cy

            if self.direccion == "Derecha":
                boca_x += size * 0.28
            elif self.direccion == "Izquierda":
                boca_x -= size * 0.28
            elif self.direccion == "Arriba":
                boca_y -= size * 0.28
            else:
                boca_y += size * 0.28

            self.lienzo.create_oval(
                boca_x - tamano_boca,
                boca_y - tamano_boca,
                boca_x + tamano_boca,
                boca_y + tamano_boca,
                fill="#3c1116",
                outline=""
            )

    # ========================================================
    # PARTÍCULAS VISUALES
    # ========================================================

    def dibujar_particulas(self):
        for particula in self.particulas:
            ratio = (
                particula["life"]
                / particula["max_life"]
            )

            size = (
                particula["size"]
                * ratio
            )

            if size < 0.4:
                continue

            color = mezclar_color(
                "#12131a",
                particula["color"],
                ratio
            )

            x = particula["x"]
            y = particula["y"]

            self.lienzo.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill=color,
                outline=""
            )

    def dibujar_textos_flotantes(self):
        for texto_flotante in self.textos_flotantes:
            ratio = (
                texto_flotante["life"]
                / texto_flotante["max_life"]
            )

            color = mezclar_color(
                "#34343c",
                texto_flotante["color"],
                ratio
            )

            self.lienzo.create_text(
                texto_flotante["x"],
                texto_flotante["y"],
                text=texto_flotante["text"],
                fill=color,
                font=("Consolas", 11, "bold")
            )

    # ========================================================
    # COMBO OVERLAY
    # ========================================================

    def dibujar_combo(
        self,
        ancho,
        alto,
        now
    ):
        if self.combo < 2:
            return

        if self.tiempo_ultima_manzana is None:
            return

        edad = now - self.tiempo_ultima_manzana

        if edad > VENTANA_COMBO_SEGUNDOS:
            return

        restante = (
            1 - edad / VENTANA_COMBO_SEGUNDOS
        )

        centro_x = ancho / 2
        y = ALTURA_HUD + 28

        pulso = (
            math.sin(now * 12)
            + 1
        ) / 2

        color = mezclar_color(
            NARANJA,
            DORADO,
            pulso
        )

        text_size = (
            13
            if ancho >= 300
            else 10
        )

        self.lienzo.create_text(
            centro_x,
            y,
            text=f"COMBO x{self.combo}",
            fill=color,
            font=("Consolas", text_size, "bold")
        )

        # Barra de tiempo del combo
        ancho_barra = min(
            180,
            ancho * 0.45
        )

        x1 = centro_x - ancho_barra / 2
        x2 = centro_x + ancho_barra / 2

        self.lienzo.create_rectangle(
            x1,
            y + 18,
            x2,
            y + 21,
            fill="#2a2114",
            outline=""
        )

        self.lienzo.create_rectangle(
            x1,
            y + 18,
            x1 + ancho_barra * restante,
            y + 21,
            fill=DORADO,
            outline=""
        )

    # ========================================================
    # PANTALLA DE MUERTE
    # ========================================================

    def dibujar_derrota(
        self,
        ancho,
        alto,
        now
    ):
        tope_tablero = ALTURA_HUD
        fondo_tablero = ALTURA_HUD + alto

        transcurrido = now - self.inicio_derrota

        if transcurrido < 0.22:
            nivel_flash = (
                1 - transcurrido / 0.22
            )

            color_flash = mezclar_color(
                FONDO_SUPERIOR,
                ROJO,
                nivel_flash * 0.58
            )

            self.lienzo.create_rectangle(
                0,
                tope_tablero,
                ancho,
                fondo_tablero,
                fill=color_flash,
                stipple="gray50",
                outline=""
            )

        self.lienzo.create_rectangle(
            0,
            tope_tablero,
            ancho,
            fondo_tablero,
            fill=NEGRO,
            stipple="gray50",
            outline=""
        )

        centro_x = ancho / 2
        centro_y = ALTURA_HUD + alto / 2

        pulso = (
            math.sin(now * 8)
            + 1
        ) / 2

        margen = 8 + pulso * 2

        self.lienzo.create_rectangle(
            margen,
            tope_tablero + margen,
            ancho - margen,
            fondo_tablero - margen,
            outline=ROJO_OSCURO,
            width=5
        )

        self.lienzo.create_rectangle(
            margen + 4,
            tope_tablero + margen + 4,
            ancho - margen - 4,
            fondo_tablero - margen - 4,
            outline=ROJO,
            width=1
        )

        if alto >= 260:
            title_y = centro_y - 80
            taunt_y = centro_y - 8
            estadisticas_y = centro_y + 48
            pie_y = centro_y + 82

            tamano_titulo = (
                26
                if ancho >= 400
                else 19
            )
        else:
            title_y = centro_y - 46
            taunt_y = centro_y
            estadisticas_y = centro_y + 31
            pie_y = centro_y + 54
            tamano_titulo = 15

        titulo = f"DERROTA #{self.derrotas}"

        glitch = math.sin(now * 22) * 2

        self.lienzo.create_text(
            centro_x - 2 - glitch,
            title_y,
            text=titulo,
            fill=CIAN,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x + 2 + glitch,
            title_y,
            text=titulo,
            fill=MAGENTA,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            title_y,
            text=titulo,
            fill=BLANCO,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            taunt_y,
            text=self.burla_derrota,
            fill=ROJO,
            font=(
                "Consolas",
                10 if ancho >= 300 else 8,
                "bold"
            ),
            width=max(100, ancho - 70),
            justify="center"
        )

        if alto >= 220:
            self.lienzo.create_text(
                centro_x,
                estadisticas_y,
                text=(
                    f"PUNTOS {self.puntos}"
                    f"   //   MEJOR COMBO x{self.combo_maximo}"
                ),
                fill=TEXTO_SECUNDARIO,
                font=("Consolas", 7, "bold")
            )

        next_cols = self.columnas - 2
        next_rows = self.filas - 2

        if (
            alto >= 180
            and ancho >= 220
        ):
            if (
                next_cols >= COLUMNAS_MINIMAS
                and next_rows >= FILAS_MINIMAS
            ):
                pie = (
                    f"Siguiente castigo: "
                    f"{next_cols} x {next_rows}"
                )
            else:
                pie = (
                    "Ya no queda mucho que quitarte."
                )

            self.lienzo.create_text(
                centro_x,
                pie_y,
                text=pie,
                fill=TEXTO_TENUE,
                font=("Consolas", 8)
            )

    # ========================================================
    # OVERLAY DE COMPRESIÓN
    # ========================================================

    def dibujar_encogimiento(
        self,
        ancho,
        alto,
        now
    ):
        top = ALTURA_HUD
        bottom = ALTURA_HUD + alto

        centro_x = ancho / 2
        centro_y = top + alto / 2

        pulso = (
            math.sin(now * 18)
            + 1
        ) / 2

        color_alerta = (
            ROJO
            if pulso > 0.42
            else BLANCO
        )

        ancho_panel = min(
            35,
            ancho * 0.10
        )

        self.lienzo.create_rectangle(
            0,
            top,
            ancho_panel,
            bottom,
            fill=BRILLO_ROJO,
            outline=ROJO,
            width=2
        )

        self.lienzo.create_rectangle(
            ancho - ancho_panel,
            top,
            ancho,
            bottom,
            fill=BRILLO_ROJO,
            outline=ROJO,
            width=2
        )

        if ancho > 220:
            for y in range(
                int(top + 25),
                int(bottom - 15),
                45
            ):
                self.lienzo.create_polygon(
                    8,
                    y,
                    ancho_panel - 6,
                    y + 10,
                    8,
                    y + 20,
                    fill=ROJO,
                    outline=""
                )

                self.lienzo.create_polygon(
                    ancho - 8,
                    y,
                    ancho - ancho_panel + 6,
                    y + 10,
                    ancho - 8,
                    y + 20,
                    fill=ROJO,
                    outline=""
                )

        # Progreso de compresión
        if ancho >= 260:
            self.lienzo.create_text(
                centro_x,
                centro_y - 28,
                text="COMPRESIÓN EN CURSO",
                fill=color_alerta,
                font=("Consolas", 14, "bold")
            )

            self.lienzo.create_text(
                centro_x,
                centro_y + 6,
                text="Porque claramente tenías demasiado espacio.",
                fill=TEXTO_SECUNDARIO,
                font=("Consolas", 8)
            )

            ancho_barra = min(
                180,
                ancho * 0.52
            )

            x1 = centro_x - ancho_barra / 2
            x2 = centro_x + ancho_barra / 2
            y = centro_y + 37

            self.lienzo.create_rectangle(
                x1,
                y,
                x2,
                y + 4,
                fill="#35131b",
                outline=""
            )

            self.lienzo.create_rectangle(
                x1,
                y,
                x1 + ancho_barra * self.progreso_encogimiento,
                y + 4,
                fill=ROJO,
                outline=""
            )

        elif ancho >= 180:
            self.lienzo.create_text(
                centro_x,
                centro_y,
                text="MENOS ESPACIO",
                fill=color_alerta,
                font=("Consolas", 10, "bold")
            )
        else:
            self.lienzo.create_text(
                centro_x,
                centro_y,
                text="-1",
                fill=ROJO,
                font=("Consolas", 18, "bold")
            )

    # ========================================================
    # FINAL
    # ========================================================

    def dibujar_final(
        self,
        ancho,
        alto,
        now
    ):
        top = ALTURA_HUD
        bottom = top + alto

        self.lienzo.create_rectangle(
            0,
            top,
            ancho,
            bottom,
            fill=NEGRO,
            stipple="gray50",
            outline=""
        )

        centro_x = ancho / 2
        centro_y = top + alto / 2

        pulso = (
            math.sin(now * 4)
            + 1
        ) / 2

        color_titulo = mezclar_color(
            ROJO,
            BLANCO,
            pulso * 0.3
        )

        tamano_titulo = (
            18
            if ancho >= 250
            else 13
        )

        self.lienzo.create_text(
            centro_x,
            centro_y - 55,
            text="FIN DEL JUEGO",
            fill=color_titulo,
            font=("Consolas", tamano_titulo, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            centro_y - 14,
            text=(
                "Conseguiste perder\n"
                "hasta quedarte sin tablero."
            ),
            fill=BLANCO,
            font=("Consolas", 8, "bold"),
            justify="center",
            width=max(100, ancho - 25)
        )

        self.lienzo.create_text(
            centro_x,
            centro_y + 27,
            text=(
                f"RÉCORD {self.mejor_puntaje}"
                f"   //   COMBO MÁX x{self.combo_maximo}"
            ),
            fill=TEXTO_SECUNDARIO,
            font=("Consolas", 7, "bold")
        )

        self.lienzo.create_text(
            centro_x,
            centro_y + 49,
            text="Impresionante.",
            fill=ROJO,
            font=("Consolas", 8, "italic")
        )

        if alto >= 150:
            indicacion = (
                "[ R / ESPACIO ] REINICIAR"
            )

            color_indicacion = mezclar_color(
                BRILLO_VERDE_1,
                VERDE,
                pulso
            )

            self.lienzo.create_text(
                centro_x,
                centro_y + 78,
                text=indicacion,
                fill=color_indicacion,
                font=("Consolas", 8, "bold")
            )

    # ========================================================
    # BORDE NEÓN
    # ========================================================

    def dibujar_borde_neon(
        self,
        ancho,
        alto,
        now
    ):
        top = ALTURA_HUD
        bottom = ALTURA_HUD + alto

        danger = (
            self.escena
            in (
                "derrota",
                "encogiendo",
                "final"
            )
        )

        principal = ROJO if danger else VERDE
        oscuro = ROJO_OSCURO if danger else BRILLO_VERDE_2

        nivel_peligro = limitar(
            self.derrotas / 11,
            0,
            1
        )

        if not danger:
            principal = mezclar_color(
                VERDE,
                NARANJA,
                nivel_peligro * 0.42
            )

        pulso = (
            math.sin(now * 3.5)
            + 1
        ) / 2

        borde = mezclar_color(
            oscuro,
            principal,
            0.35 + pulso * 0.25
        )

        self.lienzo.create_rectangle(
            1,
            top + 1,
            ancho - 2,
            bottom - 2,
            outline=borde,
            width=2
        )

    # ========================================================
    # RECTÁNGULO REDONDEADO
    # ========================================================

    def rectangulo_redondeado(
        self,
        x1,
        y1,
        x2,
        y2,
        radio,
        **kwargs
    ):
        radio = min(
            radio,
            abs(x2 - x1) / 2,
            abs(y2 - y1) / 2
        )

        puntos_poligono = [
            x1 + radio, y1,
            x2 - radio, y1,
            x2, y1,
            x2, y1 + radio,
            x2, y2 - radio,
            x2, y2,
            x2 - radio, y2,
            x1 + radio, y2,
            x1, y2,
            x1, y2 - radio,
            x1, y1 + radio,
            x1, y1,
        ]

        return self.lienzo.create_polygon(
            puntos_poligono,
            smooth=True,
            splinesteps=16,
            **kwargs
        )

    # ========================================================
    # CIERRE LIMPIO
    # ========================================================

    def cerrar_juego(self):
        if self.id_temporizador_juego is not None:
            try:
                self.raiz.after_cancel(
                    self.id_temporizador_juego
                )
            except tk.TclError:
                pass

        self.audio.cerrar()

        try:
            self.raiz.destroy()
        except tk.TclError:
            pass


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    raiz = tk.Tk()
    juego = JuegoDeLaViborita(raiz)
    raiz.mainloop()
