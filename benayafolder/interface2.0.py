

"""
still have many changes to make but this is a good base.
"""


"""
Arcade dashboard: categorization-style pie (x, y, z, e), sidebar stats, AI report page.
Wire your real lists into main() or construct AppWindow(x, y, z, e) from your pipeline.
"""
from __future__ import annotations

import arcade
import math

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Categorization overview"

SIDEBAR_WIDTH = 260
SIDEBAR_PAD = 18
DIVIDER_GREY = (120, 118, 128)

# Pie slice colors — purple / dusty blue / lavender (+ fourth tone), mockup-inspired
PIE_COLORS = (
    (130, 90, 180),   # x — medium purple
    (95, 130, 175),   # y — dusty blue
    (200, 185, 230),  # z — light lavender
    (160, 120, 200),  # e — accent purple
)

OUTLINE_COLOR = (18, 18, 22)
OUTLINE_WIDTH = 2
# Smoother arcs than Arcade default (128); scale with slice angle
PIE_ARC_SEG_PER_DEG = 3.5
PIE_ARC_SEGMENTS_CAP = 720
PIE_OUTLINE_SEGMENTS = 720
# Radial lines start slightly off center so thick strokes don’t stack into a blob
PIE_RADIAL_INSET = 0.04

# Sidebar copy — replace with strings from categorization / reporting when you hook data
STATS_HEADER = "random stats"
STATS_BODY_EXTRA = "more stats"

# Second page — connect final report text here
AI_REPORT_TITLE = "AI report"
AI_REPORT_BODY = (
    "Placeholder for your final report.\n"
    "Replace this string with output from your report module.\n\n"
    "You can still show scalars: see x, y, z, e on the dashboard."
)


class AppWindow(arcade.Window):
    VIEW_DASH = 0
    VIEW_REPORT = 1

    def __init__(self, x, y, z, e):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            resizable=False,
            antialiasing=True,
            samples=8,
        )
        self.set_mouse_visible(True)

        self.data_x = x
        self.data_y = y
        self.data_z = z
        self.data_e = e

        self.labels = ("x", "y", "z", "e")
        self._recompute_totals()

        self.active_page = self.VIEW_DASH
        self.elapsed = 0.0

        margin = 16
        self.ai_report_btn = (
            margin,
            margin,
            margin + 168,
            margin + 44,
        )
        self.back_btn = (
            margin,
            SCREEN_HEIGHT - margin - 44,
            margin + 120,
            SCREEN_HEIGHT - margin,
        )

        self._btn_hover_ai = False
        self._btn_hover_back = False

    def _recompute_totals(self):
        self.data_values = [
            sum(self.data_x),
            sum(self.data_y),
            sum(self.data_z),
            sum(self.data_e),
        ]

    def on_update(self, delta_time: float):
        self.elapsed += delta_time

    def _draw_moving_background(self):
        t = self.elapsed
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (22, 18, 38))

        blobs = [
            ((90, 70, 140), 220, 0.15, 0.11),
            ((70, 100, 160), 180, -0.09, 0.13),
            ((120, 90, 180), 200, 0.12, -0.08),
            ((60, 80, 130), 160, -0.14, 0.10),
            ((100, 85, 150), 140, 0.08, 0.15),
        ]
        for i, (base_rgb, r_base, vx, vy) in enumerate(blobs):
            ox = math.sin(t * vx + i) * (SCREEN_WIDTH * 0.35) + SCREEN_WIDTH * 0.5
            oy = math.cos(t * vy + i * 0.7) * (SCREEN_HEIGHT * 0.28) + SCREEN_HEIGHT * 0.5
            pulse = 0.92 + 0.08 * math.sin(t * 0.7 + i)
            r = r_base * pulse
            rr, gg, bb = base_rgb
            arcade.draw_circle_filled(ox, oy, r, (rr, gg, bb, 55))
            arcade.draw_circle_filled(ox * 0.96, oy * 1.04, r * 0.55, (rr + 30, gg + 20, bb, 35))

        for j in range(14):
            sx = (j * 97 + t * 28) % (SCREEN_WIDTH + 40) - 20
            sy = (j * 53 + math.sin(t * 0.4 + j) * 18) % (SCREEN_HEIGHT + 40) - 20
            arcade.draw_circle_filled(sx, sy, 2.2, (255, 255, 255, 28))

    def _main_width(self):
        return SCREEN_WIDTH - SIDEBAR_WIDTH

    def _draw_sidebar(self):
        x0 = self._main_width()
        arcade.draw_lbwh_rectangle_filled(x0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT, (248, 246, 252))
        arcade.draw_line(x0, 0, x0, SCREEN_HEIGHT, DIVIDER_GREY, 2)

        hx0 = x0 + SIDEBAR_PAD
        hx1 = SCREEN_WIDTH - SIDEBAR_PAD
        header_h = 110
        arcade.draw_lbwh_rectangle_filled(hx0, SCREEN_HEIGHT - SIDEBAR_PAD - header_h, hx1 - hx0, header_h, (255, 255, 255))
        arcade.draw_lbwh_rectangle_outline(
            hx0,
            SCREEN_HEIGHT - SIDEBAR_PAD - header_h,
            hx1 - hx0,
            header_h,
            (200, 198, 210),
            1,
        )

        arcade.Text(
            STATS_HEADER,
            hx0 + 8,
            SCREEN_HEIGHT - SIDEBAR_PAD - 24,
            (45, 42, 58),
            13,
            width=hx1 - hx0 - 16,
            multiline=True,
        ).draw()

        sx = sum(self.data_x)
        sy = sum(self.data_y)
        sz = sum(self.data_z)
        se = sum(self.data_e)
        body_lines = (
            f"x → {sx}\n"
            f"y → {sy}\n"
            f"z → {sz}\n"
            f"e → {se}\n\n"
            f"{STATS_BODY_EXTRA}"
        )
        body_top = SCREEN_HEIGHT - SIDEBAR_PAD - header_h - 20
        arcade.Text(
            body_lines,
            hx0 + 8,
            body_top,
            (55, 52, 68),
            12,
            width=hx1 - hx0 - 16,
            multiline=True,
            anchor_y="top",
        ).draw()

    def _draw_pie(self, center_x: float, center_y: float, radius: float):
        total = sum(self.data_values)
        if total <= 0:
            arcade.Text(
                "Totals are zero — check x, y, z, e",
                center_x,
                center_y,
                (255, 255, 255),
                16,
                anchor_x="center",
                anchor_y="center",
            ).draw()
            return

        start_angle = 0.0
        for i, value in enumerate(self.data_values):
            if value <= 0:
                continue
            fraction = value / total
            angle_extent = fraction * 360.0
            end_angle = start_angle + angle_extent

            seg = max(
                48,
                min(
                    PIE_ARC_SEGMENTS_CAP,
                    int(angle_extent * PIE_ARC_SEG_PER_DEG + 0.5),
                ),
            )
            arcade.draw_arc_filled(
                center_x=center_x,
                center_y=center_y,
                width=radius * 2,
                height=radius * 2,
                color=PIE_COLORS[i],
                start_angle=start_angle,
                end_angle=end_angle,
                tilt_angle=0,
                num_segments=seg,
            )

            rad_start = math.radians(start_angle)
            rin = max(2.0, radius * PIE_RADIAL_INSET)
            ix = center_x + rin * math.cos(rad_start)
            iy = center_y + rin * math.sin(rad_start)
            px = center_x + radius * math.cos(rad_start)
            py = center_y + radius * math.sin(rad_start)
            arcade.draw_line(ix, iy, px, py, OUTLINE_COLOR, OUTLINE_WIDTH)

            mid_angle = start_angle + angle_extent * 0.5
            rad_mid = math.radians(mid_angle)
            label = f"{self.labels[i]}\n{int(round(fraction * 100))}%"
            tx = center_x + radius * 0.62 * math.cos(rad_mid)
            ty = center_y + radius * 0.62 * math.sin(rad_mid)
            arcade.Text(
                label,
                tx,
                ty,
                OUTLINE_COLOR,
                13,
                width=max(72, int(radius * 0.55)),
                anchor_x="center",
                anchor_y="center",
                bold=True,
                multiline=True,
                align="center",
            ).draw()

            start_angle = end_angle

        arcade.draw_circle_outline(
            center_x,
            center_y,
            radius,
            OUTLINE_COLOR,
            OUTLINE_WIDTH,
            num_segments=PIE_OUTLINE_SEGMENTS,
        )

    def _rect_contains(self, rect, mx: float, my: float) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= mx <= x2 and y1 <= my <= y2

    def _draw_button(self, rect, label: str, hover: bool, primary: bool = True):
        x1, y1, x2, y2 = rect
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w / 2, y1 + h / 2
        if primary:
            fill = (120, 85, 185) if not hover else (140, 105, 205)
            border = (40, 30, 70)
        else:
            fill = (230, 228, 240) if not hover else (210, 208, 225)
            border = (90, 88, 105)

        arcade.draw_lbwh_rectangle_filled(x1, y1, w, h, fill)
        arcade.draw_lbwh_rectangle_outline(x1, y1, w, h, border, 2)
        arcade.Text(
            label,
            cx,
            cy,
            (255, 255, 255) if primary else (35, 32, 48),
            14,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

    def on_draw(self):
        self.clear()
        self._draw_moving_background()

        if self.active_page == self.VIEW_DASH:
            mw = self._main_width()
            arcade.draw_lbwh_rectangle_filled(0, 0, mw, SCREEN_HEIGHT, (255, 255, 255, 38))

            cx = mw * 0.48
            cy = SCREEN_HEIGHT * 0.52
            r = min(mw, SCREEN_HEIGHT) * 0.28
            self._draw_pie(cx, cy, r)

            arcade.Text(
                "Categorization",
                mw // 2,
                SCREEN_HEIGHT - 36,
                (255, 255, 255),
                22,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            ).draw()

            self._draw_sidebar()
            self._draw_button(self.ai_report_btn, "ai report", self._btn_hover_ai, primary=True)
        else:
            overlay = (14, 12, 26, 230)
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, overlay)

            arcade.Text(
                AI_REPORT_TITLE,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - 72,
                (255, 255, 255),
                26,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            ).draw()

            arcade.Text(
                AI_REPORT_BODY,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 40,
                (235, 232, 245),
                15,
                width=SCREEN_WIDTH - 120,
                multiline=True,
                align="center",
                anchor_x="center",
                anchor_y="center",
            ).draw()

            sx = sum(self.data_x)
            sy = sum(self.data_y)
            sz = sum(self.data_z)
            se = sum(self.data_e)
            arcade.Text(
                f"x={sx}  y={sy}  z={sz}  e={se}",
                SCREEN_WIDTH / 2,
                100,
                (200, 195, 220),
                13,
                anchor_x="center",
                anchor_y="center",
            ).draw()

            self._draw_button(self.back_btn, "← back", self._btn_hover_back, primary=False)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.active_page == self.VIEW_DASH:
            self._btn_hover_ai = self._rect_contains(self.ai_report_btn, x, y)
            self._btn_hover_back = False
        else:
            self._btn_hover_back = self._rect_contains(self.back_btn, x, y)
            self._btn_hover_ai = False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.active_page == self.VIEW_DASH:
            if self._rect_contains(self.ai_report_btn, x, y):
                self.active_page = self.VIEW_REPORT
        else:
            if self._rect_contains(self.back_btn, x, y):
                self.active_page = self.VIEW_DASH


def main():
    # Demo data — replace with your categorization lists
    x = [7]
    y = [12]
    z = [80]
    e = [3]

    window = AppWindow(x, y, z, e)
    arcade.run()


if __name__ == "__main__":
    main()
