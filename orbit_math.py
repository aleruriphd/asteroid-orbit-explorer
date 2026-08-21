"""Orbital-mechanics helpers shared across the app's views.

All angles in are radians internally; the app converts from the
degree-based sliders at the UI boundary. Distances are in arbitrary
units (think "AU") since only shape/orientation matter here, not a
real asteroid's true scale.
"""
import numpy as np


def solve_eccentric_anomaly(M, e, iters=80):
    """Solve Kepler's equation M = E - e sin(E) for E via Newton's method.
    M may be a scalar or array (radians)."""
    M = np.asarray(M, dtype=float)
    E = np.copy(M)
    for _ in range(iters):
        f = E - e * np.sin(E) - M
        fp = 1 - e * np.cos(E)
        E = E - f / fp
    return E


def eccentric_to_true(E, e):
    return 2.0 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2.0),
                             np.sqrt(1 - e) * np.cos(E / 2.0))


def perifocal_position(nu, r):
    """Position in the perifocal (orbital) frame: pericenter along +x."""
    x = r * np.cos(nu)
    y = r * np.sin(nu)
    z = np.zeros_like(x)
    return np.stack([x, y, z], axis=0)


def Rz(ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def Rx(ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def perifocal_to_inertial(pts, Omega, inc, omega):
    """3-1-3 Euler sequence: argument of periapsis, then inclination
    (about the line of nodes), then longitude of ascending node."""
    R = Rz(Omega) @ Rx(inc) @ Rz(omega)
    return R @ pts


def orbit_ellipse_points(a, e, Omega, inc, omega, n=360):
    """Full ellipse, in inertial (reference-frame) coordinates."""
    nu = np.linspace(0, 2 * np.pi, n)
    p = a * (1 - e ** 2)
    r = p / (1 + e * np.cos(nu))
    peri = perifocal_position(nu, r)
    return perifocal_to_inertial(peri, Omega, inc, omega)


def asteroid_state(a, e, Omega, inc, omega, M):
    """Given mean anomaly M (radians), return a dict with the asteroid's
    current position (inertial frame), distance from Sun, and the
    eccentric/true anomaly for display."""
    E = solve_eccentric_anomaly(M, e)
    nu = eccentric_to_true(E, e)
    r = a * (1 - e * np.cos(E))
    pos_peri = perifocal_position(np.array([nu]), np.array([r]))
    pos_inertial = perifocal_to_inertial(pos_peri, Omega, inc, omega)[:, 0]
    return {
        "E": E, "nu": nu, "r": r,
        "pos": pos_inertial,
    }


def node_line_direction(Omega):
    return np.array([np.cos(Omega), np.sin(Omega), 0.0])


def orbital_plane_basis(Omega, inc):
    """Orthonormal in-plane basis (u along the ascending node, v
    completing the tilted plane) for the orbital plane."""
    u = node_line_direction(Omega)
    v = np.array([-np.sin(Omega) * np.cos(inc), np.cos(Omega) * np.cos(inc), np.sin(inc)])
    return u, v


def disk_mesh(u, v, radius=1.0, n=64):
    """Vertices + triangle indices for a filled circular disk spanned by
    orthonormal in-plane vectors u, v (centered at the origin). Returns
    (x, y, z, i, j, k) ready for a Plotly Mesh3d trace."""
    u = np.asarray(u); v = np.asarray(v)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = np.array([radius * (np.cos(t) * u + np.sin(t) * v) for t in th])
    verts = np.vstack([[0, 0, 0], ring])  # index 0 = center
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    i_idx, j_idx, k_idx = [], [], []
    for k in range(n):
        i_idx.append(0)
        j_idx.append(k + 1)
        k_idx.append(((k + 1) % n) + 1)
    return x, y, z, i_idx, j_idx, k_idx


def ring_line(u, v, radius=1.0, n=100):
    """Boundary circle of a plane disk, for a crisp outline (Scatter3d line)."""
    u = np.asarray(u); v = np.asarray(v)
    th = np.linspace(0, 2 * np.pi, n)
    pts = np.array([radius * (np.cos(t) * u + np.sin(t) * v) for t in th])
    return pts[:, 0], pts[:, 1], pts[:, 2]
