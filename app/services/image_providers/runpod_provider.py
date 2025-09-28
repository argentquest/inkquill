# /ai_rag_story_app/app/services/image_providers/runpod_provider.py

import logging
import base64
import time
import asyncio
import aiohttp
import random
from typing import Optional, Dict, Any

from app.core.config import settings
from .base_provider import BaseImageProvider, ImageGenerationResult
from app.services.cost_tracker_service import log_ai_call
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)

class RunPodProvider(BaseImageProvider):
    """
    An image generation provider that uses RunPod serverless GPUs.
    Supports Flux and Stable Diffusion models.
    """

    def __init__(self):
        if not settings.RUNPOD_API_KEY:
            raise ValueError("RunPod provider is not configured. Missing RUNPOD_API_KEY.")
        if not settings.RUNPOD_ENDPOINT_ID:
            raise ValueError("RunPod provider is not configured. Missing RUNPOD_ENDPOINT_ID.")
        
        self.api_key = settings.RUNPOD_API_KEY
        self.endpoint_id = settings.RUNPOD_ENDPOINT_ID
        self.model_type = settings.RUNPOD_MODEL_TYPE
        self.checkpoint_name = settings.RUNPOD_CHECKPOINT_NAME
        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
        
        logger.info(f"RunPodProvider initialized with endpoint {self.endpoint_id}, model {self.model_type}, checkpoint {self.checkpoint_name}")

    async def generate_image(
        self,
        prompt: str,
        user_id_for_log: int,
        size: str = "1024x1024"
    ) -> Optional[ImageGenerationResult]:
        
        logger.info(f"RunPodProvider: Starting image generation for user {user_id_for_log}")
        logger.info(f"RunPodProvider: PROMPT: >>> {prompt} <<<")
        
        start_time = time.perf_counter()

        try:
            # Parse size for RunPod format
            width, height = self._parse_size(size)
            
            # Prepare RunPod request payload
            payload = self._build_payload(prompt, width, height)
            
            # Submit job to RunPod
            job_id = await self._submit_job(payload)
            if not job_id:
                raise ValueError("Failed to submit job to RunPod")
            
            logger.info(f"RunPodProvider: Job {job_id} submitted, waiting for completion...")
            
            # Poll for completion
            result_data = await self._wait_for_completion(job_id)
            if not result_data:
                raise ValueError("Job failed or timed out")
            
            # Extract image from result
            image_bytes = await self._extract_image(result_data)
            if not image_bytes:
                raise ValueError("Failed to extract image from RunPod response")
            
            end_time = time.perf_counter()
            duration_ms = int((end_time - start_time) * 1000)
            
            # Log cost if model configuration exists
            await self._log_cost(user_id_for_log, prompt, duration_ms)
            
            logger.info(f"RunPodProvider: Successfully generated image for user {user_id_for_log} in {duration_ms}ms")
            
            return ImageGenerationResult(
                image_bytes=image_bytes,
                content_type="image/png",
                revised_prompt=prompt  # RunPod typically doesn't revise prompts
            )

        except Exception as e:
            logger.error(f"RunPodProvider: Error during image generation: {e}", exc_info=True)
            return None

    def _parse_size(self, size: str) -> tuple[int, int]:
        """Parse size string like '1024x1024' into width, height tuple"""
        try:
            if 'x' in size:
                width, height = map(int, size.split('x'))
                return width, height
            else:
                # Default to square if not specified properly
                return 1024, 1024
        except:
            logger.warning(f"Invalid size format '{size}', using default 1024x1024")
            return 1024, 1024

    def _build_payload(self, prompt: str, width: int, height: int) -> Dict[str, Any]:
        """Build the payload for ComfyUI API"""
        
        # ComfyUI workflow for Flux generation
        workflow = {
            "3": {
                "inputs": {
                    "seed": random.randint(0, 2**32 - 1),  # Random seed >= 0 for ComfyUI
                    "steps": 20,
                    "cfg": 1.0,  # Flux typically uses low CFG
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "4": {
                "inputs": {
                    "ckpt_name": self.checkpoint_name
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "7": {
                "inputs": {
                    "text": "",  # Negative prompt (empty for Flux)
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        
        # ComfyUI payload format
        payload = {
            "input": {
                "workflow": workflow,
                "images": []  # No input images needed for text-to-image
            }
        }
        
        return payload

    async def _submit_job(self, payload: Dict[str, Any]) -> Optional[str]:
        """Submit job to RunPod and return job ID"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/run",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"RunPod job submission failed: {response.status} - {error_text}")
                        return None
                    
                    data = await response.json()
                    job_id = data.get("id")
                    if not job_id:
                        logger.error(f"No job ID in RunPod response: {data}")
                        return None
                    
                    return job_id
                    
            except Exception as e:
                logger.error(f"Exception during RunPod job submission: {e}")
                return None

    async def _wait_for_completion(self, job_id: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """Poll RunPod for job completion"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < timeout:
                try:
                    async with session.get(
                        f"{self.base_url}/status/{job_id}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status != 200:
                            logger.warning(f"RunPod status check failed: {response.status}")
                            await asyncio.sleep(2)
                            continue
                        
                        data = await response.json()
                        status = data.get("status")
                        
                        if status == "COMPLETED":
                            output = data.get("output")
                            if output:
                                logger.info(f"RunPod job {job_id} completed successfully")
                                return output
                            else:
                                logger.error(f"RunPod job {job_id} completed but no output")
                                return None
                        
                        elif status == "FAILED":
                            error = data.get("error", "Unknown error")
                            logger.error(f"RunPod job {job_id} failed: {error}")
                            return None
                        
                        elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                            # Still processing, continue polling
                            await asyncio.sleep(2)
                            continue
                        
                        else:
                            logger.warning(f"Unknown RunPod job status: {status}")
                            await asyncio.sleep(2)
                            continue
                
                except Exception as e:
                    logger.warning(f"Exception during RunPod status check: {e}")
                    await asyncio.sleep(2)
                    continue
        
        logger.error(f"RunPod job {job_id} timed out after {timeout} seconds")
        return None

    async def _extract_image(self, output_data: Dict[str, Any]) -> Optional[bytes]:
        """Extract image bytes from ComfyUI RunPod output"""
        try:
            logger.debug(f"ComfyUI output structure: {output_data}")
            
            # ComfyUI typically returns images in this format:
            # {"images": [{"filename": "...", "subfolder": "", "type": "output"}]}
            # or {"message": {...}, "images": [...]}
            
            # First, try to find images array
            images_array = None
            if isinstance(output_data, dict):
                if "images" in output_data:
                    images_array = output_data["images"]
                elif "message" in output_data and isinstance(output_data["message"], dict):
                    if "images" in output_data["message"]:
                        images_array = output_data["message"]["images"]
            elif isinstance(output_data, list):
                images_array = output_data
            
            if not images_array or len(images_array) == 0:
                logger.error("No images found in ComfyUI output")
                return None
            
            # Get the first image
            first_image = images_array[0]
            
            # ComfyUI can return images in different formats:
            
            # Format 1: Base64 encoded image data
            if isinstance(first_image, str):
                try:
                    return base64.b64decode(first_image)
                except Exception as e:
                    logger.warning(f"Failed to decode base64 string: {e}")
            
            # Format 2: Dictionary with image data or filename
            elif isinstance(first_image, dict):
                
                # Direct base64 in various fields
                for field in ["image", "data", "base64", "content"]:
                    if field in first_image and first_image[field]:
                        try:
                            image_data = first_image[field]
                            # Remove data URL prefix if present
                            if isinstance(image_data, str) and image_data.startswith('data:'):
                                image_data = image_data.split(',', 1)[1]
                            return base64.b64decode(image_data)
                        except Exception as e:
                            logger.warning(f"Failed to decode base64 from {field}: {e}")
                            continue
                
                # URL-based image (less common for ComfyUI)
                for field in ["url", "image_url", "file_url"]:
                    if field in first_image and first_image[field]:
                        return await self._download_image_from_url(first_image[field])
                
                # ComfyUI filename format (would need additional API call)
                if "filename" in first_image:
                    logger.warning("ComfyUI returned filename reference - would need additional API call to fetch")
                    # This would require calling ComfyUI's /view endpoint
                    # For now, we'll log this case
                    logger.error(f"Cannot handle filename-based response: {first_image}")
                    return None
            
            logger.error(f"Could not extract image from ComfyUI output format: {first_image}")
            return None
            
        except Exception as e:
            logger.error(f"Exception extracting image from ComfyUI output: {e}", exc_info=True)
            return None

    async def _download_image_from_url(self, url: str) -> Optional[bytes]:
        """Download image from URL if RunPod returns a URL instead of base64"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to download image from URL {url}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception downloading image from URL {url}: {e}")
            return None

    async def _log_cost(self, user_id_for_log: int, prompt: str, duration_ms: int):
        """Log the cost of the RunPod image generation"""
        try:
            # Find RunPod model configuration
            runpod_model_config = None
            for config in model_cache.configurations.values():
                if config.model_name == self.model_type and hasattr(config, 'provider') and config.provider.value == "RUNPOD":
                    runpod_model_config = config
                    break
            
            if runpod_model_config:
                # For RunPod, we treat each image as 1 completion token
                usage_dict = {
                    "prompt_tokens": 0,
                    "completion_tokens": 1,
                    "total_tokens": 1
                }
                await log_ai_call(
                    user_id=user_id_for_log,
                    model_config=runpod_model_config,
                    usage=usage_dict,
                    call_type="image_generation",
                    input_prompt=prompt,
                    duration_ms=duration_ms
                )
                logger.info(f"Logged RunPod cost for user {user_id_for_log}")
            else:
                logger.warning(f"No model configuration found for RunPod model '{self.model_type}'. Skipping cost logging.")
                
        except Exception as cost_log_error:
            logger.error(f"Failed to log RunPod cost, but image generation succeeded: {cost_log_error}")