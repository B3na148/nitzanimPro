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
DIVIDER_GREY = (170, 178, 196)

# Pie slice colors
PIE_COLORS = (
    (116, 178, 235),  # x — soft blue
    (132, 205, 167),  # y — mint green
    (246, 205, 127),  # z — warm peach
    (179, 156, 232),  # e — gentle lavender
    (244, 160, 173),  # h — soft pink
)

OUTLINE_COLOR = (70, 84, 110)
OUTLINE_WIDTH = 2
PIE_RADIAL_INSET = 0.04

AI_REPORT_TITLE = "Ai report"
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
        if not REPORT_PATH.exists():
            return

        with REPORT_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        summary = data.get("summary", {})
        counts = summary.get("category_counts", {})

        edu = counts.get("Education", 0)
        gms = counts.get("Games", 0)
        ent = counts.get("Entertainment", 0)
        adt = counts.get("Adult", 0)
        oth = counts.get("Other", 0)

        total = edu + gms + ent + adt + oth
        if total <= 0: total = 1

        self.data_x = [edu / total]
        self.data_y = [gms / total]
        self.data_z = [ent / total]
        self.data_e = [adt / total]
        self.data_h = [oth / total]
        self._recompute_totals()

        self.report_body = summary.get("ai_verdict", "No AI verdict found.")

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
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (56, 82, 120, 200))
        cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2

        arcade.Text("Running AI analysis...", cx, cy + 40, (248, 252, 255), 24, anchor_x="center", anchor_y="center",
                    bold=True).draw()

        for i in range(12):
            angle = (self.elapsed * 4.0 + i * (math.pi / 6.0))
            px = cx + math.cos(angle) * 52
            py = cy + math.sin(angle) * 52
            alpha = int(60 + (i / 11) * 180)
            arcade.draw_circle_filled(px, py, 5, (236, 246, 255, alpha))

    def _draw_moving_background(self):
        t = self.elapsed
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (214, 234, 255))
        for i in range(18):
            frac = i / 18
            shade = (int(214 - frac * 34), int(234 - frac * 26), int(255 - frac * 18), 22)
            arcade.draw_lbwh_rectangle_filled(0, i * (SCREEN_HEIGHT / 18), SCREEN_WIDTH, SCREEN_HEIGHT / 18 + 2, shade)

        blobs = [((193, 224, 255), 230, 0.12, 0.09), ((176, 216, 255), 190, -0.08, 0.12),
                 ((202, 235, 255), 210, 0.10, -0.07)]
        for i, (base_rgb, r_base, vx, vy) in enumerate(blobs):
            ox = math.sin(t * vx + i) * (SCREEN_WIDTH * 0.35) + SCREEN_WIDTH * 0.5
            oy = math.cos(t * vy + i * 0.7) * (SCREEN_HEIGHT * 0.28) + SCREEN_HEIGHT * 0.5
            arcade.draw_circle_filled(ox, oy, r_base * (0.92 + 0.08 * math.sin(t * 0.7 + i)), (*base_rgb, 46))

    def _draw_sidebar(self):
        x0 = SCREEN_WIDTH - SIDEBAR_WIDTH
        arcade.draw_lbwh_rectangle_filled(x0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT, (248, 246, 252))
        arcade.draw_line(x0, 0, x0, SCREEN_HEIGHT, DIVIDER_GREY, 2)

        hx0, hx1 = x0 + SIDEBAR_PAD, SCREEN_WIDTH - SIDEBAR_PAD
        header_y = SCREEN_HEIGHT - 40
        arcade.Text("Category Breakdown", x0 + (SIDEBAR_WIDTH / 2), header_y, (45, 42, 58), 16, anchor_x="center",
                    bold=True).draw()

        start_y, spacing = header_y - 55, 42
        total_val = max(1, sum(self.data_values))

        for i, label in enumerate(self.labels):
            pct = (self.data_values[i] / total_val) * 100
            y_pos = start_y - (i * spacing)
            arcade.draw_lbwh_rectangle_filled(hx0, y_pos - 16, hx1 - hx0, 32, (255, 255, 255))
            arcade.draw_lbwh_rectangle_filled(hx0 + 10, y_pos - 6, 12, 12, PIE_COLORS[i])
            arcade.Text(label, hx0 + 32, y_pos, (55, 52, 68), 12, anchor_y="center").draw()
            arcade.Text(f"{pct:.1f}%", hx1 - 10, y_pos, (55, 52, 68), 12, anchor_x="right", anchor_y="center",
                        bold=True).draw()

    def _draw_pie(self, center_x, center_y, radius):
        total = sum(self.data_values)
        if total <= 0: return
        arcade.draw_circle_filled(center_x, center_y, radius + OUTLINE_WIDTH, OUTLINE_COLOR)

        start_angle = 0.0
        for i, value in enumerate(self.data_values):
            if value <= 0: continue
            extent = (value / total) * 360.0
            arcade.draw_arc_filled(center_x, center_y, radius * 2, radius * 2, PIE_COLORS[i], start_angle,
                                   start_angle + extent + 0.5)

            mid_rad = math.radians(start_angle + extent / 2)
            label = f"{self.labels[i]}\n{int(round((value / total) * 100))}%"
            arcade.Text(label, center_x + radius * 0.65 * math.cos(mid_rad),
                        center_y + radius * 0.65 * math.sin(mid_rad),
                        OUTLINE_COLOR, 12, anchor_x="center", anchor_y="center", bold=True, multiline=True, width=80,
                        align="center").draw()
            start_angle += extent

    def _rect_contains(self, rect, mx: float, my: float) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= mx <= x2 and y1 <= my <= y2

    def _draw_button(self, rect, label, hover, primary=True):
        x1, y1, x2, y2 = rect
        fill = (96, 147, 204) if primary and not hover else (113, 165, 223) if primary else (235, 242,
                                                                                             250) if not hover else (
            220, 232, 245)
        arcade.draw_lbwh_rectangle_filled(x1, y1, x2 - x1, y2 - y1, fill)
        arcade.draw_lbwh_rectangle_outline(x1, y1, x2 - x1, y2 - y1, (66, 108, 153) if primary else (130, 146, 166), 2)
        arcade.Text(label, x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2, (255, 255, 255) if primary else (35, 32, 48), 14,
                    anchor_x="center", anchor_y="center", bold=True).draw()

    def on_draw(self):
        self.clear()
        self._draw_moving_background()
        mw = SCREEN_WIDTH - SIDEBAR_WIDTH

        arcade.draw_lbwh_rectangle_filled(0, 0, mw, SCREEN_HEIGHT, (255, 255, 255, 45))
        self._draw_sidebar()

        if self.active_page == self.VIEW_DASH:
            self._draw_pie(mw * 0.5, SCREEN_HEIGHT * 0.55, 180)
            arcade.Text("Categorization Overview", mw // 2, SCREEN_HEIGHT - 45, (56, 78, 112), 24, anchor_x="center",
                        bold=True).draw()
            self._draw_button(self.ai_report_btn, "Ai report", self._btn_hover_ai)
            self._draw_button(self.run_all_btn, "RUN ALL", self._btn_hover_run)
            arcade.Text(self.run_status, self.run_all_btn[0], self.run_all_btn[3] + 8, (76, 96, 126), 11).draw()
        else:
            # AI Report View
            arcade.Text("AI Analysis Verdict", mw // 2, SCREEN_HEIGHT - 45, (56, 78, 112), 24, anchor_x="center",
                        bold=True).draw()
            arcade.draw_lbwh_rectangle_filled(40, 120, mw - 80, SCREEN_HEIGHT - 220, (255, 255, 255, 150))

            # --- FIXED TEXT POSITION ---
            # Set anchor_y="top" and position it 140 pixels from the top of the screen (inside the white box)
            arcade.Text(
                self.report_body,
                mw // 2,
                SCREEN_HEIGHT - 140,
                (45, 42, 58),
                16,
                width=int(mw - 120),
                multiline=True,
                align="center",
                anchor_x="center",
                anchor_y="top"
            ).draw()

            self._draw_button(self.back_btn, "← Back", self._btn_hover_back, primary=False)

        if self.is_running_pipeline:
            self._draw_loading_overlay()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.is_running_pipeline: return
        self._btn_hover_ai = self.active_page == self.VIEW_DASH and self._rect_contains(self.ai_report_btn, x, y)
        self._btn_hover_run = self.active_page == self.VIEW_DASH and self._rect_contains(self.run_all_btn, x, y)
        self._btn_hover_back = self.active_page == self.VIEW_REPORT and self._rect_contains(self.back_btn, x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_running_pipeline or button != arcade.MOUSE_BUTTON_LEFT: return
        if self._btn_hover_ai:
            self.active_page = self.VIEW_REPORT
        elif self._btn_hover_run:
            self._run_everything()
        elif self._btn_hover_back:
            self.active_page = self.VIEW_DASH


def main():
    edu, gms, ent, adt, oth = 0, 0, 0, 0, 0
    if REPORT_PATH.exists():
        try:
            with REPORT_PATH.open("r", encoding="utf-8") as f:
                counts = json.load(f).get("summary", {}).get("category_counts", {})
                edu, gms, ent, adt, oth = counts.get("Education", 0), counts.get("Games", 0), counts.get(
                    "Entertainment", 0), counts.get("Adult", 0), counts.get("Other", 0)
        except:
            pass

    total = max(1, edu + gms + ent + adt + oth)
    window = AppWindow([edu / total], [gms / total], [ent / total], [adt / total], [oth / total])
    window._reload_from_report()
    arcade.run()


if __name__ == "__main__":
    main()
