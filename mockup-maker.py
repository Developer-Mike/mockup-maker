import os, sys, time, shutil, json
from zipfile import ZipFile
from PIL import Image
from mockups import MockupScreenshot, MockupScreenshotCensored, MockupText

# Get project name from the first argument
if len(sys.argv) > 1: project_name = sys.argv[1]
else: exit('No project name specified')

# Change the current working directory to the project folder
os.chdir(os.path.join(os.path.dirname(__file__), 'projects', project_name))

# Load configuration from config.py
CONFIG = json.load(open('config.json', 'r', encoding='utf-8'))

# Load input images
IMAGES_PARENT_FOLDER = 'images'
OUTPUT_PARENT_FOLDER = f'output/mockups_{int(time.time())}'

# Create a temporary folder to store the extracted images
TEMP_FOLDER = '.temp/'
if os.path.exists(TEMP_FOLDER): shutil.rmtree(TEMP_FOLDER)
os.makedirs(TEMP_FOLDER)

# Generate Mockups for all languages
default_language = CONFIG['default_language']
for language_key in CONFIG['languages']:
    print(f'Generating mockups for {language_key}...')

    # Get zip file name for the current language
    IMAGE_ZIP_FILE = os.path.join(IMAGES_PARENT_FOLDER, f'{language_key}.zip')
    if not os.path.exists(IMAGE_ZIP_FILE): IMAGE_ZIP_FILE = os.path.join(IMAGES_PARENT_FOLDER, f'{default_language}.zip')

    # Open all .jpg files in the input zip file an open them as images
    screenshots = []
    with ZipFile(IMAGE_ZIP_FILE) as input_zip:
        for filename in sorted(input_zip.namelist()):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                with input_zip.open(filename) as image_file:
                    # Save the image to the temporary folder
                    image = Image.open(image_file)
                    image.save(f'{TEMP_FOLDER}{filename}')
                    screenshots.append(Image.open(f'{TEMP_FOLDER}{filename}'))
    print(f'Loaded {len(screenshots)} screenshots.')

    # Loop through all mockups
    mockups = []
    screenshot_index = 0
    for mockup_json in CONFIG['mockups']:
        translated_description = mockup_json['descriptions'].get(language_key, mockup_json['descriptions'][default_language])
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', CONFIG['font'])

        if mockup_json['type'] == 'screenshot':
            mockups.append(MockupScreenshot(
                translated_description, 
                screenshots[screenshot_index], 
                CONFIG['device_corner_radius'],
                CONFIG['device_border_width'],
                CONFIG['output_size'], 
                CONFIG['text_color'], 
                CONFIG['background_color'],
                font_path
            ))

            screenshot_index += 1
        elif mockup_json['type'] == 'screenshot_censored':
            mockups.append(MockupScreenshotCensored(
                translated_description, 
                screenshots[screenshot_index], 
                mockup_json['censored_region'],
                CONFIG['device_corner_radius'],
                CONFIG['device_border_width'],
                CONFIG['output_size'], 
                CONFIG['text_color'], 
                CONFIG['background_color'],
                font_path
            ))

            screenshot_index += 1
        elif mockup_json['type'] == 'text':
            mockups.append(MockupText(
                translated_description, 
                CONFIG['output_size'], 
                CONFIG['text_color'], 
                CONFIG['background_color'],
                font_path
            ))

    # Export all mockups to the output folder
    OUTPUT_FOLDER = os.path.join(OUTPUT_PARENT_FOLDER, language_key)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for i, mockup_json in enumerate(mockups):
        mockup_json.export().save(os.path.join(OUTPUT_FOLDER, f'{i}.png'))

# Remove the temporary folder and its contents
shutil.rmtree(TEMP_FOLDER)

# Show the output folder in the file explorer
os.startfile(os.path.realpath(OUTPUT_PARENT_FOLDER))
