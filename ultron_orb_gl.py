"""
ultron_orb_gl.py — Native OpenGL 3D Holographic Ultron Orb for PyQt6
====================================================================
A state-of-the-art GPU-accelerated 3D Holographic Ultron Orb HUD widget.
Replicates Sagar's 10-layer Ultron Orb with:
  1. Dense wireframe sphere with 32 latitude rings and 24 meridians
  2. 4 Bright Cross Meridian bands (the iconic Ultron "plus" shape)
  3. Bright Equator band with multi-line falloff
  4. 28 Curved surface grid panels (tech patches)
  5. Secondary floating outer shell with offset arcs
  6. Hexagonal data nodes and surface tech markers
  7. Counter-rotating inner geodesic core with 8 helical spirals
  8. Rapidly rotating wireframe icosahedron hot core with center pulse
  9. 220 Orbiting debris particles on tilted planes
  10. 1200 Floating atmospheric dust/star particles
  11. Dual sweeping vertical and horizontal scan rings
  12. Multi-pass holographic bloom glow simulation with additive blending
  13. Fluid momentum/inertia mouse dragging (flick to spin)
  14. Parallax mouse tracking & hover glow
  15. Click shockwave expansion ripple
  16. High-tech QPainter HUD overlay (TITAN telemetry, status pill, audio visualizer)
"""

from __future__ import annotations
import math
import random
import time
import numpy as np
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QSurfaceFormat, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False


class UltronOrbGL(QOpenGLWidget):
    """
    Native OpenGL 3D Holographic Ultron Orb HUD widget for Mark-L (TITAN).
    High-density sci-fi aesthetics matching Sagar's Ultron Orb with full
    hardware acceleration, rich cyan/blue holographic palette, momentum physics,
    and responsive HUD telemetry overlay.
    """

    def __init__(self, assistant_name: str = "TITAN", parent=None):
        fmt = QSurfaceFormat()
        fmt.setSamples(4)          # 4x MSAA
        fmt.setSwapInterval(1)     # VSync (60 Hz)
        QSurfaceFormat.setDefaultFormat(fmt)

        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Public state (HUD API)
        self.muted = False
        self.speaking = False
        self.state = "INITIALISING"
        self._assistant_name = assistant_name
        self.on_clicked = None

        # Camera & 3D Transform
        self._rot_x = 0.20
        self._rot_y = 0.0
        self._vel_x = 0.0
        self._vel_y = 0.008      # Initial smooth rotation speed
        self._target_zoom = 5.2
        self._zoom = 5.2
        self._scale = 1.0
        self._tgt_scale = 1.0

        # Mouse interaction & Momentum
        self._is_dragging = False
        self._last_mouse_pos = None
        self._mouse_down_pos = None
        self._hover_pos = QPointF(0, 0)
        self._hover_glow = 0.0
        self._parallax_x = 0.0
        self._parallax_y = 0.0

        # Animation & Physics
        self._tick = 0
        self._time = 0.0
        self._shockwaves: list[dict] = []   # Expanding click ripple rings
        self._eq_bars = [random.uniform(0.1, 0.4) for _ in range(32)]

        # Precomputed Geometry
        self._lat_rings: list[tuple[list[tuple[float, float, float]], bool]] = []
        self._meridians: list[tuple[list[tuple[float, float, float]], bool]] = []
        self._cross_meridians: list[list[tuple[list[tuple[float, float, float]], float]]] = []
        self._equator_band: list[tuple[list[tuple[float, float, float]], float]] = []
        self._grid_panels: list[list[list[tuple[float, float, float]]]] = []
        self._sec_lat_arcs: list[tuple[list[tuple[float, float, float]], float]] = []
        self._sec_lon_arcs: list[tuple[list[tuple[float, float, float]], float]] = []
        self._hex_nodes: list[tuple[float, float, float, float]] = []
        self._spirals: list[list[tuple[float, float, float]]] = []
        self._inner_lat_rings: list[list[tuple[float, float, float]]] = []
        self._inner_meridians: list[list[tuple[float, float, float]]] = []
        self._ico_verts: list[tuple[float, float, float]] = []
        self._ico_edges: list[tuple[int, int]] = []
        self._debris: list[dict] = []
        self._dust: list[tuple[float, float, float, float, float]] = []

        # 60 FPS Render Loop
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(16)

    # ── Geometry Generation (Precomputed once) ───────────────────────

    def _generate_geometry(self):
        """Pre-compute all complex wireframe vertex data for maximum performance."""
        R1 = 2.0   # Main outer shell radius
        R2 = 2.14  # Secondary outer shell radius
        R3 = 0.90  # Inner core radius

        # 1. Outer Shell Latitude Rings (32 rings)
        self._lat_rings = []
        for i in range(-15, 16):
            lat = (i / 15.0) * (math.pi / 2.0) * 0.95
            r = R1 * math.cos(lat)
            y = R1 * math.sin(lat)
            pts = []
            for j in range(96):
                a = (j / 95.0) * math.pi * 2.0
                pts.append((r * math.cos(a), y, r * math.sin(a)))
            is_major = (i % 3 == 0)
            self._lat_rings.append((pts, is_major))

        # 2. Outer Shell Meridians (24 meridians)
        self._meridians = []
        for i in range(24):
            lon = (i / 24.0) * math.pi * 2.0
            pts = []
            for j in range(96):
                lat = (j / 95.0) * math.pi - (math.pi / 2.0)
                pts.append((
                    R1 * math.cos(lat) * math.cos(lon),
                    R1 * math.sin(lat),
                    R1 * math.cos(lat) * math.sin(lon)
                ))
            is_major = (i % 6 == 0)
            self._meridians.append((pts, is_major))

        # 3. 4 Bright Cross Meridian Bands (The iconic Ultron "Plus" Cross)
        # 4 clusters at 0, 90, 180, 270 deg. Each cluster has 16 parallel lines with center falloff
        self._cross_meridians = []
        CROSS_LINES = 16
        CROSS_SPREAD = 0.22  # radians width
        for c in range(4):
            base_lon = (c / 4.0) * math.pi * 2.0
            band = []
            for j in range(CROSS_LINES):
                t = (j / (CROSS_LINES - 1)) * 2.0 - 1.0  # -1.0 to 1.0
                offset = (t * CROSS_SPREAD) / 2.0
                lon = base_lon + offset
                falloff = 1.0 - abs(t) * 0.70  # Bright center, gentle fade
                pts = []
                for k in range(96):
                    lat = (k / 95.0) * math.pi - (math.pi / 2.0)
                    pts.append((
                        R1 * math.cos(lat) * math.cos(lon),
                        R1 * math.sin(lat),
                        R1 * math.cos(lat) * math.sin(lon)
                    ))
                band.append((pts, falloff))
            self._cross_meridians.append(band)

        # 4. Bright Equator Band (Horizontal waist belt: 18 dense parallel lines)
        self._equator_band = []
        EQ_LINES = 18
        EQ_SPREAD = 0.30
        for j in range(EQ_LINES):
            t = (j / (EQ_LINES - 1)) * 2.0 - 1.0
            offset = (t * EQ_SPREAD) / 2.0
            falloff = 1.0 - abs(t) * 0.65
            r = R1 * math.cos(offset)
            y = R1 * math.sin(offset)
            pts = []
            for k in range(96):
                a = (k / 95.0) * math.pi * 2.0
                pts.append((r * math.cos(a), y, r * math.sin(a)))
            self._equator_band.append((pts, falloff))

        # 5. Surface Grid Panels (24 curved tech patches on the sphere)
        self._grid_panels = []
        random.seed(42)  # Deterministic seed for pleasing layout
        for _ in range(24):
            lat_center = (random.random() - 0.5) * math.pi * 0.75
            lon_center = random.random() * math.pi * 2.0
            span = 0.16 + random.random() * 0.16
            divs = 3
            panel_lines = []
            # Horizontal panel lines
            for di in range(divs + 1):
                plat = lat_center - span/2.0 + (di / divs) * span
                pr = (R1 + 0.015) * math.cos(plat)
                py = (R1 + 0.015) * math.sin(plat)
                line_pts = []
                for dj in range(16):
                    plon = lon_center - span/2.0 + (dj / 15.0) * span
                    line_pts.append((pr * math.cos(plon), py, pr * math.sin(plon)))
                panel_lines.append(line_pts)
            # Vertical panel lines
            for dj in range(divs + 1):
                plon = lon_center - span/2.0 + (dj / divs) * span
                line_pts = []
                for di in range(16):
                    plat = lat_center - span/2.0 + (di / 15.0) * span
                    pr = (R1 + 0.015) * math.cos(plat)
                    py = (R1 + 0.015) * math.sin(plat)
                    line_pts.append((pr * math.cos(plon), py, pr * math.sin(plon)))
                panel_lines.append(line_pts)
            self._grid_panels.append(panel_lines)

        # 6. Secondary Outer Shell (Offset partial floating arcs at R2 = 2.14)
        self._sec_lat_arcs = []
        for _ in range(18):
            lat = (random.random() - 0.5) * math.pi * 0.85
            start_lon = random.random() * math.pi * 2.0
            arc_len = 0.4 + random.random() * 1.0
            r = R2 * math.cos(lat)
            y = R2 * math.sin(lat)
            pts = []
            for j in range(40):
                a = start_lon + (j / 39.0) * arc_len
                pts.append((r * math.cos(a), y, r * math.sin(a)))
            self._sec_lat_arcs.append((pts, 0.25 + random.random() * 0.4))

        self._sec_lon_arcs = []
        for _ in range(14):
            lon = random.random() * math.pi * 2.0
            start_lat = (random.random() - 0.5) * math.pi * 0.75
            arc_len = 0.3 + random.random() * 0.7
            pts = []
            for j in range(30):
                lat = start_lat + (j / 29.0) * arc_len
                pts.append((
                    R2 * math.cos(lat) * math.cos(lon),
                    R2 * math.sin(lat),
                    R2 * math.cos(lat) * math.sin(lon)
                ))
            self._sec_lon_arcs.append((pts, 0.2 + random.random() * 0.35))

        # 7. Hex Nodes / Surface Tech Markers (Glowing diamond markers at key intersections)
        self._hex_nodes = []
        for _ in range(40):
            phi = math.acos(2.0 * random.random() - 1.0)
            theta = random.random() * math.pi * 2.0
            r = R1 + 0.02
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.cos(phi)
            z = r * math.sin(phi) * math.sin(theta)
            size = 2.5 + random.random() * 3.5
            self._hex_nodes.append((x, y, z, size))

        # 8. Inner Core Spirals (8 helical geodesics winding inside R3 = 0.9)
        self._spirals = []
        for s in range(8):
            pts = []
            turns = 3.2 + random.random() * 1.5
            phase = (s / 8.0) * math.pi * 2.0
            for j in range(160):
                t = j / 159.0
                lat = t * math.pi - (math.pi / 2.0)
                lon = t * turns * math.pi * 2.0 + phase
                pts.append((
                    R3 * math.cos(lat) * math.cos(lon),
                    R3 * math.sin(lat),
                    R3 * math.cos(lat) * math.sin(lon)
                ))
            self._spirals.append(pts)

        # Inner latitude rings & meridians
        self._inner_lat_rings = []
        for i in range(-5, 6):
            lat = (i / 5.0) * (math.pi / 2.0) * 0.85
            r = R3 * math.cos(lat)
            y = R3 * math.sin(lat)
            pts = [(r * math.cos(a), y, r * math.sin(a))
                   for a in [k / 60.0 * math.pi * 2.0 for k in range(61)]]
            self._inner_lat_rings.append(pts)

        self._inner_meridians = []
        for i in range(12):
            lon = (i / 12.0) * math.pi * 2.0
            pts = [(R3 * math.cos(lat) * math.cos(lon),
                    R3 * math.sin(lat),
                    R3 * math.cos(lat) * math.sin(lon))
                   for lat in [(k / 60.0 * math.pi - math.pi/2.0) for k in range(61)]]
            self._inner_meridians.append(pts)

        # 9. Center Icosahedron Core
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        raw = [
            (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
            (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
            (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
        ]
        norm = math.sqrt(1 + phi*phi)
        self._ico_verts = [(v[0]/norm*0.28, v[1]/norm*0.28, v[2]/norm*0.28) for v in raw]
        self._ico_edges = [
            (0,11),(0,5),(0,1),(0,7),(0,10),
            (1,5),(1,7),(1,8),(1,9),
            (2,3),(2,4),(2,6),(2,10),(2,11),
            (3,4),(3,6),(3,8),(3,9),
            (4,5),(4,9),
            (5,9),(5,11),
            (6,7),(6,8),(6,10),
            (7,8),(7,10),
            (8,9),
            (10,11),
        ]

        # 10. Orbiting Debris Particles (220 satellites on tilted planes)
        self._debris = []
        for _ in range(220):
            self._debris.append({
                "r": 1.25 + random.random() * 3.8,
                "speed": (0.12 + random.random() * 0.55) * (1 if random.random() > 0.5 else -1),
                "tilt_x": (random.random() - 0.5) * math.pi * 0.85,
                "tilt_z": (random.random() - 0.5) * math.pi * 0.45,
                "phase": random.random() * math.pi * 2.0,
                "size": 1.8 + random.random() * 3.2,
                "brightness": 0.4 + random.random() * 0.6,
                "is_hot": random.random() > 0.75,
            })

        # 11. Atmospheric Dust Cloud (1200 glowing ambient particles)
        self._dust = []
        for _ in range(1200):
            rr = 0.6 + (random.random() ** 0.55) * 6.5
            theta = random.random() * math.pi * 2.0
            phi_a = math.acos(2.0 * random.random() - 1.0)
            x = rr * math.sin(phi_a) * math.cos(theta)
            y = rr * math.cos(phi_a)
            z = rr * math.sin(phi_a) * math.sin(theta)
            brightness = 0.15 + random.random() * 0.65
            size = 1.0 + random.random() * 2.0
            self._dust.append((x, y, z, brightness, size))

    # ── OpenGL Lifecycle ─────────────────────────────────────────────

    def initializeGL(self):
        # Ultra dark blue-black background matching Mark-L's C.BG (#05070c)
        glClearColor(0.02, 0.03, 0.05, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for true holographic glow
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_MULTISAMPLE)
        self._generate_geometry()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        w, h = self.width(), self.height()
        aspect = w / h if h > 0 else 1.0
        t = self._time

        # ── Color Palette Matrix (Dynamic Cyberpunk Hologram) ────────
        # Rich layered tones: Hot White / Electric Neon Cyan / Vibrant Hologram Blue / Royal Azure
        if self.muted:
            c_hot    = (1.00, 0.75, 0.78, 1.0)
            c_bright = (1.00, 0.28, 0.38, 1.0)  # Fiery red-pink #ff4d5e
            c_mid    = (0.85, 0.18, 0.26, 0.75)
            c_dim    = (0.45, 0.08, 0.14, 0.25)
            c_deep   = (0.22, 0.04, 0.08, 0.12)
            c_core   = (1.00, 0.50, 0.55, 0.95)
        elif self.speaking:
            c_hot    = (1.00, 1.00, 1.00, 1.0)  # Pure White Surge
            c_bright = (0.13, 0.92, 1.00, 1.0)  # Hyper Electric Cyan #22e0ff
            c_mid    = (0.25, 0.72, 1.00, 0.85) # High-energy Blue #3fa9ff
            c_dim    = (0.12, 0.40, 0.80, 0.35)
            c_deep   = (0.05, 0.18, 0.45, 0.18)
            c_core   = (1.00, 1.00, 1.00, 1.0)
        elif self.state == "THINKING":
            c_hot    = (0.95, 0.88, 1.00, 1.0)
            c_bright = (0.70, 0.45, 1.00, 1.0)  # Cosmic Neon Purple #9d6bff
            c_mid    = (0.52, 0.30, 0.90, 0.75)
            c_dim    = (0.28, 0.14, 0.55, 0.30)
            c_deep   = (0.12, 0.06, 0.30, 0.15)
            c_core   = (0.85, 0.70, 1.00, 0.95)
        elif self.state == "LISTENING":
            c_hot    = (0.85, 1.00, 0.92, 1.0)
            c_bright = (0.12, 0.92, 0.55, 1.0)  # Emerald Matrix #1fe08a
            c_mid    = (0.10, 0.75, 0.42, 0.75)
            c_dim    = (0.06, 0.38, 0.22, 0.30)
            c_deep   = (0.03, 0.18, 0.10, 0.15)
            c_core   = (0.60, 1.00, 0.80, 0.95)
        else:
            # Default / IDLE: Glorious Electric Cyan & Deep Sci-Fi Hologram Blue
            # Exactly matching Mark-L's C.ACC=#22e0ff, C.PRI=#3fa9ff
            c_hot    = (0.92, 0.98, 1.00, 1.0)  # Ice White
            c_bright = (0.13, 0.88, 1.00, 1.0)  # Electric Cyan (#22e0ff)
            c_mid    = (0.25, 0.66, 1.00, 0.75) # Hologram Blue (#3fa9ff)
            c_dim    = (0.10, 0.35, 0.70, 0.28) # Azure depth
            c_deep   = (0.04, 0.16, 0.38, 0.14) # Ambient space
            c_core   = (0.75, 0.95, 1.00, 0.95)

        # ── Setup 3D Projection & Camera ─────────────────────────────
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        fov = 52.0
        near, far = 0.1, 150.0
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        glMultMatrixf([
            f/aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far+near)/(near-far), -1,
            0, 0, 2*far*near/(near-far), 0
        ])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Camera positioning with subtle interactive parallax tilt
        cam_y = -0.25 + self._parallax_y * 0.3
        cam_x = self._parallax_x * 0.3
        glTranslatef(cam_x, cam_y, -self._zoom)

        # Rotate scene based on user drag / physics inertia
        glRotatef(math.degrees(self._rot_x), 1, 0, 0)
        glRotatef(math.degrees(self._rot_y), 0, 1, 0)

        # Scale animation (breathing pulse)
        scale = self._scale
        glScalef(scale, scale, scale)

        # ═══════════════════════════════════════════════
        # LAYER 1: BASE OUTER SPHERE (Latitude & Meridians)
        # ═══════════════════════════════════════════════
        for pts, is_major in self._lat_rings:
            col = c_mid if is_major else c_dim
            alpha = (0.65 if is_major else 0.18) * (1.0 + self._hover_glow * 0.3)
            glColor4f(col[0], col[1], col[2], alpha)
            glLineWidth(1.8 if is_major else 0.9)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        for pts, is_major in self._meridians:
            col = c_mid if is_major else c_deep
            alpha = (0.60 if is_major else 0.14) * (1.0 + self._hover_glow * 0.3)
            glColor4f(col[0], col[1], col[2], alpha)
            glLineWidth(1.6 if is_major else 0.8)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 2: 4 BRIGHT CROSS MERIDIANS (The Iconic Ultron Cross)
        # ═══════════════════════════════════════════════
        for band in self._cross_meridians:
            for pts, falloff in band:
                alpha = 0.85 * falloff * (1.0 + self._hover_glow * 0.25)
                col = c_hot if falloff > 0.85 else (c_bright if falloff > 0.5 else c_mid)
                glColor4f(col[0], col[1], col[2], alpha)
                glLineWidth(2.4 if falloff > 0.85 else 1.5)
                glBegin(GL_LINE_STRIP)
                for vx, vy, vz in pts:
                    glVertex3f(vx, vy, vz)
                glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 3: BRIGHT EQUATOR BELT (Horizontal Glowing Band)
        # ═══════════════════════════════════════════════
        for pts, falloff in self._equator_band:
            alpha = 0.80 * falloff * (1.0 + self._hover_glow * 0.25)
            col = c_hot if falloff > 0.85 else (c_bright if falloff > 0.5 else c_mid)
            glColor4f(col[0], col[1], col[2], alpha)
            glLineWidth(2.2 if falloff > 0.85 else 1.4)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 4: SURFACE GRID PANELS (Curved Tech Patches)
        # ═══════════════════════════════════════════════
        glColor4f(c_bright[0], c_bright[1], c_bright[2], 0.32)
        glLineWidth(1.1)
        for panel in self._grid_panels:
            for line_pts in panel:
                glBegin(GL_LINE_STRIP)
                for vx, vy, vz in line_pts:
                    glVertex3f(vx, vy, vz)
                glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 5: SECONDARY OUTER SHELL (Floating Arcs at R = 2.14)
        # ═══════════════════════════════════════════════
        glPushMatrix()
        glRotatef(math.degrees(t * 0.05), 0, 1, 0)
        glRotatef(math.degrees(-t * 0.03), 1, 0, 0)

        for pts, alpha_base in self._sec_lat_arcs:
            glColor4f(c_bright[0], c_bright[1], c_bright[2], alpha_base * 0.6)
            glLineWidth(1.4)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        for pts, alpha_base in self._sec_lon_arcs:
            glColor4f(c_mid[0], c_mid[1], c_mid[2], alpha_base * 0.5)
            glLineWidth(1.2)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()
        glPopMatrix()

        # ═══════════════════════════════════════════════
        # LAYER 6: HEX NODES & SURFACE TECH MARKERS
        # ═══════════════════════════════════════════════
        glPointSize(3.5)
        glBegin(GL_POINTS)
        for idx, (x, y, z, psize) in enumerate(self._hex_nodes):
            pulse = 0.5 + 0.5 * math.sin(t * 2.5 + idx * 0.8)
            glColor4f(c_hot[0], c_hot[1], c_hot[2], 0.4 + pulse * 0.5)
            glVertex3f(x, y, z)
        glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 7: INNER GEODESIC CORE (8 Helical Spirals)
        # ═══════════════════════════════════════════════
        glPushMatrix()
        glRotatef(math.degrees(-t * 0.25), 0, 1, 0)
        glRotatef(math.degrees(t * 0.12), 1, 0, 0)

        # Violet-accented helical spirals
        c_spiral = (0.50 * c_bright[0] + 0.50, 0.40 * c_bright[1] + 0.30, 1.00, 1.0)
        for idx, pts in enumerate(self._spirals):
            a = 0.45 + 0.25 * math.sin(t * 1.5 + idx * 0.8)
            glColor4f(c_spiral[0], c_spiral[1], c_spiral[2], a)
            glLineWidth(1.6)
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        # Inner latitude rings & meridians
        glColor4f(c_dim[0], c_dim[1], c_dim[2], 0.28)
        glLineWidth(1.0)
        for pts in self._inner_lat_rings:
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()
        for pts in self._inner_meridians:
            glBegin(GL_LINE_STRIP)
            for vx, vy, vz in pts:
                glVertex3f(vx, vy, vz)
            glEnd()

        glPopMatrix()

        # ═══════════════════════════════════════════════
        # LAYER 8: CENTER ICOSAHEDRON (Fast-Spinning Hot Core)
        # ═══════════════════════════════════════════════
        surge = (max(0, math.sin(t * 0.6)) ** 5) * 1.5 + (max(0, math.sin(t * 0.9 + 2.0)) ** 8) * 2.0
        ico_scale = (1.0 + surge * 0.5) * (1.35 if self.speaking else 1.0)

        glPushMatrix()
        glRotatef(math.degrees(t * 1.1), 1, 0.5, 0.2)
        glRotatef(math.degrees(t * 1.6), 0, 1, 0.5)
        glScalef(ico_scale, ico_scale, ico_scale)

        glColor4f(c_core[0], c_core[1], c_core[2], min(1.0, 0.65 + surge * 0.35))
        glLineWidth(2.4)
        glBegin(GL_LINES)
        for e1, e2 in self._ico_edges:
            v1, v2 = self._ico_verts[e1], self._ico_verts[e2]
            glVertex3f(*v1)
            glVertex3f(*v2)
        glEnd()

        # Center glowing plasma star
        glPointSize(8.0 + surge * 12.0)
        glColor4f(c_hot[0], c_hot[1], c_hot[2], min(1.0, 0.55 + surge * 0.45))
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()

        glPopMatrix()

        # ═══════════════════════════════════════════════
        # LAYER 9: ORBITING DEBRIS PARTICLES (Satellites)
        # ═══════════════════════════════════════════════
        glPointSize(2.8)
        glBegin(GL_POINTS)
        for d in self._debris:
            a = t * d["speed"] + d["phase"]
            orbit_r = d["r"]
            x = orbit_r * math.cos(a) * math.cos(d["tilt_x"])
            y = orbit_r * math.sin(d["tilt_x"]) * math.sin(a * 0.8) + math.sin(a * 0.3 + d["tilt_z"]) * 0.2
            z = orbit_r * math.sin(a) * math.cos(d["tilt_z"])
            col = c_hot if d["is_hot"] else c_bright
            glColor4f(col[0], col[1], col[2], d["brightness"] * 0.75)
            glVertex3f(x, y, z)
        glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 10: ATMOSPHERIC STAR/DUST CLOUD
        # ═══════════════════════════════════════════════
        glPushMatrix()
        glRotatef(math.degrees(t * 0.02), 0, 1, 0)
        glPointSize(1.8)
        glBegin(GL_POINTS)
        for x, y, z, brightness, psize in self._dust:
            flicker = 0.7 + 0.3 * math.sin(t * 3.0 + x * 2.0)
            glColor4f(c_mid[0], c_mid[1], c_bright[2], brightness * flicker * 0.45)
            glVertex3f(x, y, z)
        glEnd()
        glPopMatrix()

        # ═══════════════════════════════════════════════
        # LAYER 11: DUAL SWEEPING SCAN RINGS
        # ═══════════════════════════════════════════════
        R1 = 2.0
        # Scan ring 1: Vertical sweeping ring
        scan_y1 = math.sin(t * 0.5) * R1
        scan_r1 = math.sqrt(max(0, R1*R1 - scan_y1*scan_y1))
        if scan_r1 > 0.01:
            glColor4f(c_hot[0], c_hot[1], c_hot[2], 0.40 * (scan_r1 / R1))
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            for j in range(80):
                a = (j / 80.0) * math.pi * 2.0
                glVertex3f(scan_r1 * math.cos(a), scan_y1, scan_r1 * math.sin(a))
            glEnd()

        # Scan ring 2: Counter-sweeping core ring
        scan_y2 = math.sin(t * 0.75 + 1.5) * 0.90
        scan_r2 = math.sqrt(max(0, 0.81 - scan_y2*scan_y2))
        if scan_r2 > 0.01:
            glColor4f(c_bright[0], c_bright[1], c_bright[2], 0.35 * (scan_r2 / 0.90))
            glLineWidth(1.4)
            glBegin(GL_LINE_LOOP)
            for j in range(60):
                a = (j / 60.0) * math.pi * 2.0
                glVertex3f(scan_r2 * math.cos(a), scan_y2, scan_r2 * math.sin(a))
            glEnd()

        # ═══════════════════════════════════════════════
        # LAYER 12: CLICK SHOCKWAVE EXPANSION RIPPLES
        # ═══════════════════════════════════════════════
        active_shockwaves = []
        for sw in self._shockwaves:
            sw["r"] += 0.08
            sw["alpha"] *= 0.92
            if sw["alpha"] > 0.02 and sw["r"] < 5.0:
                active_shockwaves.append(sw)
                sw_r = sw["r"]
                glColor4f(c_hot[0], c_hot[1], c_hot[2], sw["alpha"])
                glLineWidth(3.0)
                glBegin(GL_LINE_LOOP)
                for j in range(64):
                    a = (j / 64.0) * math.pi * 2.0
                    glVertex3f(sw_r * math.cos(a), 0, sw_r * math.sin(a))
                glEnd()
        self._shockwaves = active_shockwaves

        # ═══════════════════════════════════════════════
        # LAYER 13: MULTI-PASS HOLOGRAPHIC BLOOM GLOW
        # ═══════════════════════════════════════════════
        bloom_strength = 2.0 + math.sin(t * 0.8) * 0.5 + self._hover_glow * 0.8
        for pass_i in range(3):
            glow_scale = 1.0 + (pass_i + 1) * 0.014
            glow_alpha = (0.09 / (pass_i + 1)) * bloom_strength

            glPushMatrix()
            glScalef(glow_scale, glow_scale, glow_scale)

            # Glow envelope on major latitudes
            for pts, is_major in self._lat_rings:
                if not is_major:
                    continue
                glColor4f(c_bright[0], c_bright[1], c_bright[2], glow_alpha)
                glLineWidth(4.0 + pass_i * 2.5)
                glBegin(GL_LINE_STRIP)
                for vx, vy, vz in pts:
                    glVertex3f(vx, vy, vz)
                glEnd()

            # Glow envelope on cross bands
            for band in self._cross_meridians:
                center_pts, _ = band[len(band)//2]
                glColor4f(c_hot[0], c_hot[1], c_hot[2], glow_alpha * 1.3)
                glLineWidth(4.5 + pass_i * 2.0)
                glBegin(GL_LINE_STRIP)
                for vx, vy, vz in center_pts:
                    glVertex3f(vx, vy, vz)
                glEnd()

            glPopMatrix()

        # ═══════════════════════════════════════════════
        # LAYER 14: 2D HUD OVERLAY (TITAN Telemetry, Status, Equalizer)
        # ═══════════════════════════════════════════════
        self._paint_hud_overlay(w, h, c_bright, c_hot, c_mid)

    def _paint_hud_overlay(self, w: int, h: int, c_bright, c_hot, c_mid):
        """Crisp antialiased 2D Sci-Fi HUD overlay rendered directly on the OpenGL surface."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        cx, cy = w / 2.0, h / 2.0

        # 1. Subtle High-Tech Corner Reticle Brackets ┌ ┐ └ ┘
        b_len = 16
        b_margin = 18
        bracket_col = QColor(63, 169, 255, 60)
        p.setPen(QPen(bracket_col, 1.5))
        # Top-Left
        p.drawLine(QPointF(b_margin, b_margin + b_len), QPointF(b_margin, b_margin))
        p.drawLine(QPointF(b_margin, b_margin), QPointF(b_margin + b_len, b_margin))
        # Top-Right
        p.drawLine(QPointF(w - b_margin - b_len, b_margin), QPointF(w - b_margin, b_margin))
        p.drawLine(QPointF(w - b_margin, b_margin), QPointF(w - b_margin, b_margin + b_len))
        # Bottom-Left
        p.drawLine(QPointF(b_margin, h - b_margin - b_len), QPointF(b_margin, h - b_margin))
        p.drawLine(QPointF(b_margin, h - b_margin), QPointF(b_margin + b_len, h - b_margin))
        # Bottom-Right
        p.drawLine(QPointF(w - b_margin - b_len, h - b_margin), QPointF(w - b_margin, h - b_margin))
        p.drawLine(QPointF(w - b_margin, h - b_margin - b_len), QPointF(w - b_margin, h - b_margin))

        # 2. Top Holographic Header & Assistant Tag
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        p.setPen(QColor(113, 136, 173, 160))
        p.drawText(QRectF(0, 14, w, 18), Qt.AlignmentFlag.AlignCenter,
                   f"[ {self._assistant_name} // 3D HOLOGRAPHIC CORE v2.0 ]")

        # 3. Status Badge (Pill at bottom)
        badge_y = h - 56
        if self.muted:
            status_text = "⊘  MUTED"
            badge_color = QColor(255, 77, 94, 220)
            glow_color = QColor(255, 77, 94, 40)
        elif self.speaking:
            status_text = "●  SPEAKING"
            badge_color = QColor(34, 224, 255, 250)
            glow_color = QColor(34, 224, 255, 60)
        elif self.state == "THINKING":
            status_text = "◈  THINKING..."
            badge_color = QColor(157, 107, 255, 230)
            glow_color = QColor(157, 107, 255, 50)
        elif self.state == "LISTENING":
            status_text = "●  LISTENING"
            badge_color = QColor(31, 224, 138, 230)
            glow_color = QColor(31, 224, 138, 50)
        else:
            status_text = f"●  {self.state}"
            badge_color = QColor(63, 169, 255, 210)
            glow_color = QColor(63, 169, 255, 40)

        # Status badge container
        pill_w = 160
        pill_rect = QRectF(cx - pill_w/2.0, badge_y, pill_w, 24)
        p.setPen(QPen(badge_color, 1.2))
        p.setBrush(QBrush(glow_color))
        p.drawRoundedRect(pill_rect, 12, 12)

        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.setPen(badge_color)
        p.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status_text)

        # 4. Animated 32-Band Audio Equalizer Array
        eq_y = badge_y + 30
        num_bars = 32
        bar_w = 4
        spacing = 2
        total_eq_w = num_bars * (bar_w + spacing) - spacing
        start_x = cx - total_eq_w / 2.0

        p.setPen(Qt.PenStyle.NoPen)
        for i in range(num_bars):
            bh = int(self._eq_bars[i] * 20.0)
            bx = start_x + i * (bar_w + spacing)
            by = eq_y - bh / 2.0
            if self.speaking or self.state == "LISTENING":
                bar_col = badge_color
            else:
                bar_col = QColor(63, 169, 255, 80)
            p.setBrush(QBrush(bar_col))
            p.drawRoundedRect(QRectF(bx, by, bar_w, max(2, bh)), 2, 2)

        p.end()

    # ── Physics & Animation Step (60 FPS) ────────────────────────────

    def _step(self):
        self._tick += 1
        self._time += 0.016

        # Apply Momentum Physics when not dragging
        if not self._is_dragging:
            self._rot_y += self._vel_y
            self._rot_x += self._vel_x
            # Silky damping towards idle velocity
            idle_vel_y = 0.022 if self.speaking else (0.015 if self.state == "THINKING" else 0.007)
            self._vel_y += (idle_vel_y - self._vel_y) * 0.04
            self._vel_x *= 0.94  # Smooth pitch damping
        else:
            # While dragging, track velocity
            pass

        # Pitch clamping (-80 deg to +80 deg)
        self._rot_x = max(-1.4, min(1.4, self._rot_x))

        # Smooth Zoom Interpolation
        self._zoom += (self._target_zoom - self._zoom) * 0.15

        # Scale Breathing & Speech Pulse
        if self.speaking:
            self._tgt_scale = random.uniform(1.03, 1.10)
        elif self.muted:
            self._tgt_scale = 0.96
        else:
            self._tgt_scale = 1.0 + 0.018 * math.sin(self._tick * 0.05)
        self._scale += (self._tgt_scale - self._scale) * 0.16

        # Audio Equalizer Bar Dynamics
        for i in range(32):
            if self.speaking:
                target_h = random.uniform(0.3, 1.0)
            elif self.state == "LISTENING":
                target_h = 0.2 + 0.4 * abs(math.sin(self._tick * 0.2 + i * 0.35))
            else:
                target_h = 0.12 + 0.08 * math.sin(self._tick * 0.08 + i * 0.2)
            self._eq_bars[i] += (target_h - self._eq_bars[i]) * 0.3

        self.update()

    # ── High-End Interactivity & Touch/Mouse Handling ────────────────

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._last_mouse_pos = ev.position()
            self._mouse_down_pos = ev.position()
            self._vel_x = 0.0
            self._vel_y = 0.0

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            if self._mouse_down_pos:
                dist = (ev.position() - self._mouse_down_pos).manhattanLength()
                if dist < 6:
                    # Click Trigger: Trigger shockwave pulse ripple
                    self._shockwaves.append({"r": 0.3, "alpha": 0.85})
            self._mouse_down_pos = None
            self._last_mouse_pos = None

    def mouseMoveEvent(self, ev):
        pos = ev.position()
        w, h = self.width(), self.height()

        # Parallax tilt towards cursor
        if w > 0 and h > 0:
            norm_x = (pos.x() / w) * 2.0 - 1.0
            norm_y = (pos.y() / h) * 2.0 - 1.0
            self._parallax_x += (norm_x - self._parallax_x) * 0.1
            self._parallax_y += (norm_y - self._parallax_y) * 0.1

        self._hover_glow = min(1.0, self._hover_glow + 0.15)

        # Dragging with smooth velocity transfer
        if self._is_dragging and self._last_mouse_pos:
            delta = pos - self._last_mouse_pos
            dx = delta.x() * 0.007
            dy = delta.y() * 0.005
            self._rot_y += dx
            self._rot_x += dy
            # Record release momentum
            self._vel_y = dx
            self._vel_x = dy
            self._last_mouse_pos = pos

    def leaveEvent(self, ev):
        self._hover_glow = 0.0
        self._parallax_x = 0.0
        self._parallax_y = 0.0

    def wheelEvent(self, ev):
        delta = ev.angleDelta().y()
        if delta > 0:
            self._target_zoom = max(2.6, self._target_zoom * 0.90)
        else:
            self._target_zoom = min(14.0, self._target_zoom * 1.10)

    def mouseDoubleClickEvent(self, ev):
        """Double click resets camera to home view."""
        self._rot_x = 0.20
        self._rot_y = 0.0
        self._vel_x = 0.0
        self._vel_y = 0.008
        self._target_zoom = 5.2
        self._shockwaves.append({"r": 0.1, "alpha": 1.0})


# ── Graceful Fallback if PyOpenGL is absent ───────────────────────

if not HAS_OPENGL:
    class UltronOrbGL(QWidget):
        def __init__(self, assistant_name="TITAN", parent=None):
            super().__init__(parent)
            self.muted = False
            self.speaking = False
            self.state = "INITIALISING"
            self._assistant_name = assistant_name
            self.on_clicked = None

        def paintEvent(self, _):
            p = QPainter(self)
            p.fillRect(self.rect(), QColor(5, 7, 12))
            p.setPen(QColor(63, 169, 255))
            p.setFont(QFont("Segoe UI", 12))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "PyOpenGL not installed.\npip install PyOpenGL PyOpenGL_accelerate")
