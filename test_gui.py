import PySimpleGUI as sg

sg.theme('LightBlue2')
layout = [[sg.Text('Teste')], [sg.Button('OK')]]
window = sg.Window('Teste', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'OK':
        break

window.close()
