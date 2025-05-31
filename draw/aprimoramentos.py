def covert_to_km (data=None):
  data = (np.array(data)*30)/1000
  return data
  

def load_media_data(axis=None, bs_ue_list=None, simulation_list=None, raw_data=None):

    uex_data = (np.array(uex_data)*30)/1000
    uey_data = (np.array(uey_data)*30)/1000
    bsx_data = (np.array(bsx_data)*30)/1000
    bsy_data = (np.array(bsy_data)*30)/1000
    uex_off_data = (np.array(uex_off_data)*30)/1000
    uey_off_data = (np.array(uey_off_data)*30)/1000
