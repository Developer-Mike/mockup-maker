from .mockup_screenshot import MockupScreenshot
from PIL import Image, ImageFilter, ImageDraw

class MockupScreenshotCensored(MockupScreenshot):
    def __init__(self, description: str, screenshot: Image, censored_region: [int, int, int, int], device_corner_radius: float, device_border_width: float, export_size: tuple[int, int], text_color: str = '#FFFFFF', background_color: str = '#000000', font: str = None):
        super().__init__(description, screenshot, device_corner_radius, device_border_width, export_size, text_color, background_color, font)
        self._censored_region = censored_region
        
    def export(self) -> Image:
        # Convert censored_region to pixel positions
        absolute_censored_region = [int(value * self._screenshot.size[i % 2]) for i, value in enumerate(self._censored_region)]
        patch_size = (absolute_censored_region[2] - absolute_censored_region[0], absolute_censored_region[3] - absolute_censored_region[1])

        # Get ground color
        ground_color = self._screenshot.getpixel((absolute_censored_region[0], absolute_censored_region[1]))
        
        # Create patch image
        patch = Image.new('RGBA', patch_size, ground_color)

        # Blur region
        blurred_region = self._screenshot.crop(absolute_censored_region).filter(ImageFilter.GaussianBlur(radius=75))

        # Alpha mask
        alpha_mask_margin = 50
        alpha_mask = Image.new('RGBA', patch_size, (0, 0, 0, 0))
        ImageDraw.Draw(alpha_mask).rectangle((alpha_mask_margin, alpha_mask_margin, patch_size[0] - alpha_mask_margin, patch_size[1] - alpha_mask_margin), fill=(255, 255, 255, 255))
        alpha_mask = alpha_mask.filter(ImageFilter.GaussianBlur(radius=alpha_mask_margin / 2))

        # Paste the blurred region into the patch
        patch.paste(blurred_region, alpha_mask)

        # Paste the blurred region back into the screenshot
        self._screenshot.paste(patch, absolute_censored_region)

        # Call super
        return super().export()