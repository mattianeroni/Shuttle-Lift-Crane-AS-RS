import dash
import dash_table
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc

import matt99
from matt99 import INPUT, OUTPUT
import simpy


app = dash.Dash(__name__, serve_locally=True)
app.title = "Matt99"



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


"""
if __name__ == "__main__":

    simTime = 140_000
    initFilling = 0.5
    avgArrival = 120

    env = simpy.Environment()

    sim = matt99.Simulation(env,
                            shuttles = tuple(matt99.Shuttle(env, 2.0, 0.5, (i*30, 0, 0)) for i in range(4)),
                            racks = tuple(matt99.Rack(corridors=30, levels=10, corridor_size=4, level_size=1,
                                                      position=(0, 0, i*12), location_spaces=(6,2), location_size=12,
                                                      crane=matt99.Crane(env, (1.3,1.3,1.3), (0.3,0.3,0.3), (0,10,i*12)),
                                                      lifts=tuple(matt99.Lift(env, 0.6, 0.3, (j*30, 0, i*12), (j*30, 10, i*12), (j*30, 0, i*12)) for j in range(4))
                                                      )
                                          for i in range(3)),
                            depots = tuple(matt99.Depot((i*30, 0, 0)) for i in range(4)),
                            depots_prob = { INPUT : {0 : 0.25,  2 : 0.25}, OUTPUT : {1 : 0.25, 3 : 0.25}},
                            kinds_prob = {INPUT : 0.5, OUTPUT : 0.5},
                            codes_prob = {(101, 6) : 0.5, (102, 3) : 0.2, (103, 5) : 0.1, (104, 3) : 0.05, (105, 6) : 0.05},
                            quantities_prob = {1 : 0.5, 2 : 0.5},
                            uploadTime = 20.0
                        )

    sim.warmup (initFilling)
    env.process(sim(simTime, avgArrival))
    env.run()


    for job in sim.done:
        print(job.kind, job.arrival, " - ", job.history["END"] - job.history["START"])

"""