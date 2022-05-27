import os
import sys
from pathlib import Path, PurePath

import PySimpleGUI as sg

from sorter import Sorter


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ASSETS_DIR = PurePath(__file__).parent / 'assets'
ASSETS_DIR = resource_path('assets')


class GUI:
    THEME = 'Dark Amber'
    LAYOUT = [
        [sg.Image(filename=Path(ASSETS_DIR) / 'logo.png', expand_x=True)],
        [
            sg.Text('Файл'),
            sg.In(size=(45, 1), enable_events=True, key='-FILE-', readonly=True),
            sg.FileBrowse('Выбрать', key='-SELECT FILE-')
        ],
        [sg.Text('Листы для сортировки', expand_x=True, justification='center')],
        [sg.Listbox(
            values=['1,0', '2,5', '4,0', '6,0'],
            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
            size=(40, 6),
            expand_x=True,
            key='-WIRE SECTIONS-')],
        [sg.ProgressBar(100, orientation='h', s=(20, 20), expand_x=True, bar_color=('blue', 'LightSteelBlue3'),
                        k='-PBAR-')],
        [sg.Button('Сортировать', expand_x=True, k='-SORT-'), sg.CloseButton('Выход')],
    ]

    def __init__(self, app_name, ):
        self.theme = self.THEME
        self.app_name = app_name
        self.window = sg.Window(self.app_name, self.LAYOUT)

    def start(self, backend: Sorter):
        sg.theme(self.theme)
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break

            try:
                self.handle_event(backend=backend, event=event, values=values)
            except Exception as e:
                sg.popup_error_with_traceback('Ошибка', e)
                self.window['-PBAR-'].update_bar(current_count=0)
            finally:
                backend.reset()
                self.window['-SORT-'].update(disabled=False)

        self.window.close()

    def handle_event(self, backend, event, values):

        if event == '-SORT-':
            self.window['-SORT-'].update(disabled=True)
            self.window['-PBAR-'].update_bar(current_count=0)
            file = values['-FILE-']
            wire_sections = values['-WIRE SECTIONS-']
            backend.wb = file
            self.window['-PBAR-'].update_bar(current_count=10)
            backend.add_sheets(wire_sections)
            sorted_circuitry = backend.sort()
            self.window['-PBAR-'].update_bar(current_count=25)
            backend.dump_circuitry(circuitry=sorted_circuitry)
            self.window['-PBAR-'].update_bar(current_count=75)
            backend.save_to_file(Path(file))
            self.window['-PBAR-'].update_bar(current_count=100)
