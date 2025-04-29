import os
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import hashlib
import random

def calculate_hashes(image_path):
    image_cv_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image_resized = cv2.resize(image_cv_gray, (8, 8), interpolation=cv2.INTER_AREA)
    diff = image_resized[:, 1:] > image_resized[:, :-1]
    perceptual_hash = ''.join(['1' if v else '0' for v in diff.flatten()])
    perceptual_hash_hex = '{:0x}'.format(int(perceptual_hash, 2))

    with open(image_path, 'rb') as f:
        bytes_data = f.read()
        sha256_hash = hashlib.sha256(bytes_data).hexdigest()

    return perceptual_hash_hex, sha256_hash

def hamming_distance(hash1, hash2):
    bin1 = bin(int(hash1, 16))[2:].zfill(64)
    bin2 = bin(int(hash2, 16))[2:].zfill(64)
    return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))

def break_perceptual_hash(input_path, output_path):
    original_phash, original_sha = calculate_hashes(input_path)

    image = Image.open(input_path).convert('RGB')
    pixels = image.load()
    width, height = image.size

    # Random brightness factor
    brightness_factor = random.uniform(0.5, 1.5)
    # Random gradient factor
    gradiente_factor = random.randint(50, 150)

    # Random pixel adjustments
    for i in range(0, min(width, height), random.randint(5, 15)):
        for offset in range(-1, 2):
            if 0 <= i + offset < width and 0 <= i < height:
                pixels[i + offset, i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if 0 <= i - offset < width and 0 <= i < height:
                pixels[i - offset, i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            factor = int((x + y) / (width + height) * gradiente_factor)
            pixels[x, y] = (min(r + factor, 255), min(g + factor, 255), min(b + factor, 255))

    # Random micro lines
    for i in range(0, min(width, height), random.randint(20, 40)):
        if 0 <= i < width and 0 <= i < height:
            pixels[i, i] = tuple(min(v ^ random.choice([0, 1]), 255) for v in pixels[i, i])
        if 0 <= width - i - 1 < width and 0 <= i < height:
            pixels[width - i - 1, i] = tuple(min(v ^ random.choice([0, 1]), 255) for v in pixels[width - i - 1, i])

    # Random dark pixel adjustments
    for x in range(0, width, random.randint(30, 50)):
        for y in range(0, height, random.randint(30, 50)):
            r, g, b = pixels[x, y]
            if r < 50 and g < 50 and b < 50:
                pixels[x, y] = (r + random.randint(5, 15), g + random.randint(5, 15), b + random.randint(5, 15))

    # Random texture overlay
    for y in range(0, height, random.randint(6, 10)):
        for x in range(0, width, random.randint(6, 10)):
            if (x + y) % random.randint(12, 20) == 0:
                r, g, b = pixels[x, y]
                pixels[x, y] = (min(r + random.randint(1, 3), 255), min(g + random.randint(1, 3), 255), min(b + random.randint(1, 3), 255))

    image = ImageEnhance.Brightness(image).enhance(brightness_factor)
    image.save(output_path)

    new_phash, new_sha = calculate_hashes(output_path)
    dist = hamming_distance(original_phash, new_phash)

    print(f"Image: {os.path.basename(input_path)}")
    print("Original perceptual hash:", original_phash)
    print("New perceptual hash:     ", new_phash)
    print("Hamming distance:        ", dist)
    if dist < 4:
        print("[!] Warning: Very small distance detected.")
        print("[!] Recommended to apply more aggressive modifications or use stealth/aggressive mode.")
    print("Original SHA256 hash:    ", original_sha)
    print("New SHA256 hash:         ", new_sha)
    print("-" * 50)

input_folder = "input"
output_folder = "output"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        break_perceptual_hash(input_path, output_path)
