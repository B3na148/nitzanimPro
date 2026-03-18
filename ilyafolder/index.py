import arcade
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dynamic circular diagram"

class PieChartWindow(arcade.Window):
    def __init__(self, x, y, z, e):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.WHITE
        
        self.data_values = [sum(x), sum(y), sum(z), sum(e)]
        self.labels = ['x', 'y', 'z', 'e']
        
        self.colors = [
            (255, 99, 132),
            (54, 162, 235),
            (255, 205, 86),
            (153, 102, 255)
        ]

    def on_draw(self):
        self.clear()
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        radius = 200
        
        total = sum(self.data_values)
        
        if total == 0:
            error_text = arcade.Text("The sum of values = 0", center_x, center_y, arcade.color.BLACK, 20, anchor_x="center")
            error_text.draw()
            return

        start_angle = 0
        
        for i in range(len(self.data_values)):
            value = self.data_values[i]
            if value == 0:
                continue
                
            fraction = value / total
            angle_extent = fraction * 360
            end_angle = start_angle + angle_extent
            
            arcade.draw_arc_filled(
                center_x=center_x,
                center_y=center_y,
                width=radius * 2,
                height=radius * 2,
                color=self.colors[i],
                start_angle=start_angle,
                end_angle=end_angle
            )
            
            rad_start = math.radians(start_angle)
            p_x = center_x + radius * math.cos(rad_start)
            p_y = center_y + radius * math.sin(rad_start)
            arcade.draw_line(center_x, center_y, p_x, p_y, arcade.color.BLACK, 3)
            
            mid_angle = start_angle + (angle_extent / 2)
            rad_mid = math.radians(mid_angle)
            
            text_x = center_x + (radius * 0.6) * math.cos(rad_mid)
            text_y = center_y + (radius * 0.6) * math.sin(rad_mid)
            
            percentage = int(round(fraction * 100))
            label_text = f"{percentage}% {self.labels[i]}"

            text_obj = arcade.Text(
                label_text,
                text_x,
                text_y,
                arcade.color.BLACK,
                14,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
            text_obj.draw()
            
            start_angle = end_angle
            
        arcade.draw_circle_outline(center_x, center_y, radius, arcade.color.BLACK, 3)

def main():
    x = [7]
    y = [12]
    z = [25]
    e = [3]
    
    window = PieChartWindow(x, y, z, e)
    arcade.run()

if __name__ == "__main__":
    main()