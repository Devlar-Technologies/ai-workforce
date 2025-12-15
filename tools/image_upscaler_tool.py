"""
Image Upscaling Tool - AI-powered image enhancement and resolution increase
High-quality upscaling using fal.ai's advanced upscaling models
"""

import os
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime

import requests
import fal_client
from loguru import logger
from crewai.tools import BaseTool

class ImageUpscalerTool(BaseTool):
    """
    AI-powered image upscaling tool via fal.ai.
    Enhances resolution and quality of existing images.
    """

    name: str = "image_upscaler"
    description: str = (
        "Upscale and enhance image quality using AI models. "
        "Increase resolution up to 4x while maintaining or improving quality."
    )

    def __init__(self):
        super().__init__()
        # fal_client uses FAL_KEY environment variable automatically
        self.api_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY or FAL_API_KEY environment variable is required")

    def _run(
        self,
        image_path: str,
        upscale_factor: int = 2,
        model: str = "clarity",
        enhance_quality: bool = True,
        output_path: Optional[str] = None
    ) -> str:
        """
        Upscale an image using AI models

        Args:
            image_path: Path to the input image file
            upscale_factor: Upscaling factor (1-4x)
            model: Upscaling model ("clarity", "esrgan", "topaz", "creative", "aura")
            enhance_quality: Whether to enhance quality during upscaling
            output_path: Optional output path for the upscaled image

        Returns:
            Information about the upscaled image and download details
        """
        try:
            logger.info(f"🔍 Upscaling image: {image_path} with {upscale_factor}x factor...")

            # Read and encode image
            image_data = self._encode_image(image_path)

            # Select appropriate model and upscale
            result = self._upscale_image(
                image_data,
                upscale_factor=upscale_factor,
                model=model,
                enhance_quality=enhance_quality
            )

            # Format response
            return self._format_upscale_result(result, image_path, upscale_factor, model)

        except Exception as e:
            logger.error(f"❌ Image upscaling failed: {e}")
            return f"Image upscaling failed: {str(e)}"

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API upload"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            raise ValueError(f"Failed to read image file {image_path}: {e}")

    def _upscale_image(
        self,
        image_data: str,
        upscale_factor: int = 2,
        model: str = "clarity",
        enhance_quality: bool = True
    ) -> Dict[str, Any]:
        """Upscale image using selected fal.ai model"""

        # Model configurations
        model_configs = {
            "clarity": "fal-ai/clarity-upscaler",
            "esrgan": "fal-ai/esrgan",
            "topaz": "fal-ai/topaz/upscale/image",
            "creative": "fal-ai/creative-upscaler",
            "aura": "fal-ai/aura-sr",
            "recraft": "fal-ai/recraft/upscale/crisp"
        }

        model_endpoint = model_configs.get(model, model_configs["clarity"])

        # Prepare arguments based on model
        if model == "clarity":
            arguments = {
                "image": image_data,
                "scale_factor": upscale_factor
            }
        elif model == "esrgan":
            arguments = {
                "image": image_data,
                "scale": upscale_factor
            }
        elif model == "topaz":
            arguments = {
                "image": image_data,
                "upscale_factor": upscale_factor
            }
        elif model == "creative":
            arguments = {
                "image": image_data,
                "scale_factor": upscale_factor,
                "creativity": 0.3 if enhance_quality else 0.1,
                "resemblance": 0.8 if enhance_quality else 0.9
            }
        elif model == "aura":
            arguments = {
                "image": image_data
            }
        elif model == "recraft":
            arguments = {
                "image": image_data
            }
        else:
            # Default to clarity
            arguments = {
                "image": image_data,
                "scale_factor": upscale_factor
            }

        # Execute upscaling
        result = fal_client.subscribe(
            model_endpoint,
            arguments=arguments
        )

        return result

    def _format_upscale_result(
        self,
        result: Dict[str, Any],
        original_path: str,
        upscale_factor: int,
        model: str
    ) -> str:
        """Format the upscaling result"""

        if not result or 'image' not in result:
            return "Image upscaling completed but no image data returned"

        image_info = result.get('image', {})
        image_url = image_info.get('url') if isinstance(image_info, dict) else result.get('image', {}).get('url', 'No URL provided')

        # Handle different response formats
        if isinstance(result.get('image'), str):
            image_url = result['image']

        # Extract metadata if available
        width = image_info.get('width', 'Enhanced') if isinstance(image_info, dict) else 'Enhanced'
        height = image_info.get('height', 'Enhanced') if isinstance(image_info, dict) else 'Enhanced'

        formatted_result = f"""
# 🔍 Image Successfully Upscaled

## Upscaling Details
**Original File**: {original_path}
**Upscale Factor**: {upscale_factor}x
**Model Used**: {model.title()}
**Enhanced Dimensions**: {width} x {height}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Download Links
**Enhanced Image URL**: {image_url}

## Model Information
- **Clarity**: Best for general photos and logos
- **ESRGAN**: Good for anime/cartoon style images
- **Topaz**: Professional-grade upscaling
- **Creative**: Artistic enhancement with customizable creativity
- **AuraSR**: Real-world image enhancement
- **Recraft**: Focus on crisp details and faces

## Usage Recommendations
- **Webapp Display**: Perfect for high-DPI screens and retina displays
- **Print Materials**: Enhanced resolution suitable for print media
- **Marketing Assets**: Professional quality for presentations and websites
- **Social Media**: Crisp images for all platform requirements

## Next Steps
1. Download the enhanced image from the URL above
2. Save to your project's assets directory
3. Update webapp configuration to use the high-res version
4. Test display across different screen resolutions

---
*Enhanced with {model.title()} via fal.ai*
"""

        return formatted_result

    def upscale_logo_for_webapp(
        self,
        logo_path: str,
        target_width: int = 800,
        model: str = "clarity"
    ) -> str:
        """Specialized function for upscaling logos for webapp use"""

        # Calculate appropriate upscale factor
        try:
            from PIL import Image
            with Image.open(logo_path) as img:
                current_width = img.width
                upscale_factor = max(1, min(4, target_width // current_width))
        except ImportError:
            # Fallback if PIL not available
            upscale_factor = 2

        logger.info(f"🎯 Upscaling logo for webapp: target width {target_width}px, factor {upscale_factor}x")

        return self._run(
            image_path=logo_path,
            upscale_factor=upscale_factor,
            model=model,
            enhance_quality=True
        )

    def batch_upscale_assets(
        self,
        asset_paths: list,
        upscale_factor: int = 2,
        model: str = "clarity"
    ) -> Dict[str, str]:
        """Batch upscale multiple assets"""
        results = {}

        for asset_path in asset_paths:
            try:
                result = self._run(
                    image_path=asset_path,
                    upscale_factor=upscale_factor,
                    model=model
                )
                results[asset_path] = result
            except Exception as e:
                results[asset_path] = f"Failed: {str(e)}"

        return results

    def get_model_recommendations(self, image_type: str = "logo") -> Dict[str, str]:
        """Get model recommendations based on image type"""
        recommendations = {
            "logo": {
                "primary": "clarity",
                "alternative": "recraft",
                "reason": "Best for preserving sharp edges and text in logos"
            },
            "photo": {
                "primary": "aura",
                "alternative": "topaz",
                "reason": "Optimized for real-world photography"
            },
            "artwork": {
                "primary": "creative",
                "alternative": "esrgan",
                "reason": "Enhances artistic details and stylized content"
            },
            "screenshot": {
                "primary": "clarity",
                "alternative": "recraft",
                "reason": "Maintains UI element sharpness"
            }
        }

        return recommendations.get(image_type, recommendations["logo"])

    def estimate_upscaling_cost(
        self,
        num_images: int = 1,
        upscale_factor: int = 2,
        model: str = "clarity"
    ) -> Dict[str, Any]:
        """Estimate cost for upscaling operations"""

        # Cost estimates per model (approximate)
        model_costs = {
            "clarity": 0.02,
            "esrgan": 0.015,
            "topaz": 0.08,  # Higher cost for professional model
            "creative": 0.025,
            "aura": 0.03,
            "recraft": 0.02
        }

        # Factor multipliers
        factor_multipliers = {
            1: 1.0,
            2: 1.2,
            3: 1.5,
            4: 1.8
        }

        base_cost = model_costs.get(model, 0.02)
        multiplier = factor_multipliers.get(upscale_factor, 1.0)
        total_cost = base_cost * multiplier * num_images

        return {
            "num_images": num_images,
            "model": model,
            "upscale_factor": upscale_factor,
            "cost_per_image": base_cost * multiplier,
            "total_cost": total_cost,
            "currency": "USD"
        }