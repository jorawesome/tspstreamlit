import streamlit as st


import pandas as pd
import numpy
#import itertools
#import datetime
#from python_tsp.exact import solve_tsp_dynamic_programming,solve_tsp_brute_force
#from copy import deepcopy
#from datetime import datetime, timedelta, time
#import math
import random
import os.path
#import matplotlib.pyplot as plt

#Data importeren
pad = 'dummydataset2.xlsx'
pad_tijd_matrix = 'time_matrix_pd.p'
pad_afstand_matrix = 'distance_matrix_pd.p'
locaties_zonder_hub_pad = 'locaties_zonder_hub.p'

# 👇 Your function that runs the algorithm (you should implement the full logic in this function)
def run_my_algorithm(dag_gekozen,cap_bak,cap_kar):

    # Ophalen en brengen gescheiden
    ophalen = pd.read_excel(pad, sheet_name='ophalen')
    ophalen['halen_check'] = 'h'
    brengen = pd.read_excel(pad, sheet_name='brengen')
    brengen['brengen_check'] = 'b'
    #bestellingen = pd.concat([ophalen,brengen])

    locaties = pd.read_excel(pad, sheet_name='locaties')
    locaties['index_locatie'] = locaties.index
    locaties_zonder_hub = locaties[locaties['Type']!='Hub']
    hubs = locaties[locaties['Type']=='Hub']['volledig_adres'].tolist()
    locaties_zonder_hub = pd.read_pickle(locaties_zonder_hub_pad)

    ophalen['datum_tijd_begin'] = ophalen.apply(lambda row: pd.Timestamp.combine(row['datum_rijden'].date(), row['tijd_begin']), axis=1)
    ophalen['datum_tijd_deadline'] = ophalen.apply(lambda row: pd.Timestamp.combine(row['datum_deadline'].date(), row['tijd_deadline']), axis=1)
    brengen['datum_tijd_begin'] = brengen.apply(lambda row: pd.Timestamp.combine(row['datum_rijden'].date(), row['tijd_begin']), axis=1)
    brengen['datum_tijd_deadline'] = brengen.apply(lambda row: pd.Timestamp.combine(row['datum_deadline'].date(), row['tijd_deadline']), axis=1)

    locaties_col_nodig = locaties_zonder_hub[['Type','adres_ID','volledig_adres','index_locatie','Dichtstbijzijnde hub','Reistijd naar hub (s)']]
    ophalen = pd.merge(ophalen, locaties_col_nodig, on="adres_ID")
    brengen = pd.merge(brengen, locaties_col_nodig, on="adres_ID")

    #Over de dataset itereren en bepalen met bakken en/of karren hoeveel sets het in de auto inneemt per bestelling.
    for i in range(len(ophalen)):
        # Check of ziekenhuis (z) of kliniek (k)
        if ophalen.loc[i,'Type']=='Kliniek':
            #Als kliniek dan bakken gebruiken.
            ophalen.at[i,'bakken/karren']='bakken'
            totaal_bakken = ophalen.loc[i,'instrumentensets']//cap_bak+1
            ophalen.at[i,'capaciteit_benodigd'] = totaal_bakken*cap_bak
        else:
            #Als ziekenhuis dan karren gebruiken.
            ophalen.at[i,'bakken/karren']='karren'
            totaal_karren = ophalen.loc[i,'instrumentensets']//cap_kar+1
            ophalen.at[i,'capaciteit_benodigd'] = totaal_karren*cap_kar

    for i in range(len(brengen)):
        # Check of ziekenhuis (z) of kliniek (k)
        if brengen.loc[i,'Type']=='Kliniek':
            #Als kliniek dan bakken gebruiken.
            brengen.at[i,'bakken/karren']='bakken'
            totaal_bakken = brengen.loc[i,'instrumentensets']//cap_bak+1
            brengen.at[i,'capaciteit_benodigd'] = totaal_bakken*cap_bak
        else:
            #Als ziekenhuis dan karren gebruiken.
            brengen.at[i,'bakken/karren']='karren'
            totaal_karren = brengen.loc[i,'instrumentensets']//cap_kar+1
            brengen.at[i,'capaciteit_benodigd'] = totaal_karren*cap_kar

    #Alle dagen van ophalen en brengen opvragen.
    dagen_brengen = list(set(brengen['datum_rijden']))
    dagen_ophalen = list(set(ophalen['datum_rijden']))
    dagen_brengen.sort()
    dagen_ophalen.sort()

    #Dataframes per dag
    dataframes_dagen_ophalen = {k: ophalen.loc[(ophalen['datum_rijden']==k) & (ophalen['halen_check']=='h')] for k in dagen_ophalen}
    #dataframes_dagen_brengen = {k: brengen.loc[(brengen['datum_rijden']==k) & (brengen['brengen_check']=='b')] for k in dagen_brengen}

    output_dag = dataframes_dagen_ophalen[dagen_ophalen[dag_gekozen]]

    return output_dag

# Streamlit UI
st.title("🔧 Variabelen aanpassen en algoritme uitvoeren")

with st.form("variable_editor"):
    st.subheader("Wijzig de onderstaande waarden")

    #start_dag = st.number_input("Start dag", value=0)
    start_dag = st.selectbox("Start dag", options=[0, 1])
    cap_bak = st.number_input("Capaciteit bak", value=6)
    cap_kar = st.number_input("Capaciteit kar", value=20)
    submitted = st.form_submit_button("🚀 Start algoritme")

# Run and display output
if submitted:
    st.info("Algoritme wordt uitgevoerd...")
    out1 = run_my_algorithm(start_dag,cap_bak,cap_kar)
    st.success("✅ Uitvoering voltooid!")
    st.dataframe(out1)
    #st.write("**pairs (eerste 5):**", out2[:5])
    #st.write("**done_merged_total (laatste):**", out3[-1] if out3 else "Leeg")
