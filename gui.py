#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 01:52:31 2023

@author: Reetinav Das
"""

### GUI Design for Camera App ###


## Packages ##
# Package for GUI #
import PySimpleGUI as sg
# Camera class package #
from Camera import Camera
from HandNetwork import HandNetwork

def main():
    ## Stored Text ##
    intro = "This program enables hand gestures to interact with your computer."

    ## Creating GUI ##
    sg.theme("DarkBlue14")
    layout = [
            # Introduction Section
            [sg.Text('Hand Gesture Inputs', font=('Arial', 30))],
            [sg.Text(intro)],
            [sg.HSep()],
            
            # Enable Camera #
            [sg.Text('Enable Camera', font=('Arial', 20))],
            [sg.Button('Turn on camera')],
            [sg.HSep()],
            
            # Settings Tab #
            [sg.Text('Settings',font=('Arial',20))],
            [sg.Text('Input Sensitivity')],
            [sg.Slider([70,90], orientation='h', s=(10,15), 
                        key='-PER-', default_value = 80)],
            # Testing button #
            [sg.Button('Check')],
            [sg.HSep()],
            
            # Gestures List #
            [sg.Text('List of Recognized Gestures', font=('Arial', 20))],
            [sg.Table([['Point Up','Volume Up'],
                        ['Point Down','Volume Down'],
                        ['Open Hand','Pause/Play'],
                        ['Thumb Left','Previous Song'],
                        ['Thumb Right','Skip Song'],
                        ['Point Left','Scrub Back'],
                        ['Point Right','Scrub Forward']],
                        ['Recognized Gesture','Output'], 
                        num_rows=3
                        )],
            [sg.HSep()],
            
            # Useful Inputs #
            [sg.Text('Necessary Hotkeys:', font=('Arial', 20))],
            [sg.Frame('Keyboard Inputs', [[
                sg.Text('Q: Quit Camera')
                ]])],
            [sg.Quit()]
            ]      

    # Initialize Window. 
    window = sg.Window('Hand Gesture Inputs', layout, size = (800,600)) 

    # Everything runs in the loop here.
    while True:
        event, values = window.read()
        
        # Quit Button #
        if event == sg.WIN_CLOSED or event == 'Quit':
            break
        
        # Testing Button #
        if event =='Check':
            print("Confidence: ", values['-PER-']/100)
        
        # Event Trigger for Camera Enable #
        if event == 'Turn on camera':
            cap = Camera(values['-PER-']/100)
            cap.start_capture_session()
        
        # Storing Updated Slider Value #
        if event == '-PER-':
            window['-PER-'].update(values['-PER-'][:-1])
        
    window.close()

if __name__ == '__main__':
    main()