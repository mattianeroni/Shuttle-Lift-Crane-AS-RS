"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This file is part of the collaboration between University of Parma, Universitat 
Oberta de Catalunya, and Matter Srl.

The object of the collaboration is (i) the development of a discrete event simulation 
for the Matt99 system (i.e., a Shuttle-Lift-Crane based Automated Storage/Retrieval 
System sold by the company), (ii) the development of a web application so that the 
simulation can be used by everybody (even who is not able of programming), (iii) the 
development aand validation of a biased-randomised discrete event heuristic 
able to improve the system performance.


Written by: Mattia Neroni, Ph.D, Eng. (May 2020)
Author's contact: mattianeroni@yahoo.it
Author's website: https://mattianeroni.github.io

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import dash
import dash_table
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc

import asrs
from asrs.kind import INPUT, OUTPUT
import simpy


app = dash.Dash(__name__, serve_locally=True)
app.title = "Shuttle Lift Crane AS/RS"



app.layout = html.Div([

    html.H6('General data'),
    dash_table.DataTable(
        id='general-table',
        editable=True,
        style_cell={"textAlign" : "center"},
        style_table={'width': '20px'},
        style_header={'fontWeight': 'bold'},
        columns=[
            {"name": "SimulationTime[days]", "id": "SimulationTime"},
            {"name": "InitialFilling[%]", "id": "InitialFilling"},
            {"name": "UploadingTime[s]", "id": "UploadingTime"}
        ],
        data=[{"SimulationTime" : 5, "InitialFilling" : .5, "UploadingTime" : 120}]
    ),
    html.Br(),
    dbc.Row([html.H6('Depots data'), html.Button("Add",id="add-depot",n_clicks=0), html.Button("Remove",id="pop-depot",n_clicks=0)]),
    dash_table.DataTable(
        id='depots-table',
        editable=True,
        style_cell={"textAlign" : "center"},
        style_table={'width': '20px'},
        style_header={'fontWeight': 'bold'},
        columns=[
            {"name": "Type", "id": "Type", "presentation" : "dropdown"},
            {"name": "Probability", "id": "Probability"},
            {"name": "ShuttleSpeed[m/s]", "id": "ShuttleSpeed"},
            {"name": "ShuttleAcceleration[m/s2]", "id": "ShuttleAcceleration"}
        ],
        dropdown={"Type" : {"options" : [{"label" : "INPUT", "value" : INPUT}, {"label" : "OUTPUT", "value" : OUTPUT}]}},
        data=[
            {"Type" : "INPUT", "Probability" : 0.25,"ShuttleSpeed" : 2.0, "ShuttleAcceleration" : .5},
            {"Type" : "OUTPUT", "Probability" : 0.25,"ShuttleSpeed" : 2.0, "ShuttleAcceleration" : .5},
            {"Type" : "INPUT", "Probability" : 0.25,"ShuttleSpeed" : 2.0, "ShuttleAcceleration" : .5},
            {"Type" : "OUTPUT", "Probability" : 0.25,"ShuttleSpeed" : 2.0, "ShuttleAcceleration" : .5}
        ]
    ),


])



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)





