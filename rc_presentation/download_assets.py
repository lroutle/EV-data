import os
import requests

ASSETS_DIR = "rc_presentation/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

image_urls = {
    "slide1_left.jpg": "https://www.supermotoxl.com/images/stories/product_review/tamiya_hornet/tamiya_hornet_01.jpg",
    "slide1_right.jpg": "https://www.arrma-rc.com/dw/image/v2/BFBR_PRD/on/demandware.static/-/Sites-horizon-master/default/dw5992376c/Images/ARA/ARA5208_A00_6T0IW11O.jpg?sw=800&sh=800&sm=fit",
    "slide2_left.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/9.6V_Ni-Cd_Battery.jpg/800px-9.6V_Ni-Cd_Battery.jpg",
    "slide2_right.jpg": "https://www.hobby-addicts.com/cdn/shop/files/SPMX652SH2_A1_MLSF6B6M.jpg?v=1754142789&width=800",
    "slide3_left.jpg": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Motor_internals.JPG",
    "slide3_right.jpg": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Brushless-Motor-DUM60.jpg",
    "slide4_left.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/RC_transmitter_27MHz.jpg/640px-RC_transmitter_27MHz.jpg", # Generic 27MHz transmitter from Commons if available, or I will use a different placeholder if this fails.
    # Actually, I will use a more reliable URL for a vintage-style radio.
    # Trying: https://upload.wikimedia.org/wikipedia/commons/e/e0/RC_Transmitter_Futaba.jpg - this is a guess.
    # Let's use the one found for the Golden Arrow article if possible, but that's a whole page.
    # I will stick to a generic "old radio" image or a workaround.
    # Better idea: Use the Tamiya Hornet image again for Slide 5 Left as a "Vintage Toy/Hobby Hybrid" representation, or try to find a Tyco one.
    # For Slide 4 Left, I will try a specific Wikimedia URL for "RC Transmitter" that looks older.
    "slide4_left.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Radio_control_transmitter.jpg/360px-Radio_control_transmitter.jpg", # This is often an older style stick radio.
    "slide4_right.jpg": "https://futabausa.com/wp-content/uploads/2019/12/7PXR-sidetop.jpg",
    "slide5_left.jpg": "https://i0.wp.com/rctoymemories.com/wp-content/uploads/2012/05/tycoturbohopper0011.jpg?resize=840,630&ssl=1", # Tyco Turbo Hopper from rctoymemories
    "slide5_right.jpg": "https://www.supermotoxl.com/images/gallery/my_technologies__hobbies/ground_based_models_100/1_10_axial_scx-10_jeep_crawler_150/photo_10_20190520_1124236359.jpg"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_image(url, filename):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        with open(os.path.join(ASSETS_DIR, filename), 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename} from {url}: {e}")

for filename, url in image_urls.items():
    download_image(url, filename)
