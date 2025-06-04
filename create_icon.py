from PIL import Image, ImageDraw
import os

def create_bike_icon():
    # Create a 256x256 image with a transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple bike icon
    # Main circle (wheel)
    wheel_radius = 80
    center_x = size // 2
    center_y = size // 2
    
    # Draw wheels
    draw.ellipse((center_x - wheel_radius, center_y - wheel_radius,
                  center_x + wheel_radius, center_y + wheel_radius),
                 outline=(0, 120, 212), width=8)  # Blue color
    
    # Draw frame
    frame_color = (0, 120, 212)  # Blue color
    # Main frame
    draw.line([(center_x - 40, center_y - 40),
               (center_x + 40, center_y + 40)],
              fill=frame_color, width=8)
    # Handlebar
    draw.line([(center_x - 40, center_y - 40),
               (center_x - 60, center_y - 60)],
              fill=frame_color, width=8)
    # Seat
    draw.line([(center_x + 40, center_y + 40),
               (center_x + 60, center_y + 60)],
              fill=frame_color, width=8)
    
    # Save as ICO file
    if not os.path.exists('assets'):
        os.makedirs('assets')
    image.save('assets/velib_icon.ico', format='ICO')
    print("Icon created successfully!")

if __name__ == "__main__":
    create_bike_icon() 