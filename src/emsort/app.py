from gui import GUI
from sorter import Sorter


class App:
    def __init__(self, name: str):
        self.gui = GUI(app_name=name)
        self.backend = Sorter()

    def start(self):
        self.gui.start(backend=self.backend)

