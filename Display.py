import sdl2
import sdl2.ext
import numpy as np

class Chip8Display:
    def __init__(self, scale=10):
        self.width = 64
        self.height = 32
        self.scale = scale
        self.screen = np.zeros((self.height, self.width), dtype=np.uint8)

        # Inicializa SDL2
        sdl2.ext.init()
        self.window = sdl2.ext.Window("CHIP-8 Emulator", size=(self.width * self.scale, self.height * self.scale))
        self.window.show()

        self.renderer = sdl2.ext.Renderer(self.window)
        self.renderer.clear()

    def clear(self):
        """Limpa a tela (instrução 00E0)."""
        self.screen.fill(0)

    def draw_sprite(self, x, y, sprite):
        collision = False
        for row_index, byte in enumerate(sprite):
            for col_index in range(8):  # Cada byte tem 8 bits (horizontal)
                if (byte >> (7 - col_index)) & 1:  # Verifica se o bit está ligado
                    pixel_x = (x + col_index) % self.width
                    pixel_y = (y + row_index) % self.height

                    if self.screen[pixel_y, pixel_x] == 1:
                        collision = True  # Um pixel aceso foi apagado

                    # XOR (inverte o estado do pixel)
                    self.screen[pixel_y, pixel_x] ^= 1

        return collision

    def scroll_right(self):
        """Desloca a tela para a direita, movendo os pixels da direita para a esquerda e limpando a coluna mais à esquerda."""
        for y in range(self.height):
            self.screen[y] = np.roll(self.screen[y], 1)
            self.screen[y, 0] = 0

    def scroll_left(self):
        """Desloca a tela para a esquerda, movendo os pixels da esquerda para a direita e limpando a última coluna."""
        for y in range(self.height):
            self.screen[y] = np.roll(self.screen[y], -1)
            self.screen[y, -1] = 0

    def scroll_down(self, n):
        """Desloca a tela para baixo, movendo as linhas para baixo e limpando as linhas superiores."""
        if n <= 0:
            return
        for i in range(self.height - n):
            self.screen[i] = self.screen[i + n]
        for i in range(self.height - n, self.height):
            self.screen[i] = [0] * self.width  # Limpa as últimas linhas

    def set_high_resolution(self, enabled):
        """Muda para gráficos de alta resolução (128x64) ou baixa resolução (64x32)."""
        if enabled:
            self.width, self.height = 128, 64
            self.screen = np.zeros((self.height, self.width), dtype=np.uint8)
        else:
            self.width, self.height = 64, 32
            self.screen = np.zeros((self.height, self.width), dtype=np.uint8)

    def render(self):
        """Renderiza a tela no SDL2."""
        self.renderer.clear()
        self.renderer.color = sdl2.ext.Color(255, 255, 255)  # Branco para pixels acesos

        for y in range(self.height):
            for x in range(self.width):
                if self.screen[y, x]:  # Se o pixel estiver ligado
                    rect = sdl2.SDL_Rect(x * self.scale, y * self.scale, self.scale, self.scale)
                    sdl2.SDL_RenderFillRect(self.renderer.sdlrenderer, rect)

        self.renderer.present()

    def destroy(self):
        """Fecha a janela e encerra o SDL2."""
        self.window.close()
        sdl2.ext.quit()

# Teste
if __name__ == "__main__":
    display = Chip8Display(scale=10)  # Escala de 10x (tela 640x320)

    # Teste: desenha um número "0" na posição (10,5)
    sprite_0 = [0xF0, 0x90, 0x90, 0x90, 0xF0]
    display.draw_sprite(10, 5, sprite_0)
    display.render()

    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False

    display.destroy()
