from .mockup import Mockup
from PIL import Image, ImageDraw, ImageFont

class MockupScreenshot(Mockup):
    def __init__(self, description: str, screenshot: Image, device_corner_radius: float, device_border_width: float, export_size: tuple[int, int], text_color: str = '#FFFFFF', background_color: str = '#000000', font: str = None):
        self._description = description
        self._screenshot = screenshot
        self._device_corner_radius = device_corner_radius
        self._device_border_width = device_border_width
        self._export_size = export_size
        self._text_color = text_color
        self._background_color = background_color
        self._font = font

    def round_corners(self, image, radius):
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
        alpha = Image.new('L', image.size, 255)
        w, h = image.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        image.putalpha(alpha)
        return image

    def export(self) -> Image:
        # Make a new image with the size of _export_size and the background color of _background_color
        image = Image.new('RGB', self._export_size, self._background_color)
        draw = ImageDraw.Draw(image)

        # Calculate the font size
        font_size = 60
        font = ImageFont.truetype(self._font, font_size)

        # Center the text on the image with the new getbbox() function
        bounding_box = draw.multiline_textbbox((0, 0), text=self._description, font=font)
        text_position = (
            self._export_size[0] // 2 - bounding_box[2] // 2,
            int(self._export_size[1] * 0.09) - bounding_box[3] // 2
        )

        # Draw the text
        draw.multiline_text(text_position, self._description, self._text_color, font=font, align='center')

        # Resize the screenshot to fit the image
        screenshot_width = int(self._export_size[0] * 0.8)
        screenshot_height = self._screenshot.size[1] * screenshot_width // self._screenshot.size[0]
        screenshot_size = (screenshot_width, screenshot_height)

        resized_screenshot = self._screenshot.resize(screenshot_size, Image.BILINEAR)

        # Round the corners of the screenshot
        screenshot_corner_radius = int(self._device_corner_radius * screenshot_size[0])
        rounded_screenshot = self.round_corners(resized_screenshot, screenshot_corner_radius)

        # Calculate the position of the screenshot
        screenshot_position = (
            self._export_size[0] // 2 - screenshot_size[0] // 2, 
            int(self._export_size[1] * 0.2)
        )

        # Calculate the position and size of the device
        absolute_border_width = int(self._device_border_width * screenshot_size[0])
        device_size = tuple(dimension + absolute_border_width * 2 for dimension in screenshot_size)
        device_position = tuple(position - absolute_border_width for position in screenshot_position)
        device_bounding_box = (
            device_position[0],
            device_position[1],
            device_position[0] + device_size[0],
            device_position[1] + device_size[1]
        )
        device_corner_radius = screenshot_corner_radius + absolute_border_width

        # Draw the device
        draw.rounded_rectangle(device_bounding_box, device_corner_radius, fill='#000000')

        # Paste the screenshot on the image
        image.paste(rounded_screenshot, screenshot_position, rounded_screenshot)

        return image