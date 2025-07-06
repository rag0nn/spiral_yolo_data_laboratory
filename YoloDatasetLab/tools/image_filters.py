import numpy as np
from enum import Enum
import cv2
from noise import pnoise2

from .utils import get_conf


class Filters (Enum):
            
    def apply_noise(image:np.array) -> np.array:
        """
        Applies Noise filter to image
        Args:
            Image (np.array) : Input Image
        Returns:
            Image (np.array) : The Filter Applied Image
        """
        cfg = get_conf()
        min_mean = cfg.image_filter.noise.min_mean
        max_mean = cfg.image_filter.noise.max_mean
        max_sigma = cfg.image_filter.noise.max_sigma
        mean = np.random.randint(min_mean,max_mean)
        sigma = np.random.randint(0,max_sigma)
            
        gaussian_noise = np.random.normal(mean, sigma, image.shape).astype(np.float32)
        # Görüntüye gürültü ekleme
        noisy_image = cv2.add(image.astype(np.float32), gaussian_noise)
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return noisy_image
    
    def apply_cloud(image:np.array) -> np.array:
        """
        Applies Cloud filter to image
        Args:
            Image (np.array) : Input Image
        Returns:
            Image (np.array) : The Filter Applied Image
        """
        
        def _generate_cloud_mask(width: int,
                                height: int,
                                scale: float = 200.0,
                                octaves: int = 6,
                                persistence: float = 0.5,
                                lacunarity: float = 2.0) -> np.ndarray:
            """
            Perlin noise kullanarak 0–255 aralığında tek kanallı (grayscale) bir bulut maskesi üretir.
            
            Args:
                width, height: çıktı maskesinin boyutları.
                scale: noise'un frekans ölçeği (büyük -> geniş bulutlar, küçük -> ince taneli).
                octaves: kaç katman fBm (fraktal Brownian motion) eklenecek.
                persistence: her octave'daki genliğin azalma kat sayısı.
                lacunarity: her octave'daki frekans artış kat sayısı.
            
            Returns:
                Grayscale uint8 numpy array (yüksek değer = yoğun bulut).
            """
            # Rastgele parametreler
            scale = np.random.uniform(100.0, 400.0)
            octaves = np.random.randint(3, 8)
            persistence = np.random.uniform(0.3, 0.7)
            lacunarity = np.random.uniform(1.5, 2.5)
            mask = np.zeros((height, width), dtype=np.float32)
            for y in range(height):
                for x in range(width):
                    nx = x / scale
                    ny = y / scale
                    # pnoise2 returns [-1,1]
                    mask[y, x] = pnoise2(nx, ny,
                                        octaves=octaves,
                                        persistence=persistence,
                                        lacunarity=lacunarity,
                                        repeatx=1024,
                                        repeaty=1024,
                                        base=42)
            # normalize to [0,255]
            mask = (mask - mask.min()) / (mask.max() - mask.min())
            mask = (mask * 255).astype(np.uint8)
            return mask

        def _overlay_clouds(image: np.ndarray,
                        cloud_mask: np.ndarray,
                        alpha: float = 0.5) -> np.ndarray:
            """
            Bulut maskesini orijinal imaj üzerine alfa blend ile bindirir.
            
            Args:
                image: BGR renkli uint8 görüntü.
                cloud_mask: generate_cloud_mask ile üretilmiş grayscale uint8 maske.
                alpha: bulut opaklığı (0 = görünmez, 1 = tamamen maske).
            
            Returns:
                BGR uint8 sonuç görüntü.
            """
            cloud_bgr = cv2.cvtColor(cloud_mask, cv2.COLOR_GRAY2BGR)
            return cv2.addWeighted(image.astype(np.float32), 1 - alpha,
                                cloud_bgr.astype(np.float32), alpha,
                                gamma=0).astype(np.uint8)        

        cfg = get_conf()
        h, w = image.shape[:2]

            
        cloud = _generate_cloud_mask(w, h,
                                    scale=cfg.image_filter.cloud.scale,
                                    octaves=cfg.image_filter.cloud.octaves,
                                    persistence=cfg.image_filter.cloud.persistance,
                                    lacunarity=cfg.image_filter.cloud.lacunarity)

        result = _overlay_clouds(image, cloud, alpha=cfg.image_filter.cloud.opacity)

        return result
    
    
    
    Noise = ("Noise Filter" ,apply_noise)
    Cloud = ("Cloud Filter" ,apply_cloud)