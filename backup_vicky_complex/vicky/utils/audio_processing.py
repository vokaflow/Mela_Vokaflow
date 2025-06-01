"""
Módulo de procesamiento avanzado de audio para VokaFlow.
Implementa técnicas avanzadas para mejorar la calidad del audio.
"""
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List, Union

logger = logging.getLogger("vicky.utils.audio_processing")

class AudioProcessor:
    """
    Clase para procesamiento avanzado de audio.
    """
    
    def __init__(self, sample_rate: int = 24000):
        """
        Inicializa el procesador de audio.
        
        Args:
            sample_rate: Tasa de muestreo del audio
        """
        self.sample_rate = sample_rate
        logger.info(f"Inicializando procesador de audio con sample_rate={sample_rate}")
        
    def normalize(self, audio: np.ndarray, target_level: float = -24.0) -> np.ndarray:
        """
        Normaliza el audio al nivel LUFS especificado.
        
        Args:
            audio: Array de audio a normalizar
            target_level: Nivel objetivo en LUFS
            
        Returns:
            Audio normalizado
        """
        try:
            import pyloudnorm as pyln
            
            # Medir nivel actual
            meter = pyln.Meter(self.sample_rate)
            loudness = meter.integrated_loudness(audio)
            
            # Normalizar si no es silencio
            if loudness != float('-inf'):
                gain_db = target_level - loudness
                gain_linear = 10 ** (gain_db / 20.0)
                normalized_audio = audio * gain_linear
            else:
                normalized_audio = audio
                
            logger.debug(f"Audio normalizado de {loudness:.2f} LUFS a {target_level:.2f} LUFS")
            return normalized_audio
        except ImportError:
            logger.warning("pyloudnorm no encontrado, usando normalización básica")
            # Normalización básica usando RMS
            return self._basic_normalize(audio, level=0.3)
        except Exception as e:
            logger.error(f"Error en normalización: {e}")
            return audio
    
    def _basic_normalize(self, audio: np.ndarray, level: float = 0.3) -> np.ndarray:
        """
        Normalización básica basada en amplitud máxima.
        
        Args:
            audio: Array de audio
            level: Nivel objetivo (0-1)
            
        Returns:
            Audio normalizado
        """
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio * (level / max_val)
        return audio
    
    def reduce_noise(self, audio: np.ndarray, noise_reduce_amount: float = 0.5) -> np.ndarray:
        """
        Aplica reducción de ruido espectral al audio.
        
        Args:
            audio: Array de audio
            noise_reduce_amount: Cantidad de reducción (0-1)
            
        Returns:
            Audio con ruido reducido
        """
        try:
            import librosa
            from scipy import signal
            
            # Estimar ruido de fondo de segmentos de baja energía
            S = np.abs(librosa.stft(audio))
            noise_profile = np.mean(np.sort(S, axis=1)[:, :int(S.shape[1] * 0.1)], axis=1)
            
            # Aplicar sustracción espectral
            S_reduced = S - noise_profile[:, np.newaxis] * noise_reduce_amount
            S_reduced = np.maximum(S_reduced, 0.0)
            
            # Reconstruir señal
            audio_reduced = librosa.istft(S_reduced * np.exp(1j * np.angle(librosa.stft(audio))))
            
            logger.debug(f"Reducción de ruido aplicada con factor {noise_reduce_amount}")
            return audio_reduced
        except ImportError:
            logger.warning("librosa no encontrado, omitiendo reducción de ruido")
            return audio
        except Exception as e:
            logger.error(f"Error en reducción de ruido: {e}")
            return audio
    
    def enhance_clarity(self, audio: np.ndarray, clarity_amount: float = 0.3) -> np.ndarray:
        """
        Mejora la claridad del audio enfatizando frecuencias de voz.
        
        Args:
            audio: Array de audio
            clarity_amount: Cantidad de mejora (0-1)
            
        Returns:
            Audio con claridad mejorada
        """
        try:
            from scipy import signal
            
            # Crear filtros para bandas de frecuencia de voz
            nyquist = self.sample_rate / 2
            
            # Filtro para consonantes (2000-4000 Hz)
            b_high, a_high = signal.butter(4, [2000/nyquist, 4000/nyquist], 'bandpass')
            high_boost = signal.lfilter(b_high, a_high, audio)
            
            # Filtro para vocales (300-1000 Hz)
            b_mid, a_mid = signal.butter(4, [300/nyquist, 1000/nyquist], 'bandpass')
            mid_boost = signal.lfilter(b_mid, a_mid, audio)
            
            # Combinar filtros con la señal original
            enhanced = audio + clarity_amount * high_boost + (clarity_amount * 0.5) * mid_boost
            
            # Normalizar para evitar clipping
            enhanced = enhanced / np.max(np.abs(enhanced))
            
            logger.debug(f"Mejora de claridad aplicada con factor {clarity_amount}")
            return enhanced
        except Exception as e:
            logger.error(f"Error en mejora de claridad: {e}")
            return audio
    
    def apply_compression(self, audio: np.ndarray, threshold: float = -20, 
                         ratio: float = 4.0, attack: float = 0.005, 
                         release: float = 0.1) -> np.ndarray:
        """
        Aplica compresión dinámica para mejorar la consistencia del audio.
        
        Args:
            audio: Array de audio
            threshold: Umbral en dB
            ratio: Ratio de compresión
            attack: Tiempo de ataque en segundos
            release: Tiempo de liberación en segundos
            
        Returns:
            Audio comprimido
        """
        try:
            # Convertir umbral de dB a lineal
            threshold_linear = 10 ** (threshold / 20.0)
            
            # Calcular envolvente RMS
            n_attack = int(self.sample_rate * attack)
            n_release = int(self.sample_rate * release)
            
            if n_attack < 1:
                n_attack = 1
            if n_release < 1:
                n_release = 1
                
            # Inicializar envolvente
            env = np.zeros_like(audio)
            
            # Calcular envolvente
            for i in range(len(audio)):
                # Detector (valor absoluto)
                env[i] = abs(audio[i])
                
                # Apliador tiempo de ataque/liberación
                if i > 0:
                    if env[i] > env[i-1]:  # Ataque
                        env[i] = env[i-1] + (env[i] - env[i-1]) / n_attack
                    else:  # Liberación
                        env[i] = env[i-1] + (env[i] - env[i-1]) / n_release
            
            # Aplicar compresor
            compressed = np.zeros_like(audio)
            for i in range(len(audio)):
                # Si la envolvente está por debajo del umbral, no hay compresión
                if env[i] <= threshold_linear:
                    gain = 1.0
                else:
                    # Calcular ganancia para valores sobre el umbral
                    gain_reduction = ((env[i] / threshold_linear) ** (1/ratio)) / (env[i] / threshold_linear)
                    gain = gain_reduction
                
                # Aplicar ganancia
                compressed[i] = audio[i] * gain
            
            # Normalizar resultado
            compressed = compressed / np.max(np.abs(compressed)) * 0.95
            
            logger.debug(f"Compresión aplicada: threshold={threshold}dB, ratio={ratio}")
            return compressed
        except Exception as e:
            logger.error(f"Error en compresión: {e}")
            return audio
    
    def process_audio(self, audio: np.ndarray, processing_profile: str = "speech") -> np.ndarray:
        """
        Aplica una cadena completa de procesamiento según el perfil especificado.
        
        Args:
            audio: Array de audio
            processing_profile: Perfil de procesamiento ('speech', 'music', 'podcast')
            
        Returns:
            Audio procesado
        """
        processed = audio.copy()
        
        if processing_profile == "speech":
            # Perfil optimizado para voz hablada
            processed = self.normalize(processed, target_level=-18.0)
            processed = self.reduce_noise(processed, noise_reduce_amount=0.7)
            processed = self.enhance_clarity(processed, clarity_amount=0.3)
            processed = self.apply_compression(processed, threshold=-24, ratio=3.0)
            
        elif processing_profile == "music":
            # Perfil optimizado para música
            processed = self.normalize(processed, target_level=-14.0)
            processed = self.reduce_noise(processed, noise_reduce_amount=0.3)
            processed = self.enhance_clarity(processed, clarity_amount=0.1)
            processed = self.apply_compression(processed, threshold=-20, ratio=2.0)
            
        elif processing_profile == "podcast":
            # Perfil optimizado para podcasts
            processed = self.normalize(processed, target_level=-16.0)
            processed = self.reduce_noise(processed, noise_reduce_amount=0.5)
            processed = self.enhance_clarity(processed, clarity_amount=0.4)
            processed = self.apply_compression(processed, threshold=-22, ratio=3.5)
            
        logger.info(f"Audio procesado con perfil '{processing_profile}'")
        return processed
