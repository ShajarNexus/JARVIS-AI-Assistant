import tkinter as tk
import math

from app import theme


class JarvisOrb(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent, bg=theme.PANEL)

        self.canvas = tk.Canvas(
            self,
            width=300,
            height=300,
            bg=theme.PANEL,
            highlightthickness=0
        )

        self.canvas.pack()

        self.state = "idle"
        self.angle = 0
        self.pulse = 0

        self.animate()

    def set_state(self, state):
        self.state = state

    def animate(self):

        self.canvas.delete("all")

        cx, cy = 150, 150

        colors = {
            "idle": "#087FAD",
            "listening": "#00E5FF",
            "thinking": "#A855F7",
            "speaking": "#00E5A0"
        }

        color = colors.get(self.state, "#087FAD")

        pulse = abs(math.sin(self.pulse)) * 10

        # Outer rings
        for i in range(5):

            radius = 105 + i * 9 + pulse

            self.canvas.create_oval(
                cx-radius,
                cy-radius,
                cx+radius,
                cy+radius,
                outline=color,
                width=1
            )

        # Main orb
        radius = 78 + pulse / 3

        self.canvas.create_oval(
            cx-radius,
            cy-radius,
            cx+radius,
            cy+radius,
            fill="#10243A",
            outline=color,
            width=3
        )

        # Inner circle
        self.canvas.create_oval(
            115, 115,
            185, 185,
            fill="#071624",
            outline="#00D9FF",
            width=2
        )

        # JARVIS logo
        self.canvas.create_text(
            cx,
            cy,
            text="J",
            fill="white",
            font=("Arial", 36, "bold")
        )

        # Rotating particles
        for i in range(8):

            angle = math.radians(
                self.angle + i * 45
            )

            x = cx + 115 * math.cos(angle)
            y = cy + 115 * math.sin(angle)

            self.canvas.create_oval(
                x-3, y-3,
                x+3, y+3,
                fill=color,
                outline=color
            )

        self.angle += 3
        self.pulse += 0.08

        self.after(40, self.animate)