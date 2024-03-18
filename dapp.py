from os import environ
import logging
import requests
import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def generate_perlin_noise_image(width, height, scale, octaves, persistence, lacunarity, seed):
    # Generate Perlin noise
    noise_image = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            print(f"x: {x}, y: {y}, scale: {scale}, octaves: {octaves}, persistence: {persistence}, lacunarity: {lacunarity}, seed: {seed}")
            noise_image[y][x] = pnoise2(x / scale, y / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=width, repeaty=height, base=seed)
    
    # Normalize values to range [0, 1]
    noise_image = (noise_image - np.min(noise_image)) / (np.max(noise_image) - np.min(noise_image))
    return noise_image

def save_image(image, filename):
    plt.imsave(filename, image, cmap='ocean')


def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    width = 512
    height = 512
    scale = 100.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    seed = 0

    # Generate Perlin noise image
    noise_image = generate_perlin_noise_image(width, height, scale, octaves, persistence, lacunarity, seed)

    # save as png file
    save_image(noise_image, "perlin_noise_image.png")
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
