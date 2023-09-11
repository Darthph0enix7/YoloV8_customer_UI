import PySimpleGUI as sg
import yaml

with open('config.yaml', 'r') as file:
    data = yaml.safe_load(file)
    
    Model_typ = data['Model_typ']

def first_page_layout():
        label_button = True if Model_typ in ['Detection', 'Segmentation'] else False

        file_list_column = [
            [
                sg.Text("Image Folder"),
                sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
                )
            ],
            [
                sg.Text("Are you satisfied from the results?"),
                sg.Button("Yes", key='next'),
                sg.Button("No, upload for Training", key='upload')
            ],
            [
                sg.Button("Prev"),
                sg.Button("Next", key="Next_img")
            ]
        ]

        # For now will only show the name of the file that was chosen
        image_viewer_column = [
            [
                sg.Text("Choose an image from list on left:"),
                sg.Button('Label images for Training', key="label", visible=label_button)  # Visibility set here
            ],
            [sg.Text(size=(40, 1), key="-TOUT-")],
            [sg.Image(key="-IMAGE-", expand_x=False, expand_y=False)],
        ]

        # ----- Full layout -----
        layout = [
            [sg.Column(file_list_column), sg.VSeperator(), sg.Column(image_viewer_column),]
        ]
        return layout 