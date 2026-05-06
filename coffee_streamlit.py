# Coffee Streamlit
# 5/5/26
# Birch

# %% Init
import numpy as np
import streamlit as st
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"

def temp_change(t, state):
    T, integral = state

    error = T_ideal - T
    P = Kp * error
    
    I = Ki * integral
    
    Q_heater = np.clip(
        P + I, 0, Q_h_max
    )  # clip the proportional between 0 and max
    
    Q_loss = h * A * (T - T_amb)

    dTdt = (Q_heater - Q_loss) / mc
    return dTdt, error


# %% Scipy

# @st.cache_data(show_time=True)
def scipy(T0,t_span,t_eval,method):
    sol = solve_ivp(
        temp_change, t_span=t_span, t_eval=t_eval, method=method, y0=[T0,0.0]
    )
    
    time = sol.t
    temp = sol.y[0, :]
    return [time, temp]


# %% Plotly

def line_graph(time, temp) -> go.Figure:
    fig = px.line(x=time, y=temp)
    fig.update_traces(
        line=dict(color="#704241", width=4),
        hovertemplate="%{x:.1f} seconds<br>%{y:.2f} C",
    )
    
    fig.update_layout(
        title=f"Coffee Temperature Change Over Time, Kp: {Kp} Ki: {Ki}",
        xaxis_title="Seconds (s)",
        yaxis_title="Temperature (C)",
        showlegend=False,
    )
    
    fig.add_hline(y=T_ideal, line_dash="dash", line_color="steelblue",annotation_text=f'Ideal Temp: {T_ideal:.1f}',annotation_position='top left')
    
    fig.add_hline(y=T_amb, line_dash="dash", line_color="green",annotation_text=f'Ambient Temp: {T_amb:.1f}',annotation_position='top left')
    
    return fig

#%% Streamlit

st.set_page_config(page_title="Coffee Heat Controller", layout="wide")

st.title("Coffee Heat Controller")

# T0 = 82.22  # C, roughly 180F
# T_ideal = 54.5  # C, roughly 130F
# T_amb = 25  # C
C_WATER = 4186  # J / kg C
# M = 380 / 1000  # Kg, 380g medium mug. Small mug would be 255g
# A = 0.015  # m^2, surface area of mug
# h = 200  # W/(M^2 C), heat transfer coefficient
METHODS = ['RK45', 'RK23', 'DOP853','Radau','BDF','LSODA']

DEFAULTS = {
    "T0": 82.22,
    "T_amb": 25.0,
    "T_ideal": 54.5,
    "M": 0.380,
    "A": 0.015,
    "h": 200,
    "Kp": 55.0,
    "Ki": 0.5,
    "Q_h_max": 200,
    "method": 'RK45',
}



# Kp = 55  # proportional
# Ki = 1
# Q_h_max = 200  # W

if __name__ == '__main__':
    
    with st.sidebar:
        st.header('Parameters')
        if st.button('Default parameters'):
            for key, val in DEFAULTS.items():
                st.session_state[key] = val
            st.rerun()
    
        st.subheader('Temperature')
        T0 = st.slider('Initial Temperature (C)',min_value=0.0,max_value=300.0,value=82.22,key='T0')
        T_ideal = st.slider('Target temperature (C)',
                    min_value=0.0,
                    max_value=300.0,
                    value=54.5,
                    key='T_ideal')
        T_amb = st.slider('Ambient temperature (C)',min_value=0.0,max_value=100.0,value=25.0,key='T_amb')
        
        st.subheader('Mug')
        M = st.slider('Mug mass (kg)',min_value=0.0,max_value=1.0,
                      step=.05,value=.380,key='M')
        A = st.slider('Mug surface area:',min_value=0.005,max_value=1.0,value=.015,step=.005,key='A')
        h = st.slider('Heat transfer coefficient',min_value=1,max_value=1000,value=200,
                      key='h')
        
        st.subheader('PI Controller')
        Kp = st.slider('Kp (Proportional)',min_value=0.0,max_value=500.0,value=55.0,step=0.5,key='Kp')
        Ki = st.slider('Ki (Integral)',min_value=0.0,max_value=10.0,step=.05,value=0.50,key='Ki')
        Q_h_max = st.slider('Max heater power (W)', min_value=0, max_value=600, step=10, value=200,key='Q_h_max')
        
        method = st.selectbox('Solver Method: ',METHODS,key='method')
        
    if 'runs' not in st.session_state:
        st.session_state['runs'] = []
    
    if st.button('Run',width='content'):
        mc = M * C_WATER
        tau = mc / (h*A)
        t_end = 8 * tau
        t_span = (0, t_end)
        t_eval = np.linspace(0, t_end, 8000)
        
        
        
        time, temp = scipy(T0,t_span,t_eval,method)
        
        run_num = len(st.session_state['runs']) + 1
        label = f"Run {run_num} - T0: {T0:.1f}C  Target: {T_ideal:.1f}C  Kp: {Kp}  Ki: {Ki}  Q_max: {Q_h_max}W"

        
        fig = line_graph(time,temp)
        st.session_state['runs'].append({
            "label": f"Run {run_num} - T0: {T0:.1f}C  Target: {T_ideal:.1f}C  Kp: {Kp}  Ki: {Ki}  Q_max: {Q_h_max}W",
            "time": time,
            "temp": temp,
            # snapshot the params so line_graph renders correctly for each run
            "T_ideal": T_ideal,
            "T_amb": T_amb,
            "Kp": Kp,
            "Ki": Ki,
        })
        
      
    if st.session_state['runs']:
        if st.button('Clear all runs'):
            st.session_state['runs'] = []
            st.rerun()
        
        for i, entry in enumerate(reversed(st.session_state["runs"])):
            st.caption(entry["label"])
            # Temporarily set globals so line_graph uses the snapshotted params
            T_ideal = entry["T_ideal"]
            T_amb   = entry["T_amb"]
            Kp      = entry["Kp"]
            Ki      = entry["Ki"]
            fig = line_graph(entry["time"], entry["temp"])
            st.plotly_chart(fig, width='content', key=f"run_{i}")

        
      
    else:
        st.info('Adjust these parameters then click Run to start')

