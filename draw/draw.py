import matplotlib.pyplot as plt
import seaborn as sns
import io
import os, sys
from datetime import datetime
from PIL import Image
import pandas as pd
from load_data import load_config, load_raw_data, load_xy_data, load_position_data, load_distance_data, load_data, analyze_simulation_structure, press_any_key_to_continue, create_list
from plot_data import draw_map
from scipy.interpolate import make_interp_spline
import numpy as np

#print('Modify the config.yml file, keeping in mind that:\n')
#analyze_simulation_structure('/home/cristiano/PycharmProjects/Sama_simulator/output/04_15_25-19_00_41/04_15_25-19_00_41.pkl')
#print()
#press_any_key_to_continue()


#load the configuration file
config = load_config('config.yml')

#load the raw data (downlink or uplink) from the .pkl file
raw_data = load_raw_data (config['general']['file'], config['general']['type_link'])

#load simulation_list and bs_ue_list
simulation_list = create_list(config['general']['s_min'], config['general']['s_max'], config['general']['s_step'])
bs_ue_list = create_list(config['general']['bs_ue_min'], config['general']['bs_ue_max'], config['general']['bs_ue_step'])

time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if config['general']['make'] == 'graph':
    if config['graph']['x_var'] == 'distance' or config['graph']['y_var']=='distance':
        if config['graph']['x_var']=='distance':
              x_data = load_distance_data(bs_ue_list, simulation_list, raw_data)
              y_data = load_data(config['graph']['y_var'],bs_ue_list,simulation_list, raw_data)
        else:
              y_data = load_distance_data(bs_ue_list, simulation_list, raw_data)
              x_data = load_data(config['graph']['y_var'],bs_ue_list,simulation_list, raw_data)

    else:
        x_data, y_data = load_xy_data(config['graph']['x_var'],config['graph']['y_var'],bs_ue_list,simulation_list, raw_data)

    #customize the graph
    plt.figure(figsize=tuple(config['graph']['figsize']), dpi=config['graph']['resolution'])
    plt.title(config['graph']['title'])
    plt.xlabel(config['graph']['xlabel'])
    plt.ylabel(config['graph']['ylabel'])
    match config['graph']['auto_scale']:
        case 'True':
            plt.autoscale()
            plt.grid(config['graph']['grid'])
        case 'False':
            plt.xlim((config['graph']['xlim']))
            plt.ylim(config['graph']['ylim'])
            plt.grid(config['graph']['grid'])


    #draw the graph
    match config['graph']['graph_type']:
        case 'scatter':
            fig =  sns.scatterplot(x=x_data, y=y_data, color='purple', size=y_data, sizes=(1,1), legend=False)
        case 'line':
            if config['graph']['x_var'] == 'distance' or config['graph']['y_var'] == 'distance':
                data_long = pd.DataFrame({"x": x_data, "y": y_data})
                data_long = data_long.sort_values(by="x").groupby("x", as_index=False).mean()
                x_smooth = np.linspace(data_long["x"].min(), data_long["x"].max(), 500)  # Mais pontos para suavização
                spl = make_interp_spline(data_long["x"], data_long["y"], k=1)  # k=3 para spline cúbica
                y_smooth = spl(x_smooth)
                print(data_long)
                sns.lineplot(data=data_long, x='x', y='y', color="blue")
                #sns.regplot(data=data_long, x="x", y="y", order=5, ci=None, color="blue", scatter=False)
            else:
                fig = sns.lineplot(x=x_data, y=y_data)
        case 'boxplot':
            fig = sns.boxplot(x=x_data, y=y_data)
        case 'bar':
            fig = sns.barplot(x=x_data, y=y_data, ci=None)
        case 'histplot':
            fig = sns.histplot(x_data)
        case _:
            print("Check the 'graph_type' parameter!")

    # save the graph
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    imagem1 = Image.open(buf)
    imagem1.show()
    print('2) Your graph is ready!')
    s = input("3) Do you want to save your graph(y/n)?:")
    match s:
        case "y":
            output_dir = os.path.join("graphics", time)
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, config['graph']['save_as'])
            imagem1.save(save_path)
            print("4) Graphic saved as " + str(config['graph']['save_as']) + "!")
        case _:
            print ("4) Make the desired changes to config.yml!")


elif config['general']['make'] == 'map':

    #draw maps (complete == true --> draw all maps | complete == false --> draw a specific map)
    if config['map']['complete'] == True:
        for t in bs_ue_list:
            for i in simulation_list:
                title = config['map']['title'] +  ' (' + str(t+1)  + ' BSs, simulation ' + str(i+1) + ')'
                save_as = str(t+1) +' BSs and ' + str(i+1) + ' simulation_' + config['map']['save_as']
                uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data,bs_index_data = load_position_data(t, i, raw_data)
                draw_map(uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data, title,config['map']['xlabel'], config['map']['ylabel'], config['map']['auto_scale'], config['map']['xlim'], config['map']['ylim'], config['map']['figsize'], config['map']['resolution'], save_as, config['map']['complete'],config['map']['grid'],time )
    elif config['map']['complete'] == False:
        uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data,bs_index_data = load_position_data(config['general']['bs_ue_min'], config['general']['s_min'], raw_data)
        draw_map(uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data, config['map']['title'],config['map']['xlabel'], config['map']['ylabel'], config['map']['auto_scale'], config['map']['xlim'], config['map']['ylim'], config['map']['figsize'], config['map']['resolution'], config['map']['save_as'], config['map']['complete'],config['map']['grid'],time)
    else:
        print('Complete just be True or False!')

else:
    print("The variable make just be 'map' or 'graph'!")
