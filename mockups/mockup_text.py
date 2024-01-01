from .mockup import Mockup
from PIL import Image, ImageDraw, ImageFont

class MockupText(Mockup):
    def __init__(self, description: str, export_size: tuple[int, int], text_color: str = '#FFFFFF', background_color: str = '#000000', font: str = None):
        self._description = description
        self._export_size = export_size
        self._text_color = text_color
        self._background_color = background_color
        self._font = font

    def export(self) -> Image:
        # Make a new image with the size of _export_size and the background color of _background_color
        image = Image.new('RGB', self._export_size, self._background_color)
        draw = ImageDraw.Draw(image)

        # Calculate the font size
        font_size = 80
        font = ImageFont.truetype(self._font, font_size)

        # Center the text on the image with the new getbbox() function
        bounding_box = draw.multiline_textbbox((0, 0), text=self._description, font=font)
        text_position = (
            self._export_size[0] // 2 - bounding_box[2] // 2, 
            self._export_size[1] // 2 - bounding_box[3] // 2
        )

        # Draw the text
        draw.multiline_text(text_position, self._description, self._text_color, font=font, align='center')

        return image