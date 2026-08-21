# Asteroid Orbital Elements — Interactive Explorer

A small Streamlit app for playing with the six classical orbital elements
and seeing their effect on an orbit's shape and orientation in real time.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL it prints (usually http://localhost:8501).

## What's inside

- **Sidebar sliders** for eccentricity (e), semi-major axis (a),
  inclination (i), longitude of the ascending node (Ω), argument of
  periapsis (ω), and mean anomaly (M).
- **🌌 3D Orbit tab** — a rotatable/zoomable view showing the reference
  (ecliptic) plane, the tilted orbital plane, the line of nodes, the
  ascending node, periapsis, the Sun, and the asteroid's live position.
- **🥚 Eccentricity & Size tab** — a flattened, in-plane view isolating
  just e and a.
- **🕒 Mean Anomaly tab** — the real orbit vs. a fictitious uniformly-moving
  point on the auxiliary circle, showing why they only coincide at
  perihelion and aphelion.

`orbit_math.py` holds the orbital-mechanics helpers (Kepler's equation
solver, the perifocal→inertial rotation, and the plane/mesh geometry) —
no external astronomy library required, just NumPy.
