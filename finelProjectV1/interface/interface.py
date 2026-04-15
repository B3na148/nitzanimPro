from __future__ import annotations

import arcade
import math
import json

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Categorization overview"

SIDEBAR_WIDTH = 260
SIDEBAR_PAD = 18
DIVIDER_GREY = (120, 118, 128)

# Pie slice colors — added a 5th color (warm pink/purple) for "h"
PIE_COLORS = (
    (130, 90, 180),   # x — medium purple
    (95, 130, 175),   # y — dusty blue
    (200, 185, 230),  # z — light lavender
    (160, 120, 200),  # e — accent purple
    (220, 110, 180),  # h — warm pink/purple (New)
)

OUTLINE_COLOR = (18, 18, 22)
OUTLINE_WIDTH = 2
PIE_RADIAL_INSET = 0.04

STATS_HEADER = "random stats"
STATS_BODY_EXTRA = "more stats"

AI_REPORT_TITLE = "AI report"
with open(r'C:\Programing\nitzanim\ornitz\server\final_report.json', 'r') as file:
    data = json.load(file)
jsonreport = data['summary']['ai_verdict']

AI_REPORT_BODY = (
    jsonreport
)


class AppWindow(arcade.Window):
    VIEW_DASH = 0
    VIEW_REPORT = 1

    def __init__(self, x, y, z, e, h): # Added h here
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
        self.data_h = h # New data member

        self.labels = ("Education", "Games", "Entertainment", "Adult", "Other")
        self._recompute_totals()

        self.active_page = self.VIEW_DASH
        self.elapsed = 0.0

        margin = 16
        self.ai_report_btn = (margin, margin, margin + 168, margin + 44)
        self.back_btn = (margin, SCREEN_HEIGHT - margin - 44, margin + 120, SCREEN_HEIGHT - margin)

        self._btn_hover_ai = False
        self._btn_hover_back = False

    def _recompute_totals(self):
        # Added h to the value list
        self.data_values = [
            sum(self.data_x),
            sum(self.data_y),
            sum(self.data_z),
            sum(self.data_e),
            sum(self.data_h),
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

        arcade.Text(STATS_HEADER, hx0 + 8, SCREEN_HEIGHT - SIDEBAR_PAD - 24, (45, 42, 58), 13, width=hx1 - hx0 - 16, multiline=True).draw()

        sx, sy, sz, se, sh = self.data_values
        body_lines = (
            f"Education → {sx:.2f}\n"
            f"Games → {sy:.2f}\n"
            f"Entertainment → {sz:.2f}\n"
            f"Adult → {se:.2f}\n"
            f"Other → {sh:.2f}\n\n"
            f"{STATS_BODY_EXTRA}"
        )
        body_top = SCREEN_HEIGHT - SIDEBAR_PAD - header_h - 20
        arcade.Text(body_lines, hx0 + 8, body_top, (55, 52, 68), 12, width=hx1 - hx0 - 16, multiline=True, anchor_y="top").draw()

    def _draw_pie(self, center_x: float, center_y: float, radius: float):
        total = sum(self.data_values)
        if total <= 0:
            arcade.Text("Totals are zero", center_x, center_y, (255, 255, 255), 16, anchor_x="center", anchor_y="center").draw()
            return

        arcade.draw_circle_filled(center_x, center_y, radius + OUTLINE_WIDTH, OUTLINE_COLOR, num_segments=360)

        slices_data = []
        start_angle = 0.0
        for i, value in enumerate(self.data_values):
            if value <= 0: continue
            fraction = value / total
            angle_extent = fraction * 360.0
            end_angle = start_angle + angle_extent
            slices_data.append((i, fraction, start_angle, end_angle))
            start_angle = end_angle

        # Draw Slices
        for i, fraction, start_angle, end_angle in slices_data:
            arcade.draw_arc_filled(center_x, center_y, radius*2, radius*2, PIE_COLORS[i], start_angle, end_angle + 0.5, 0, 360)

        # Draw Lines and Labels
        for i, fraction, start_angle, end_angle in slices_data:
            rad_start = math.radians(start_angle)
            rin = max(2.0, radius * PIE_RADIAL_INSET)
            arcade.draw_line(center_x + rin * math.cos(rad_start), center_y + rin * math.sin(rad_start),
                             center_x + (radius - 0.5) * math.cos(rad_start), center_y + (radius - 0.5) * math.sin(rad_start), OUTLINE_COLOR, OUTLINE_WIDTH)

            mid_angle = start_angle + (end_angle - start_angle) * 0.5
            rad_mid = math.radians(mid_angle)
            label = f"{self.labels[i]}\n{int(round(fraction * 100))}%"
            arcade.Text(label, center_x + radius * 0.62 * math.cos(rad_mid), center_y + radius * 0.62 * math.sin(rad_mid),
                        OUTLINE_COLOR, 13, width=max(72, int(radius * 0.55)), anchor_x="center", anchor_y="center", bold=True, multiline=True, align="center").draw()

        arcade.draw_circle_filled(center_x, center_y, OUTLINE_WIDTH * 2, OUTLINE_COLOR)

    def _rect_contains(self, rect, mx: float, my: float) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= mx <= x2 and y1 <= my <= y2

    def _draw_button(self, rect, label: str, hover: bool, primary: bool = True):
        x1, y1, x2, y2 = rect
        cx, cy = x1 + (x2-x1)/2, y1 + (y2-y1)/2
        fill = (120, 85, 185) if primary and not hover else (140, 105, 205) if primary else (230, 228, 240) if not hover else (210, 208, 225)
        arcade.draw_lbwh_rectangle_filled(x1, y1, x2-x1, y2-y1, fill)
        arcade.draw_lbwh_rectangle_outline(x1, y1, x2-x1, y2-y1, (40, 30, 70) if primary else (90, 88, 105), 2)
        arcade.Text(label, cx, cy, (255, 255, 255) if primary else (35, 32, 48), 14, anchor_x="center", anchor_y="center", bold=True).draw()

    def on_draw(self):
        self.clear()
        self._draw_moving_background()

        if self.active_page == self.VIEW_DASH:
            mw = self._main_width()
            arcade.draw_lbwh_rectangle_filled(0, 0, mw, SCREEN_HEIGHT, (255, 255, 255, 38))
            self._draw_pie(mw * 0.48, SCREEN_HEIGHT * 0.52, min(mw, SCREEN_HEIGHT) * 0.28)
            arcade.Text("Categorization", mw // 2, SCREEN_HEIGHT - 36, (255, 255, 255), 22, anchor_x="center", anchor_y="center", bold=True).draw()
            self._draw_sidebar()
            self._draw_button(self.ai_report_btn, "ai report", self._btn_hover_ai, primary=True)
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (14, 12, 26, 230))
            arcade.Text(AI_REPORT_TITLE, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 72, (255, 255, 255), 26, anchor_x="center", anchor_y="center", bold=True).draw()
            arcade.Text(AI_REPORT_BODY, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, (235, 232, 245), 15, width=SCREEN_WIDTH - 120, multiline=True, align="center", anchor_x="center", anchor_y="center").draw()

            sx, sy, sz, se, sh = self.data_values
            arcade.Text(f"x={sx}  y={sy}  z={sz}  e={se}  h={sh}", # Added h to report footer
                        SCREEN_WIDTH / 2, 100, (200, 195, 220), 13, anchor_x="center", anchor_y="center").draw()
            self._draw_button(self.back_btn, "← back", self._btn_hover_back, primary=False)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self._btn_hover_ai = self.active_page == self.VIEW_DASH and self._rect_contains(self.ai_report_btn, x, y)
        self._btn_hover_back = self.active_page == self.VIEW_REPORT and self._rect_contains(self.back_btn, x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT: return
        if self.active_page == self.VIEW_DASH and self._btn_hover_ai: self.active_page = self.VIEW_REPORT
        elif self.active_page == self.VIEW_REPORT and self._btn_hover_back: self.active_page = self.VIEW_DASH


def main():
    # access json file to get data.
    with open(r'C:\Programing\nitzanim\ornitz\server\final_report.json', 'r') as file:
        data = json.load(file)

    Education = data['summary']['category_counts']['Education']
    Games = data['summary']['category_counts']['Games']
    Entertainment = data['summary']['category_counts']['Entertainment']
    Adult = data['summary']['category_counts']['Adult']
    Other = data['summary']['category_counts']['Other']

    # 2. Calculate the total
    total = Education + Games + Entertainment + Adult + Other

    # Safety check: prevent division by zero if the JSON is completely empty
    if total == 0:
        total = 1

        # 3. Calculate the ratios and pass them as lists
    x = [Education / total]
    y = [Games / total]
    z = [Entertainment / total]
    e = [Adult / total]
    h = [Other / total]

    window = AppWindow(x, y, z, e, h)
    arcade.run()

if __name__ == "__main__":
    main()