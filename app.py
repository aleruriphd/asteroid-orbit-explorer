"""
Asteroid Orbital Elements — Interactive Explorer
--------------------------------------------------
A Streamlit app for playing with the six classical orbital elements
(eccentricity, semi-major axis, inclination, longitude of the ascending
node, argument of periapsis, mean anomaly) and seeing their effect on
the orbit's shape and orientation in real time.

Run with:  streamlit run app.py
"""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

import orbit_math as om

# ----------------------------------------------------------------- palette --
BG        = "#0a0e1a"
PAPER     = "#0a0e1a"
GRID      = "#1c2540"
ORBIT     = "#4fc3f7"
REF_PLANE = "#ff9e57"
SUN       = "#ffd54f"
ASTEROID  = "#ff6b6b"
NODE_LINE = "#8de08d"
AUX       = "#7e8bd8"
ANGLE_ARC = "#f4f4f4"
TEXT      = "#eef1f8"
SUBTEXT   = "#9aa4c0"

st.set_page_config(page_title="Asteroid Orbital Elements", page_icon="🪐", layout="wide")

# ------------------------------------------------------------------ styling --
st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; }}
    section[data-testid="stSidebar"] {{ background-color: #0d1326; }}
    h1, h2, h3, p, label, .stMarkdown {{ color: {TEXT} !important; }}
    [data-testid="stMetricValue"] {{ color: {ORBIT}; }}
    [data-testid="stMetricLabel"] {{ color: {SUBTEXT} !important; }}
</style>
""", unsafe_allow_html=True)

st.title("🪐 Asteroid Orbital Elements — Interactive Explorer")
st.caption("Drag the sliders in the sidebar and watch the orbit respond. "
           "Distances are in arbitrary units (think “AU”) — only shape and orientation matter here.")

# ------------------------------------------------------------------ sidebar --
st.sidebar.header("Orbital elements")

e = st.sidebar.slider("Eccentricity  (e)", 0.0, 0.95, 0.35, 0.01,
                       help="0 = circle, closer to 1 = more elongated ellipse.")
a = st.sidebar.slider("Semi-major axis  (a)", 0.3, 3.0, 1.2, 0.05,
                       help="Half the length of the orbit's long axis — its overall size.")
inc_deg = st.sidebar.slider("Inclination  (i, °)", 0.0, 180.0, 25.0, 1.0,
                             help="Tilt of the orbital plane from the reference (ecliptic) plane.")
Omega_deg = st.sidebar.slider("Longitude of ascending node  (Ω, °)", 0.0, 360.0, 50.0, 1.0,
                               help="Swings the line of nodes around the reference direction.")
omega_deg = st.sidebar.slider("Argument of periapsis  (ω, °)", 0.0, 360.0, 60.0, 1.0,
                               help="Rotates the ellipse within its own tilted plane.")
M_deg = st.sidebar.slider("Mean anomaly  (M, °)", 0.0, 360.0, 90.0, 1.0,
                           help="Where the asteroid is along its orbit right now, as a uniformly-increasing angle.")

st.sidebar.markdown("---")
show_ref_plane = st.sidebar.checkbox("Show reference (ecliptic) plane", value=True)
show_aux_circle = st.sidebar.checkbox("Show auxiliary circle (mean-anomaly guide)", value=False)

# convert to radians
inc, Omega, omega, M = map(np.radians, (inc_deg, Omega_deg, omega_deg, M_deg))

state = om.asteroid_state(a, e, Omega, inc, omega, M)
q = a * (1 - e)   # perihelion distance
Q = a * (1 + e)   # aphelion distance

# ----------------------------------------------------------------- metrics --
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Perihelion distance (q)", f"{q:.2f}")
c2.metric("Aphelion distance (Q)", f"{Q:.2f}")
c3.metric("Current distance (r)", f"{state['r']:.2f}")
c4.metric("True anomaly (ν)", f"{np.degrees(state['nu']) % 360:.1f}°")
c5.metric("Eccentric anomaly (E)", f"{np.degrees(state['E']) % 360:.1f}°")

tab1, tab2, tab3 = st.tabs(["🌌 3D Orbit", "🥚 Eccentricity & Size", "🕒 Mean Anomaly"])


def base_layout(fig, scene=True, height=640):
    common = dict(
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(color=TEXT, size=13),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    )
    fig.update_layout(**common)
    return fig


# ============================================================ TAB 1: 3D ====
with tab1:
    fig = go.Figure()

    lim = max(1.15 * Q, 1.15)

    # reference plane -------------------------------------------------------
    if show_ref_plane:
        x, y, z, i_idx, j_idx, k_idx = om.disk_mesh((1, 0, 0), (0, 1, 0), radius=lim)
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=i_idx, j=j_idx, k=k_idx,
                                 color=REF_PLANE, opacity=0.08, name="reference plane",
                                 hoverinfo="skip", showscale=False))
        rx, ry, rz = om.ring_line((1, 0, 0), (0, 1, 0), radius=lim)
        fig.add_trace(go.Scatter3d(x=rx, y=ry, z=rz, mode="lines",
                                    line=dict(color=REF_PLANE, width=3),
                                    name="reference plane (ecliptic)"))
        fig.add_trace(go.Scatter3d(x=[0, lim], y=[0, 0], z=[0, 0], mode="lines+text",
                                    line=dict(color=REF_PLANE, width=4),
                                    text=["", "♈ reference dir."], textposition="top center",
                                    textfont=dict(color=REF_PLANE), name="vernal direction",
                                    showlegend=False))

    # orbital plane -----------------------------------------------------------
    u_orb, v_orb = om.orbital_plane_basis(Omega, inc)
    x, y, z, i_idx, j_idx, k_idx = om.disk_mesh(u_orb, v_orb, radius=lim)
    fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=i_idx, j=j_idx, k=k_idx,
                             color=ORBIT, opacity=0.10, name="orbital plane",
                             hoverinfo="skip", showscale=False))

    # line of nodes -------------------------------------------------------
    n_hat = om.node_line_direction(Omega)
    fig.add_trace(go.Scatter3d(
        x=[-n_hat[0] * lim, n_hat[0] * lim], y=[-n_hat[1] * lim, n_hat[1] * lim], z=[0, 0],
        mode="lines", line=dict(color=NODE_LINE, width=4, dash="dash"), name="line of nodes"))

    # orbit ellipse -----------------------------------------------------------
    ox, oy, oz = om.orbit_ellipse_points(a, e, Omega, inc, omega)
    fig.add_trace(go.Scatter3d(x=ox, y=oy, z=oz, mode="lines",
                                line=dict(color=ORBIT, width=6), name="orbit"))

    # auxiliary circle (optional) ---------------------------------------------
    if show_aux_circle:
        cx, cy, cz = om.ring_line(u_orb, v_orb, radius=a)
        # shift to Sun-at-focus frame: circle center sits at -e*a along periapsis dir
        peri_dir = om.perifocal_to_inertial(np.array([[1.0], [0], [0]]), Omega, inc, omega)[:, 0]
        shift = -peri_dir * (a * e)
        fig.add_trace(go.Scatter3d(x=cx + shift[0], y=cy + shift[1], z=cz + shift[2],
                                    mode="lines", line=dict(color=AUX, width=2, dash="dot"),
                                    name="auxiliary circle"))

    # Sun --------------------------------------------------------------------
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers",
                                marker=dict(size=10, color=SUN, line=dict(color="#ffe9a8", width=1)),
                                name="Sun"))

    # periapsis / ascending node markers --------------------------------------
    peri_pt = om.perifocal_to_inertial(np.array([[q], [0], [0]]), Omega, inc, omega)[:, 0]
    fig.add_trace(go.Scatter3d(x=[peri_pt[0]], y=[peri_pt[1]], z=[peri_pt[2]], mode="markers",
                                marker=dict(size=5, color=TEXT), name="periapsis"))
    asc_pt = n_hat * q
    fig.add_trace(go.Scatter3d(x=[asc_pt[0]], y=[asc_pt[1]], z=[asc_pt[2]], mode="markers",
                                marker=dict(size=5, color=NODE_LINE), name="ascending node"))

    # asteroid's current position ---------------------------------------------
    p = state["pos"]
    fig.add_trace(go.Scatter3d(x=[0, p[0]], y=[0, p[1]], z=[0, p[2]], mode="lines",
                                line=dict(color=ASTEROID, width=3), name="radius vector",
                                showlegend=False))
    fig.add_trace(go.Scatter3d(x=[p[0]], y=[p[1]], z=[p[2]], mode="markers",
                                marker=dict(size=8, color=ASTEROID), name="asteroid"))

    axis_style = dict(showbackground=False, showgrid=True, gridcolor=GRID,
                       zeroline=False, color=SUBTEXT, range=[-lim, lim])
    fig.update_layout(scene=dict(
        xaxis=axis_style, yaxis=axis_style, zaxis=dict(**{**axis_style, "range": [-lim * 0.7, lim * 0.7]}),
        aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.7),
        camera=dict(eye=dict(x=1.4, y=-1.4, z=0.9)),
        bgcolor=BG,
    ))
    fig = base_layout(fig, height=680)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Drag to rotate, scroll to zoom, double-click to reset the view.")


# ================================================== TAB 2: ECCENTRICITY ====
with tab2:
    st.subheader("Shape (e) & size (a) — flattened, in-plane view")
    fig2 = go.Figure()

    nu = np.linspace(0, 2 * np.pi, 400)
    p_ = a * (1 - e ** 2)
    r_ = p_ / (1 + e * np.cos(nu))
    x_, y_ = r_ * np.cos(nu), r_ * np.sin(nu)
    fig2.add_trace(go.Scatter(x=x_, y=y_, mode="lines", line=dict(color=ORBIT, width=3),
                              name=f"orbit  (e={e:.2f}, a={a:.2f})"))

    # comparison circle of the same semi-major axis
    th = np.linspace(0, 2 * np.pi, 200)
    fig2.add_trace(go.Scatter(x=a * np.cos(th), y=a * np.sin(th), mode="lines",
                              line=dict(color=SUBTEXT, width=1.5, dash="dot"),
                              name="reference circle (e=0, same a)"))

    fig2.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                              marker=dict(size=14, color=SUN, line=dict(color="#ffe9a8", width=1)),
                              name="Sun (focus)"))
    fig2.add_trace(go.Scatter(x=[q, -Q], y=[0, 0], mode="markers+text",
                              marker=dict(size=8, color=ASTEROID),
                              text=["perihelion", "aphelion"], textposition="top center",
                              textfont=dict(color=TEXT), name="apsides"))

    lim2 = 1.15 * Q
    fig2.update_xaxes(range=[-lim2, lim2 * 0.4], zeroline=False, showgrid=True, gridcolor=GRID, color=SUBTEXT,
                       scaleanchor="y", scaleratio=1)
    fig2.update_yaxes(range=[-lim2 * 0.75, lim2 * 0.75], zeroline=False, showgrid=True, gridcolor=GRID, color=SUBTEXT)
    fig2 = base_layout(fig2, height=560)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("e = 0 traces a perfect circle; as e climbs toward 1 the ellipse stretches and the Sun "
               "sits further from the ellipse's own center. a sets the overall size.")


# =================================================== TAB 3: MEAN ANOMALY ====
with tab3:
    st.subheader("Mean anomaly — fictitious uniform motion vs. the real orbit")
    fig3 = go.Figure()

    c = a * e
    Efull = np.linspace(0, 2 * np.pi, 400)
    b = a * np.sqrt(1 - e ** 2)
    fig3.add_trace(go.Scatter(x=a * np.cos(Efull) - c, y=b * np.sin(Efull), mode="lines",
                              line=dict(color=ORBIT, width=3), name="real orbit"))
    fig3.add_trace(go.Scatter(x=a * np.cos(Efull) - c, y=a * np.sin(Efull), mode="lines",
                              line=dict(color=AUX, width=1.5, dash="dot"), name="auxiliary circle"))

    N = 8
    Ms = np.linspace(0, 2 * np.pi, N, endpoint=False)
    Es = om.solve_eccentric_anomaly(Ms, e)
    xr, yr = a * np.cos(Es) - c, b * np.sin(Es)
    xf, yf = a * np.cos(Ms) - c, a * np.sin(Ms)
    fig3.add_trace(go.Scatter(x=xr, y=yr, mode="markers", marker=dict(size=6, color=ORBIT),
                              name="real position (8 equal time-steps)"))
    fig3.add_trace(go.Scatter(x=xf, y=yf, mode="markers", marker=dict(size=6, color=AUX),
                              name="fictitious point (equal M steps)"))

    fig3.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                              marker=dict(size=14, color=SUN, line=dict(color="#ffe9a8", width=1)),
                              name="Sun"))

    # current M marker (from the sidebar slider) --------------------------------
    Ef = om.solve_eccentric_anomaly(np.array([M]), e)[0]
    xr_cur, yr_cur = a * np.cos(Ef) - c, b * np.sin(Ef)
    xf_cur, yf_cur = a * np.cos(M) - c, a * np.sin(M)
    fig3.add_trace(go.Scatter(x=[xf_cur], y=[yf_cur], mode="markers", marker=dict(size=13, color=AUX,
                              line=dict(color=TEXT, width=1)), name="fictitious point (now)"))
    fig3.add_trace(go.Scatter(x=[xr_cur], y=[yr_cur], mode="markers", marker=dict(size=13, color=ASTEROID,
                              line=dict(color=TEXT, width=1)), name="asteroid (now)"))
    fig3.add_trace(go.Scatter(x=[0, xr_cur], y=[0, yr_cur], mode="lines",
                              line=dict(color=ASTEROID, width=1.5), showlegend=False))

    lim3 = 1.15 * a
    fig3.update_xaxes(range=[-lim3 - c, lim3], zeroline=False, showgrid=True, gridcolor=GRID, color=SUBTEXT,
                       scaleanchor="y", scaleratio=1)
    fig3.update_yaxes(range=[-lim3, lim3], zeroline=False, showgrid=True, gridcolor=GRID, color=SUBTEXT)
    fig3 = base_layout(fig3, height=560)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Mean anomaly M grows at a perfectly steady rate with time. The real asteroid (cyan/red) "
               "moves faster near perihelion and slower near aphelion, so it only matches the fictitious "
               "uniformly-moving point (purple) at perihelion and aphelion. Drag the M slider to move both "
               "at once.")
