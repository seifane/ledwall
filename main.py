import sys

import PySide6
from PySide6 import QtWidgets
from PySide6.QtCore import QThread
from PySide6.QtGui import Qt, QPen, QBrush, QColor, QImage, QPixmap
from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat.QtCore import Qt as compactQt

from Core import Core
from Effects.Attributes.BoolAttribute import BoolAttribute
from Effects.Attributes.IntAttribute import IntAttribute
from Effects.Attributes.IntRangeAttribute import IntRangeAttribute
from Effects.Attributes.StringAttribute import StringAttribute
from Effects.BarsEffect import BarsEffect
from Effects.GifEffect import GifEffect
from Effects.HaloEffect import HaloEffect
from Effects.Rainbow import Rainbow
from Effects.TextEffect import TextEffect
from Effects.Wave import Wave
from LedGroup import LedGroup

EFFECT_CLASS_LIST = [
    BarsEffect,
    HaloEffect,
    TextEffect,
    GifEffect,
    Rainbow,
    Wave,
]

class MixerWidget(QtWidgets.QWidget):
    def __init__(self, parent, core:Core):
        super().__init__(parent)
        self.core = core
        self.core.onFrame.connect(lambda x: self.on_frame(x))

        self.layout = QtWidgets.QVBoxLayout(self)

        self.qt_buffer = QImage(self.core.group.width, self.core.group.height, QImage.Format_ARGB32)
        self.qt_buffer.fill(QColor(0, 0, 0, 255))
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem(QPixmap(self.qt_buffer))

        self.graphics = QtWidgets.QGraphicsScene(self)
        self.graphics.addItem(self.pixmap_item)
        self.graphics_view = QtWidgets.QGraphicsView(self.graphics)
        self.layout.addWidget(self.graphics_view)

        self.fader_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.fader_slider.setMinimum(0)
        self.fader_slider.setMaximum(1000)
        self.fader_slider.setValue(0)
        self.fader_slider.valueChanged.connect(self.handle_fader)
        self.layout.addWidget(self.fader_slider)

    def handle_fader(self, value):
        self.core.fader = value


    def on_frame(self, bufferName: str):
        if bufferName != 'merge':
            return
        self.qt_buffer.fill(QColor(0, 0, 0, 255))
        for x in range(len(self.core.buffer_merge)):
            for y in range(len(self.core.buffer_merge[x])):
                color = self.core.buffer_merge[x][y]
                self.qt_buffer.setPixelColor(x, y, QColor(color[0], color[1], color[2], color[3]))
        self.pixmap_item.setPixmap(QPixmap.fromImage(self.qt_buffer).scaled(400, 200))



class SideWidget(QtWidgets.QWidget):
    def __init__(self, parent, core: Core, effect_key: str):
        super().__init__(parent)
        self.widgets = []
        self.effect_key = effect_key

        self.pen = QPen()
        self.brush = QBrush(QColor(0, 0, 0, 255))

        self.core = core
        self.thread = QThread(self)
        self.core.onFrame.connect(lambda x: self.on_frame(x))

        self.selected_effect = None

        self.layout = QtWidgets.QVBoxLayout(self)

        self.qt_buffer = QImage(self.core.group.width, self.core.group.height, QImage.Format_ARGB32)
        self.qt_buffer.fill(QColor(0, 0, 0, 255))
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem(QPixmap(self.qt_buffer))

        # self.glrect = GLWidget(self)
        # self.glrect.setMaximumWidth(400)
        # self.glrect.setMaximumHeight(200)
        # self.layout.addWidget(self.glrect)

        self.graphics = QtWidgets.QGraphicsScene(self)
        self.graphics.addItem(self.pixmap_item)
        self.graphics_view = QtWidgets.QGraphicsView(self.graphics)
        self.layout.addWidget(self.graphics_view)

        self.selector = QtWidgets.QComboBox(self)
        self.selector.currentIndexChanged.connect(self.handle_effect_selected)
        self.layout.addWidget(self.selector)
        self.fill_effect_selector(self.selector)

        self.attribute_layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.attribute_layout)


    def handle_effect_selected(self, index):
        targetClass = self.selector.itemData(index)
        if targetClass is None:
            setattr(self.core, self.effect_key, None)
            return
        setattr(self.core, self.effect_key, targetClass(self.core))
        self.update_ui_for_effect(getattr(self.core, self.effect_key), self.attribute_layout)

    def update_ui_for_effect(self, effect, layout):
        widgets = []

        for w in self.widgets:
            layout.removeWidget(w)
            w.deleteLater()

        if effect is None:
            self.widgets = widgets
            return

        for key, attr in effect.get_attributes().items():
            widget = None
            if isinstance(attr, IntAttribute):
                label = QtWidgets.QLabel(self)
                label.setText(key)
                widgets.append(label)
                widget = QtWidgets.QSlider(Qt.Horizontal, self)
                widget.setMinimum(attr.min)
                widget.setMaximum(attr.max)
                widget.setValue(attr.value)
                widget.valueChanged.connect(lambda value, k=key: self.handle_input_int(value, k))
            if isinstance(attr, BoolAttribute):
                widget = QtWidgets.QCheckBox(self)
                widget.setCheckState(Qt.Checked if attr.value else Qt.Unchecked)
                widget.setText(key)
                widget.stateChanged.connect(lambda value, k=key: self.handle_input_bool(value, k))
            if isinstance(attr, IntRangeAttribute):
                label = QtWidgets.QLabel(self)
                label.setText(key)
                widgets.append(label)
                widget = QRangeSlider(compactQt.Horizontal)
                widget.setMinimum(float(attr.min))
                widget.setMaximum(float(attr.max))
                widget.setValue(attr.value)
                widget.valueChanged.connect(lambda value, k=key: self.handle_input_int_range(value, k))
            if isinstance(attr, StringAttribute):
                label = QtWidgets.QLabel(self)
                label.setText(key)
                widgets.append(label)
                widget = QtWidgets.QTextEdit(self)
                widget.setText(attr.value)
                widget.textChanged.connect(lambda w=widget, k=key: self.handle_input_str(w.toPlainText(), k))
            if widget is not None:
                widgets.append(widget)

        self.widgets = widgets
        for w in self.widgets:
            layout.addWidget(w)

        self.selected_effect = effect

    def handle_input_int(self, value: int, key: str):
        self.selected_effect.set_attribute_value(key, value)

    def handle_input_int_range(self, value: (int, int), key: str):
        self.selected_effect.set_attribute_value(key, value)

    def handle_input_bool(self, value: int, key: str):
        value = True if value == Qt.Checked else False
        self.selected_effect.set_attribute_value(key, value)

    def handle_input_str(self, value: str, key: str):
        self.selected_effect.set_attribute_value(key, value)

    def on_frame(self, x):
        if x != self.effect_key:
            return
        buffer = getattr(self.core, 'buffer_' + x).copy()
        self.qt_buffer.fill(QColor(0, 0, 0, 255))
        for x in range(len(buffer)):
            for y in range(len(buffer[x])):
                color = buffer[x][y]
                self.qt_buffer.setPixelColor(x, y, QColor(color[0], color[1], color[2], color[3]))
        self.pixmap_item.setPixmap(QPixmap.fromImage(self.qt_buffer).scaled(400, 200))
        # self.glrect.setBuffer(buffer)

    def fill_effect_selector(self, selector: QtWidgets.QComboBox):
        selector.clear()
        selector.addItem('None', None)
        for elem in EFFECT_CLASS_LIST:
            selector.addItem(elem.get_name(), elem)

class MainWindow(QtWidgets.QWidget):
    core: Core = None

    effect_list_content = []
    selected_effect = None

    widgets = []

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenLed")

        self.core = Core()
        self.core.group = LedGroup(32, 1)
        self.core.start()

        self.layout = QtWidgets.QHBoxLayout(self)

        self.side_a_widget = SideWidget(self, self.core, 'effect_a')
        self.side_b_widget = SideWidget(self, self.core, 'effect_b')
        self.mixer_widget = MixerWidget(self, self.core)
        self.layout.addWidget(self.side_a_widget)
        self.layout.addWidget(self.mixer_widget)
        self.layout.addWidget(self.side_b_widget)

    def closeEvent(self, event:PySide6.QtGui.QCloseEvent) -> None:
        self.core.stop()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(1400, 800)
    widget.show()

    sys.exit(app.exec_())