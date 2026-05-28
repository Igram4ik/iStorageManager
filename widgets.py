import tkinter as tk

class ModernButton(tk.Canvas):
    """Кастомная кнопка на Canvas с эффектом наведения."""
    def __init__(self, parent, text, command,
                 bg="#2a6cb6", bg_hover="#4a90d9",
                 fg="white", font=('Arial', 11, 'bold'), **kwargs):
        # Сохраняем наши кастомные параметры
        self._command = command
        self._text = text
        self._bg = bg
        self._bg_hover = bg_hover
        self._fg = fg
        self._font = font

        # Все остальные параметры (width, height и т.д.) уйдут в Canvas
        super().__init__(parent, highlightthickness=0, **kwargs)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        # Рисуем кнопку после того, как Canvas создан и размеры известны
        self._draw_button()

    def _draw_button(self, bg=None):
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        if bg is None:
            bg = self._bg
        self.create_rectangle(0, 0, w, h, fill=bg, outline="", tags="bg")
        self.create_text(w//2, h//2, text=self._text,
                         fill=self._fg, font=self._font, tags="txt")

    def _on_enter(self, event):
        self._draw_button(self._bg_hover)

    def _on_leave(self, event):
        self._draw_button(self._bg)

    def _on_click(self, event):
        self._command()