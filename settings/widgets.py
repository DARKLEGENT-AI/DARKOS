from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPainterPath, QRegion

class OctagonButton(QPushButton):
    def resizeEvent(self, event):
        super().resizeEvent(event)

        w, h = self.width(), self.height()
        cut = min(w, h) * 0.2

        path = QPainterPath()
        path.moveTo(cut, 0)
        path.lineTo(w - cut, 0)
        path.lineTo(w, cut)
        path.lineTo(w, h - cut)
        path.lineTo(w - cut, h)
        path.lineTo(cut, h)
        path.lineTo(0, h - cut)
        path.lineTo(0, cut)
        path.closeSubpath()

        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
