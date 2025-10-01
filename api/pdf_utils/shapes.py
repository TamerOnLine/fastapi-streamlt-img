from reportlab.pdfgen import canvas
from .config import LEFT_BG, LEFT_BORDER, RULE_COLOR, CARD_RADIUS

def draw_round_rect(c: canvas.Canvas, x: float, y: float, w: float, h: float,
                    fill_color=LEFT_BG, stroke_color=LEFT_BORDER, radius=CARD_RADIUS):
    c.setFillColor(fill_color)
    c.setStrokeColor(stroke_color)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)

def draw_rule(c: canvas.Canvas, x: float, y: float, w: float, color=RULE_COLOR):
    c.setStrokeColor(color)
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
