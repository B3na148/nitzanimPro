from __future__ import annotations

import arcade
import math
import json
import sys
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from BigButton.main import run_big_button

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Categorization overview"

SIDEBAR_WIDTH = 260
SIDEBAR_PAD = 18
DIVIDER_GREY = (120, 118, 128)

# Pie slice colors
PIE_COLORS = (
    (130, 90, 180),  # x — medium purple
    (95, 130, 175),  # y — dusty blue
    (200, 185, 230),  # z — light lavender
    (160, 120, 200),  # e — accent purple
    (220, 110, 180),  # h — warm pink/purple
)

OUTLINE_COLOR = (18, 18, 22)
OUTLINE_WIDTH = 2
PIE_RADIAL_INSET = 0.04

AI_REPORT_TITLE = "AI report"
REPORT_PATH = ROOT_DIR / "server" / "final_report.json"


class AppWindow(arcade.Window):
    VIEW_DASH = 0
    VIEW_REPORT = 1

    def __init__(self, x, y, z, e, h):
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
        self.data_h = h

        self.labels = ("Education", "Games", "Entertainment", "Adult", "Other")
        self._recompute_totals()

        self.active_page = self.VIEW_DASH
        self.elapsed = 0.0
        self.run_status = "Ready"
        self.report_body = "Run analysis to see the AI verdict."
        self.is_running_pipeline = False
        self._worker_thread: threading.Thread | None = None
        self._worker_error: str | None = None
        self._worker_done = False

        margin = 16
        self.ai_report_btn = (margin, margin, margin + 168, margin + 44)
        self.run_all_btn = (margin, margin + 54, margin + 168, margin + 98)
        self.back_btn = (margin, SCREEN_HEIGHT - margin - 44, margin + 120, SCREEN_HEIGHT - margin)

        self._btn_hover_ai = False
        self._btn_hover_run = False
        self._btn_hover_back = False

    def _recompute_totals(self):
        self.data_values = [
            sum(self.data_x),
            sum(self.data_y),
            sum(self.data_z),
            sum(self.data_e),
            sum(self.data_h),
        ]

    def on_update(self, delta_time: float):
        self.elapsed += delta_time
        if self._worker_thread and self._worker_done:
            self._worker_thread = None
            self._worker_done = False
            if self._worker_error:
                self.run_status = f"Error: {self._worker_error}"
            else:
                try:
                    self._reload_from_report()
                    self.run_status = "Done"
                except Exception as exc:
                    self.run_status = f"Error: {exc}"
            self.is_running_pipeline = False

    def _reload_from_report(self):
        with REPORT_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        counts = data["summary"]["category_counts"]
        education = counts.get("Education", 0)
        games = counts.get("Games", 0)
        entertainment = counts.get("Entertainment", 0)
        adult = counts.get("Adult", 0)
        other = counts.get("Other", 0)

        total = education + games + entertainment + adult + other
        if total <= 0:
            total = 1

        self.data_x = [education / total]
        self.data_y = [games / total]
        self.data_z = [entertainment / total]
        self.data_e = [adult / total]
        self.data_h = [other / total]
        self._recompute_totals()

        self.report_body = data["summary"].get("ai_verdict", "No AI verdict found.")

    def _run_everything(self):
        if self.is_running_pipeline:
            return

        self.is_running_pipeline = True
        self.run_status = "Running..."
        self._worker_error = None
        self._worker_done = False

        def _task():
            try:
                run_big_button(history_payload=None, start_server_if_needed=True, run_ai_analysis=True)
            except Exception as exc:
                self._worker_error = str(exc)
            finally:
                self._worker_done = True

        self._worker_thread = threading.Thread(target=_task, daemon=True)
        self._worker_thread.start()

    def _draw_loading_overlay(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (10, 8, 18, 210))
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2

        arcade.Text(
            "Running AI analysis...",
            cx,
            cy + 40,
            (250, 250, 255),
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

        # Lightweight spinner made from 12 animated dots
        for i in range(12):
            angle = (self.elapsed * 4.0 + i * (math.pi / 6.0))
            px = cx + math.cos(angle) * 52
            py = cy + math.sin(angle) * 52
            alpha = int(60 + (i / 11) * 180)
            arcade.draw_circle_filled(px, py, 5, (186, 164, 236, alpha))

        arcade.Text(
            "Please wait. This can take a bit on first run.",
            cx,
            cy - 36,
            (220, 215, 240),
            14,
            anchor_x="center",
            anchor_y="center",
        ).draw()

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
        # 1. Background and divider
        arcade.draw_lbwh_rectangle_filled(x0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT, (248, 246, 252))
        arcade.draw_line(x0, 0, x0, SCREEN_HEIGHT, DIVIDER_GREY, 2)

        hx0 = x0 + SIDEBAR_PAD
        hx1 = SCREEN_WIDTH - SIDEBAR_PAD

        # 2. Header
        header_y = SCREEN_HEIGHT - 40
        arcade.Text("Category Breakdown", x0 + (SIDEBAR_WIDTH / 2), header_y, (45, 42, 58), 16, anchor_x="center",
                    anchor_y="center", bold=True).draw()
        arcade.draw_line(hx0, header_y - 20, hx1, header_y - 20, (220, 218, 228), 1)

        # 3. Dynamic List Items with Color Swatches
        start_y = header_y - 55
        spacing = 42

        total_val = sum(self.data_values)
        if total_val == 0: total_val = 1  # Safety to prevent division by zero

        for i in range(len(self.labels)):
            val = self.data_values[i]
            pct = (val / total_val) * 100
            y_pos = start_y - (i * spacing)

            # Draw white card background for the row
            arcade.draw_lbwh_rectangle_filled(hx0, y_pos - 16, hx1 - hx0, 32, (255, 255, 255))

            # Draw color swatch
            color = PIE_COLORS[i]
            arcade.draw_lbwh_rectangle_filled(hx0 + 10, y_pos - 6, 12, 12, color)

            # Draw Category Label
            arcade.Text(self.labels[i], hx0 + 32, y_pos, (55, 52, 68), 12, anchor_y="center").draw()

            # Draw Percentage right-aligned
            arcade.Text(f"{pct:.1f}%", hx1 - 10, y_pos, (55, 52, 68), 12, anchor_x="right", anchor_y="center",
                        bold=True).draw()

        # 4. Footer
        footer_y = 40
        arcade.draw_line(hx0, footer_y + 20, hx1, footer_y + 20, (220, 218, 228), 1)
        arcade.Text("Data based on AI report", x0 + (SIDEBAR_WIDTH / 2), footer_y, (140, 138, 148), 10,
                    anchor_x="center", anchor_y="center", italic=True).draw()

    def _draw_pie(self, center_x: float, center_y: float, radius: float):
        total = sum(self.data_values)
        if total <= 0:
            arcade.Text("Totals are zero", center_x, center_y, (255, 255, 255), 16, anchor_x="center",
                        anchor_y="center").draw()
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
            arcade.draw_arc_filled(center_x, center_y, radius * 2, radius * 2, PIE_COLORS[i], start_angle,
                                   end_angle + 0.5, 0, 360)

        # Draw Lines and Labels
        for i, fraction, start_angle, end_angle in slices_data:
            rad_start = math.radians(start_angle)
            rin = max(2.0, radius * PIE_RADIAL_INSET)
            arcade.draw_line(center_x + rin * math.cos(rad_start), center_y + rin * math.sin(rad_start),
                             center_x + (radius - 0.5) * math.cos(rad_start),
                             center_y + (radius - 0.5) * math.sin(rad_start), OUTLINE_COLOR, OUTLINE_WIDTH)

            mid_angle = start_angle + (end_angle - start_angle) * 0.5
            rad_mid = math.radians(mid_angle)
            label = f"{self.labels[i]}\n{int(round(fraction * 100))}%"
            arcade.Text(label, center_x + radius * 0.62 * math.cos(rad_mid),
                        center_y + radius * 0.62 * math.sin(rad_mid),
                        OUTLINE_COLOR, 13, width=max(72, int(radius * 0.55)), anchor_x="center", anchor_y="center",
                        bold=True, multiline=True, align="center").draw()

        arcade.draw_circle_filled(center_x, center_y, OUTLINE_WIDTH * 2, OUTLINE_COLOR)

    def _rect_contains(self, rect, mx: float, my: float) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= mx <= x2 and y1 <= my <= y2

    def _draw_button(self, rect, label: str, hover: bool, primary: bool = True):
        x1, y1, x2, y2 = rect
        cx, cy = x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2
        fill = (120, 85, 185) if primary and not hover else (140, 105, 205) if primary else (230, 228,
                                                                                             240) if not hover else (
            210, 208, 225)
        arcade.draw_lbwh_rectangle_filled(x1, y1, x2 - x1, y2 - y1, fill)
        arcade.draw_lbwh_rectangle_outline(x1, y1, x2 - x1, y2 - y1, (40, 30, 70) if primary else (90, 88, 105), 2)
        arcade.Text(label, cx, cy, (255, 255, 255) if primary else (35, 32, 48), 14, anchor_x="center",
                    anchor_y="center", bold=True).draw()

    def on_draw(self):
        self.clear()
        self._draw_moving_background()

        if self.active_page == self.VIEW_DASH:
            mw = self._main_width()
            arcade.draw_lbwh_rectangle_filled(0, 0, mw, SCREEN_HEIGHT, (255, 255, 255, 38))
            self._draw_pie(mw * 0.48, SCREEN_HEIGHT * 0.52, min(mw, SCREEN_HEIGHT) * 0.28)
            arcade.Text("Categorization", mw // 2, SCREEN_HEIGHT - 36, (255, 255, 255), 22, anchor_x="center",
                        anchor_y="center", bold=True).draw()
            self._draw_sidebar()
            self._draw_button(self.ai_report_btn, "ai report", self._btn_hover_ai, primary=True)
            self._draw_button(self.run_all_btn, "RUN ALL", self._btn_hover_run, primary=True)
            arcade.Text(
                self.run_status,
                self.run_all_btn[0],
                self.run_all_btn[3] + 10,
                (230, 230, 240),
                11,
                anchor_x="left",
                anchor_y="bottom",
            ).draw()
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (14, 12, 26, 230))
            arcade.Text(AI_REPORT_TITLE, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 72, (255, 255, 255), 26, anchor_x="center",
                        anchor_y="center", bold=True).draw()
            arcade.Text(self.report_body, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, (235, 232, 245), 15,
                        width=SCREEN_WIDTH - 120, multiline=True, align="center", anchor_x="center",
                        anchor_y="center").draw()

            sx, sy, sz, se, sh = self.data_values
            arcade.Text(f"x={sx:.2f}  y={sy:.2f}  z={sz:.2f}  e={se:.2f}  h={sh:.2f}",
                        SCREEN_WIDTH / 2, 100, (200, 195, 220), 13, anchor_x="center", anchor_y="center").draw()
            self._draw_button(self.back_btn, "← back", self._btn_hover_back, primary=False)

        if self.is_running_pipeline:
            self._draw_loading_overlay()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.is_running_pipeline:
            self._btn_hover_ai = False
            self._btn_hover_run = False
            self._btn_hover_back = False
            return
        self._btn_hover_ai = self.active_page == self.VIEW_DASH and self._rect_contains(self.ai_report_btn, x, y)
        self._btn_hover_run = self.active_page == self.VIEW_DASH and self._rect_contains(self.run_all_btn, x, y)
        self._btn_hover_back = self.active_page == self.VIEW_REPORT and self._rect_contains(self.back_btn, x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.is_running_pipeline:
            return
        if button != arcade.MOUSE_BUTTON_LEFT: return
        if self.active_page == self.VIEW_DASH and self._btn_hover_ai:
            self.active_page = self.VIEW_REPORT
        elif self.active_page == self.VIEW_DASH and self._btn_hover_run:
            self._run_everything()
        elif self.active_page == self.VIEW_REPORT and self._btn_hover_back:
            self.active_page = self.VIEW_DASH


def main():
    try:
        with REPORT_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        counts = data.get("summary", {}).get("category_counts", {})
        Education = counts.get("Education", 0)
        Games = counts.get("Games", 0)
        Entertainment = counts.get("Entertainment", 0)
        Adult = counts.get("Adult", 0)
        Other = counts.get("Other", 0)
    except Exception:
        # First-run safe defaults (no report yet)
        Education = 0
        Games = 0
        Entertainment = 0
        Adult = 0
        Other = 0

    total = Education + Games + Entertainment + Adult + Other

    if total == 0:
        total = 1

    x = [Education / total]
    y = [Games / total]
    z = [Entertainment / total]
    e = [Adult / total]
    h = [Other / total]

    window = AppWindow(x, y, z, e, h)
    try:
        window._reload_from_report()
    except Exception:
        pass
    arcade.run()


if __name__ == "__main__":
    main()
