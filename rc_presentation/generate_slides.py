from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os

# Configuration
ASSETS_DIR = "rc_presentation/assets"
OUTPUT_DIR = "rc_presentation/output"
CANVAS_SIZE = (1920, 1080)
HALF_WIDTH = 960
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Slides Configuration
slides = [
    {
        "id": 1,
        "left": "slide1_left.jpg",
        "right": "slide1_right.jpg",
        "text": "RC EVOLUTION: 1990s vs 2025"
    },
    {
        "id": 2,
        "left": "slide2_left.jpg",
        "right": "slide2_right.jpg",
        "text": "POWER: NiCd vs LiPo"
    },
    {
        "id": 3,
        "left": "slide3_left.jpg",
        "right": "slide3_right.jpg",
        "text": "EFFICIENCY: Brushed vs Brushless"
    },
    {
        "id": 4,
        "left": "slide4_left.jpg", # This failed to download, handle missing
        "right": "slide4_right.jpg",
        "text": "CONTROL: Analog vs Telemetry"
    },
    {
        "id": 5,
        "left": "slide5_left.jpg",
        "right": "slide5_right.jpg",
        "text": "SCALE REALISM: 2025"
    }
]

def create_placeholder_image(size, color, text):
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill="white", font=font)
    return img

def apply_vintage_style(img):
    # Grayscale, Sepia, Noise, Slight Blur
    img = ImageOps.grayscale(img)
    img = ImageOps.colorize(img, "#704214", "#C0C0C0") # Sepia-ish
    # Add noise (grain)
    # Simple grain simulation: merge with noise image or just leave as sepia for "vintage" feel given library constraints
    # Adding slight blur
    img = img.filter(ImageFilter.GaussianBlur(1))
    return img

def apply_modern_style(img):
    # Sharpen, Saturation boost, Contrast boost
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    return img

def process_slide(slide_data):
    canvas = Image.new('RGB', CANVAS_SIZE, "black")

    # Left Image
    left_path = os.path.join(ASSETS_DIR, slide_data["left"])
    if os.path.exists(left_path):
        try:
            left_img = Image.open(left_path).convert("RGB")
            # Resize to fill half
            left_img = ImageOps.fit(left_img, (HALF_WIDTH, CANVAS_SIZE[1]), method=Image.Resampling.LANCZOS)
            left_img = apply_vintage_style(left_img)
        except Exception as e:
            print(f"Error processing left image for slide {slide_data['id']}: {e}")
            left_img = create_placeholder_image((HALF_WIDTH, CANVAS_SIZE[1]), "#333333", "Image Error")
    else:
        left_img = create_placeholder_image((HALF_WIDTH, CANVAS_SIZE[1]), "#333333", "Asset Not Found")

    # Right Image
    right_path = os.path.join(ASSETS_DIR, slide_data["right"])
    if os.path.exists(right_path):
        try:
            right_img = Image.open(right_path).convert("RGB")
            # Resize to fill half
            right_img = ImageOps.fit(right_img, (HALF_WIDTH, CANVAS_SIZE[1]), method=Image.Resampling.LANCZOS)
            right_img = apply_modern_style(right_img)
        except Exception as e:
            print(f"Error processing right image for slide {slide_data['id']}: {e}")
            right_img = create_placeholder_image((HALF_WIDTH, CANVAS_SIZE[1]), "#555555", "Image Error")
    else:
        right_img = create_placeholder_image((HALF_WIDTH, CANVAS_SIZE[1]), "#555555", "Asset Not Found")

    # Paste images
    canvas.paste(left_img, (0, 0))
    canvas.paste(right_img, (HALF_WIDTH, 0))

    # Draw Text Overlay
    draw = ImageDraw.Draw(canvas)
    text = slide_data["text"]

    # Font setup
    try:
        # Try to find a bold font
        font_size = 80
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        # Fallback
        font = ImageFont.load_default()
        font_size = 40 # Default font is small

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (CANVAS_SIZE[0] - text_w) / 2
    y = (CANVAS_SIZE[1] - text_h) / 2

    # Draw shadow/outline
    outline_range = 3
    for dx in range(-outline_range, outline_range+1):
        for dy in range(-outline_range, outline_range+1):
            draw.text((x+dx, y+dy), text, font=font, fill="black")

    # Draw main text
    draw.text((x, y), text, font=font, fill="white")

    # Save
    output_filename = f"slide_{slide_data['id']}.png"
    canvas.save(os.path.join(OUTPUT_DIR, output_filename))
    print(f"Generated {output_filename}")

if __name__ == "__main__":
    for slide in slides:
        process_slide(slide)
