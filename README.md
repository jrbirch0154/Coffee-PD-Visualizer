# Coffee Heat Controller

A Streamlit app that simulates a PI-controlled mug warmer using real heat transfer physics. Adjust controller gains, mug properties, and heater power to see how the system responds. Compare multiple runs side by side!

## Link
[https://coffee-controller.streamlit.app/](https://coffee-controller.streamlit.app/)

## What it does

The app models a coffee mug losing heat to its environment, with a PI controller driving a heater to maintain a target temperature. The underlying ODE is:

```
dT/dt = (Q_heater - Q_loss) / mc

Q_loss   = h · A · (T - T_amb) -> Natural heat loss
Q_heater = clip(Kp · error + Ki · ∫error dt, 0, Q_max) -> added heat from heater
```

The simulation time span is automatically calculated from the system's thermal time constant (`τ = mc / h·A`), so the plot always shows enough time for the system to settle.

## Parameters

| Parameter | Description |
|---|---|
| **T0** | Initial coffee temperature (°C) |
| **T_amb** | Ambient room temperature (°C) |
| **T_ideal** | Target temperature to hold (°C) |
| **M** | Mug mass (kg) - affects thermal inertia |
| **A** | Mug surface area (m²) - affects heat loss rate |
| **h** | Heat transfer coefficient (W/m²·°C) |
| **Kp** | Proportional gain - reacts to current error |
| **Ki** | Integral gain - eliminates steady-state error |
| **Q_max** | Maximum heater power (W) - hard power budget |
| **Solver** | SciPy ODE solver method (RK45, BDF, etc.) |

## Things to try

- **Set Kp and Ki = 0** Watch what happens with no PI controller. The temperature slowly falls to room temp
- **Crank Ki too high** to watch integral windup cause overshoot and oscillation
- **Lower Q_max** to see the controller saturate and lose the battle against heat loss
- **Increase M** with a fixed Q_max to see a heavier mug overwhelm the heater's power budget
- **Run multiple configurations** and compare them - all previous runs stay on screen until you clear them

## Stack

- [Streamlit](https://streamlit.io) - UI and session state
- [SciPy](https://scipy.org) `solve_ivp` - ODE solver
- [Plotly](https://plotly.com/python/) - interactive charts
