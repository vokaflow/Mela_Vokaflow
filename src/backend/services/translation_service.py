#!/usr/bin/env python3
"""
VokaFlow - Servicio de Traducción Real
Integración completa con NLLB-3.3B para traducción de alta calidad
"""

import logging
import time
import asyncio
import torch
from typing import Dict, Any, Optional, List, Tuple
import re
from datetime import datetime
from dataclasses import dataclass

from .model_manager import model_manager, ModelInfo

logger = logging.getLogger("vokaflow.translation")

@dataclass
class TranslationResult:
    """Resultado de una traducción"""
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float
    processing_time: float
    model_used: str
    alternatives: List[str] = None
    detected_language: Optional[str] = None
    character_count: int = 0
    word_count: int = 0

class TranslationService:
    """Servicio de traducción usando NLLB-3.3B"""
    
    def __init__(self):
        self.model_name = "nllb-3.3b"
        
        # Mapeo de códigos de idioma a códigos NLLB
        self.language_mapping = {
            "es": "spa_Latn",  # Español
            "en": "eng_Latn",  # Inglés
            "fr": "fra_Latn",  # Francés
            "de": "deu_Latn",  # Alemán
            "it": "ita_Latn",  # Italiano
            "pt": "por_Latn",  # Portugués
            "ru": "rus_Cyrl",  # Ruso
            "zh": "zho_Hans",  # Chino simplificado
            "ja": "jpn_Jpan",  # Japonés
            "ko": "kor_Hang",  # Coreano
            "ar": "arb_Arab",  # Árabe
            "hi": "hin_Deva",  # Hindi
            "tr": "tur_Latn",  # Turco
            "nl": "nld_Latn",  # Holandés
            "sv": "swe_Latn",  # Sueco
            "no": "nob_Latn",  # Noruego
            "da": "dan_Latn",  # Danés
            "fi": "fin_Latn",  # Finlandés
            "pl": "pol_Latn",  # Polaco
            "cs": "ces_Latn",  # Checo
            "hu": "hun_Latn",  # Húngaro
            "ro": "ron_Latn",  # Rumano
            "bg": "bul_Cyrl",  # Búlgaro
            "hr": "hrv_Latn",  # Croata
            "sk": "slk_Latn",  # Eslovaco
            "sl": "slv_Latn",  # Esloveno
            "et": "est_Latn",  # Estonio
            "lv": "lvs_Latn",  # Letón
            "lt": "lit_Latn",  # Lituano
            "mt": "mlt_Latn",  # Maltés
            "ga": "gle_Latn",  # Irlandés
            "cy": "cym_Latn",  # Galés
            "eu": "eus_Latn",  # Euskera
            "ca": "cat_Latn",  # Catalán
            "gl": "glg_Latn",  # Gallego
            "is": "isl_Latn",  # Islandés
            "mk": "mkd_Cyrl",  # Macedonio
            "sr": "srp_Cyrl",  # Serbio
            "uk": "ukr_Cyrl",  # Ucraniano
            "be": "bel_Cyrl",  # Bielorruso
            "th": "tha_Thai",  # Tailandés
            "vi": "vie_Latn",  # Vietnamita
            "id": "ind_Latn",  # Indonesio
            "ms": "zsm_Latn",  # Malayo
            "tl": "tgl_Latn",  # Tagalo
            "sw": "swh_Latn",  # Swahili
            "he": "heb_Hebr",  # Hebreo
            "fa": "pes_Arab",  # Persa
            "ur": "urd_Arab",  # Urdu
            "bn": "ben_Beng",  # Bengalí
            "gu": "guj_Gujr",  # Gujarati
            "kn": "kan_Knda",  # Kannada
            "ml": "mal_Mlym",  # Malayalam
            "mr": "mar_Deva",  # Marathi
            "ne": "npi_Deva",  # Nepalí
            "pa": "pan_Guru",  # Punjabi
            "si": "sin_Sinh",  # Cingalés
            "ta": "tam_Taml",  # Tamil
            "te": "tel_Telu",  # Telugu
            "my": "mya_Mymr",  # Birmano
            "km": "khm_Khmr",  # Jemer
            "lo": "lao_Laoo",  # Lao
            "ka": "kat_Geor",  # Georgiano
            "hy": "hye_Armn",  # Armenio
            "az": "azj_Latn",  # Azerbaiyano
            "kk": "kaz_Cyrl",  # Kazajo
            "ky": "kir_Cyrl",  # Kirguís
            "tg": "tgk_Cyrl",  # Tayiko
            "tk": "tuk_Latn",  # Turcomano
            "uz": "uzn_Latn",  # Uzbeko
            "mn": "khk_Cyrl",  # Mongol
            "am": "amh_Ethi",  # Amhárico
            "ig": "ibo_Latn",  # Igbo
            "yo": "yor_Latn",  # Yoruba
            "zu": "zul_Latn",  # Zulú
            "af": "afr_Latn",  # Afrikáans
            "sq": "als_Latn",  # Albanés
            "lv": "lvs_Latn",  # Letón
            "lt": "lit_Latn",  # Lituano
        }
        
        # Patrones para detección de idioma
        self.language_patterns = {
            "es": [r'\b(el|la|los|las|un|una|es|son|que|de|en|y|con|por|para|el)\b',
                   r'[ñáéíóúü]', r'\b(hola|gracias|adiós|sí|no)\b'],
            "en": [r'\b(the|and|is|are|you|that|it|for|with|on|as|be|at)\b',
                   r'\b(hello|thanks|goodbye|yes|no)\b'],
            "fr": [r'\b(le|la|les|un|une|est|sont|que|de|et|dans|pour|avec)\b',
                   r'[àâäéèêëïîôöùûüÿç]', r'\b(bonjour|merci|au revoir|oui|non)\b'],
            "de": [r'\b(der|die|das|ein|eine|ist|sind|und|in|mit|für|von)\b',
                   r'[äöüß]', r'\b(hallo|danke|auf wiedersehen|ja|nein)\b'],
            "it": [r'\b(il|la|gli|le|un|una|è|sono|che|di|e|in|con|per)\b',
                   r'[àèéìíîòóùú]', r'\b(ciao|grazie|arrivederci|sì|no)\b'],
            "pt": [r'\b(o|a|os|as|um|uma|é|são|que|de|e|em|com|para)\b',
                   r'[áâãàçéêíóôõú]', r'\b(olá|obrigado|tchau|sim|não)\b'],
            "ru": [r'[а-яё]', r'\b(и|в|на|с|по|для|от|за|к|о)\b'],
            "zh": [r'[\u4e00-\u9fff]', r'[的是了我在有他这为]'],
            "ja": [r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', r'[のはをがでにへと]'],
            "ko": [r'[\uac00-\ud7af]', r'[이가은는을를의와과]'],
            "ar": [r'[\u0600-\u06ff]', r'\b(في|من|إلى|على|عن|مع|هذا|التي)\b'],
            "hi": [r'[\u0900-\u097f]', r'\b(और|में|से|के|की|को|पर|है)\b'],
            "tr": [r'[çğıöşü]', r'\b(ve|bir|bu|için|ile|olan|var|yok)\b'],
        }
        
        logger.info("Servicio de traducción NLLB inicializado")
    
    def get_nllb_language_code(self, lang_code: str) -> str:
        """Convierte código de idioma a formato NLLB"""
        return self.language_mapping.get(lang_code, lang_code)
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detecta el idioma del texto usando patrones"""
        text_lower = text.lower()
        scores = {}
        
        # Calcular puntuaciones para cada idioma
        for lang, patterns in self.language_patterns.items():
            score = 0
            text_length = len(text_lower)
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    # Puntuación basada en número de coincidencias y longitud
                    match_score = len(matches) / max(1, text_length / 10)
                    score += match_score
            
            scores[lang] = score
        
        if not scores:
            return "en", 0.5  # Default
        
        # Obtener el idioma con mayor puntuación
        detected_lang = max(scores, key=scores.get)
        confidence = min(0.95, scores[detected_lang] / max(1, max(scores.values())))
        
        return detected_lang, max(0.3, confidence)
    
    async def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        context: Optional[str] = None,
        max_length: int = 512
    ) -> TranslationResult:
        """Traduce texto usando NLLB-3.3B"""
        start_time = time.time()
        
        try:
            # Detectar idioma origen si no se especifica
            detected_language = None
            if not source_lang:
                detected_language, confidence = self.detect_language(text)
                source_lang = detected_language
                logger.info(f"Idioma detectado: {source_lang} (confianza: {confidence:.2f})")
            
            # Verificar si necesita traducción
            if source_lang == target_lang:
                return TranslationResult(
                    translated_text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    confidence=1.0,
                    processing_time=time.time() - start_time,
                    model_used="nllb-3.3b",
                    detected_language=detected_language,
                    character_count=len(text),
                    word_count=len(text.split())
                )
            
            # Obtener modelo NLLB
            model_info = await asyncio.get_event_loop().run_in_executor(
                None, model_manager.get_model, self.model_name
            )
            
            if not model_info or not model_info.model:
                # Fallback a traducción simulada si el modelo no está disponible
                logger.warning("Modelo NLLB no disponible, usando traducción simulada")
                return await self._fallback_translation(text, source_lang, target_lang, start_time)
            
            # Convertir códigos de idioma a formato NLLB
            nllb_source = self.get_nllb_language_code(source_lang)
            nllb_target = self.get_nllb_language_code(target_lang)
            
            logger.info(f"Traduciendo: {nllb_source} -> {nllb_target}")
            
            # Realizar traducción en hilo separado
            translated_text, confidence = await asyncio.get_event_loop().run_in_executor(
                None, self._translate_with_nllb, 
                model_info, text, nllb_source, nllb_target, max_length
            )
            
            processing_time = time.time() - start_time
            
            return TranslationResult(
                translated_text=translated_text,
                source_lang=source_lang,
                target_lang=target_lang,
                confidence=confidence,
                processing_time=processing_time,
                model_used="nllb-3.3b",
                detected_language=detected_language,
                character_count=len(text),
                word_count=len(text.split()),
                alternatives=[]  # TODO: Implementar alternativas
            )
            
        except Exception as e:
            logger.error(f"Error en traducción NLLB: {e}")
            # Fallback a traducción simulada en caso de error
            return await self._fallback_translation(text, source_lang, target_lang, start_time)
    
    def _translate_with_nllb(
        self,
        model_info: ModelInfo,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int
    ) -> Tuple[str, float]:
        """Realiza la traducción usando el modelo NLLB cargado"""
        try:
            model = model_info.model
            tokenizer = model_info.tokenizer
            
            logger.info(f"🔄 Traduciendo con NLLB: {source_lang} -> {target_lang}")
            
            # Configurar idioma origen en el tokenizer
            tokenizer.src_lang = source_lang
            
            # Tokenizar el texto de entrada
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            )
            
            # Mover a dispositivo correcto
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generar traducción
            with torch.no_grad():
                # Obtener el token de idioma objetivo
                target_lang_id = tokenizer.convert_tokens_to_ids(target_lang)
                
                # Si no se encuentra el idioma, usar el mapeo de códigos
                if target_lang_id == tokenizer.unk_token_id:
                    # Intentar con el formato completo del idioma
                    target_token = target_lang
                    if hasattr(tokenizer, 'lang_code_to_id') and target_lang in tokenizer.lang_code_to_id:
                        target_lang_id = tokenizer.lang_code_to_id[target_lang]
                    else:
                        # Fallback: usar el primer token del vocabulario que coincida
                        for token, token_id in tokenizer.get_vocab().items():
                            if target_lang in token:
                                target_lang_id = token_id
                                break
                
                # Generar la traducción
                outputs = model.generate(
                    **inputs,
                    forced_bos_token_id=target_lang_id if target_lang_id != tokenizer.unk_token_id else None,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decodificar el resultado
            translated_text = tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            ).strip()
            
            # Remover el texto original si se repitió
            if translated_text.startswith(text):
                translated_text = translated_text[len(text):].strip()
            
            # Calcular confianza basada en la calidad de la traducción
            if len(translated_text) == 0:
                confidence = 0.1
            elif translated_text == text:
                confidence = 0.3  # Probable que no se tradujo
            else:
                # Confianza basada en longitud relativa y diferencia del texto original
                length_ratio = len(translated_text) / max(1, len(text))
                similarity = 1.0 if translated_text != text else 0.5
                confidence = min(0.95, 0.7 + (length_ratio * 0.15) + (similarity * 0.1))
            
            logger.info(f"✅ NLLB traducción completada: '{text[:30]}...' -> '{translated_text[:30]}...'")
            
            return translated_text, confidence
            
        except Exception as e:
            logger.error(f"❌ Error en _translate_with_nllb: {e}")
            raise
    
    async def _fallback_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        start_time: float
    ) -> TranslationResult:
        """Traducción de respaldo cuando NLLB no está disponible"""
        
        # Diccionario de traducciones básicas
        basic_translations = {
            ("es", "en"): {
                "hola": "hello",
                "mundo": "world",
                "gracias": "thank you",
                "por favor": "please",
                "adiós": "goodbye",
                "buenos días": "good morning",
                "buenas noches": "good night",
                "cómo estás": "how are you",
                "muy bien": "very good",
                "hasta luego": "see you later"
            },
            ("en", "es"): {
                "hello": "hola",
                "world": "mundo",
                "thank you": "gracias",
                "please": "por favor",
                "goodbye": "adiós",
                "good morning": "buenos días",
                "good night": "buenas noches",
                "how are you": "cómo estás",
                "very good": "muy bien",
                "see you later": "hasta luego"
            },
            ("es", "fr"): {
                "hola": "bonjour",
                "mundo": "monde",
                "gracias": "merci",
                "por favor": "s'il vous plaît",
                "adiós": "au revoir"
            },
            ("es", "de"): {
                "hola": "hallo",
                "mundo": "welt",
                "gracias": "danke",
                "por favor": "bitte",
                "adiós": "auf wiedersehen"
            }
        }
        
        # Simular tiempo de procesamiento
        await asyncio.sleep(0.1)
        
        text_lower = text.lower().strip()
        lang_pair = (source_lang, target_lang)
        
        # Buscar traducción exacta
        if lang_pair in basic_translations:
            translations = basic_translations[lang_pair]
            if text_lower in translations:
                translated_text = translations[text_lower]
                confidence = 0.85
            else:
                # Buscar coincidencias parciales
                translated_text = text
                confidence = 0.60
                for original, translation in translations.items():
                    if original in text_lower:
                        translated_text = text_lower.replace(original, translation)
                        confidence = 0.75
                        break
                else:
                    translated_text = f"[{target_lang.upper()}] {text}"
                    confidence = 0.30
        else:
            translated_text = f"[{target_lang.upper()}] {text}"
            confidence = 0.30
        
        processing_time = time.time() - start_time
        
        logger.warning(f"Usando traducción de respaldo para {source_lang}->{target_lang}")
        
        return TranslationResult(
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=confidence,
            processing_time=processing_time,
            model_used="fallback",
            character_count=len(text),
            word_count=len(text.split())
        )
    
    async def translate_batch(
        self,
        texts: List[str],
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> List[TranslationResult]:
        """Traduce múltiples textos en lote"""
        results = []
        
        for text in texts:
            try:
                result = await self.translate_text(text, target_lang, source_lang)
                results.append(result)
            except Exception as e:
                logger.error(f"Error traduciendo texto en lote: {e}")
                # Agregar resultado de error
                results.append(TranslationResult(
                    translated_text=f"[ERROR] {text}",
                    source_lang=source_lang or "unknown",
                    target_lang=target_lang,
                    confidence=0.0,
                    processing_time=0.0,
                    model_used="error"
                ))
        
        return results
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Obtiene idiomas soportados"""
        return {
            "supported_languages": list(self.language_mapping.keys()),
            "total_count": len(self.language_mapping),
            "model": "nllb-3.3b",
            "high_quality_pairs": [
                ("es", "en"), ("en", "es"),
                ("fr", "es"), ("es", "fr"),
                ("de", "en"), ("en", "de"),
                ("it", "es"), ("es", "it"),
                ("pt", "es"), ("es", "pt")
            ]
        }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Obtiene estado del servicio de traducción"""
        model_loaded = self.model_name in model_manager.loaded_models
        
        return {
            "status": "operational" if model_loaded else "ready",
            "model": self.model_name,
            "model_loaded": model_loaded,
            "supported_languages": len(self.language_mapping),
            "gpu_available": torch.cuda.is_available(),
            "memory_usage": model_manager.get_memory_usage()
        }

# Instancia global del servicio de traducción
translation_service = TranslationService()
