"""
Flux.1 Pro Image Generation Tool - AI-powered visual content creation
High-quality image generation for Devlar marketing and product materials
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
import fal_client
from loguru import logger
from crewai.tools import BaseTool

class FluxImageGenerationTool(BaseTool):
    """
    Flux.1 Pro image generation tool via fal.ai.
    Creates high-quality images for marketing, product mockups, and visual content.
    """

    name: str = "flux_image_generation"
    description: str = (
        "Generate high-quality images using Flux.1 Pro AI model. "
        "Create marketing visuals, product mockups, social media content, and brand materials."
    )

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("FAL_API_KEY")
        if not self.api_key:
            raise ValueError("FAL_API_KEY environment variable is required")

        # Configure fal client
        fal_client.api_key = self.api_key
        self.model = "fal-ai/flux-pro"

    def _run(
        self,
        prompt: str,
        style: str = "professional",
        aspect_ratio: str = "16:9",
        quality: str = "high",
        brand_context: str = "devlar",
        content_type: str = "marketing",
        safety_tolerance: int = 2
    ) -> str:
        """
        Generate image using Flux.1 Pro

        Args:
            prompt: Detailed description of the image to generate
            style: Visual style (professional, modern, minimalist, tech, creative)
            aspect_ratio: Image aspect ratio (16:9, 1:1, 9:16, 4:3)
            quality: Image quality (high, medium, low)
            brand_context: Brand context for consistent styling
            content_type: Type of content (marketing, product, social, mockup)
            safety_tolerance: Content safety level (1-5, higher = more permissive)

        Returns:
            Generated image information and download details
        """
        try:
            logger.info(f"🎨 Generating image with Flux.1 Pro: {prompt[:50]}...")

            # Enhance prompt with Devlar brand context
            enhanced_prompt = self._enhance_prompt_with_context(
                prompt, style, brand_context, content_type
            )

            # Generate image
            result = self._generate_image(
                enhanced_prompt,
                aspect_ratio=aspect_ratio,
                quality=quality,
                safety_tolerance=safety_tolerance
            )

            # Format response
            return self._format_generation_result(result, prompt, enhanced_prompt)

        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return f"Image generation failed: {str(e)}"

    def _generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        quality: str = "high",
        safety_tolerance: int = 2
    ) -> Dict[str, Any]:
        """Generate image using fal.ai Flux.1 Pro"""

        # Map quality to model parameters
        quality_settings = {
            "low": {"num_inference_steps": 20, "guidance_scale": 3.5},
            "medium": {"num_inference_steps": 28, "guidance_scale": 4.0},
            "high": {"num_inference_steps": 35, "guidance_scale": 4.5}
        }

        # Map aspect ratio to dimensions
        aspect_ratios = {
            "1:1": {"width": 1024, "height": 1024},
            "16:9": {"width": 1344, "height": 768},
            "9:16": {"width": 768, "height": 1344},
            "4:3": {"width": 1152, "height": 896},
            "3:4": {"width": 896, "height": 1152}
        }

        settings = quality_settings.get(quality, quality_settings["high"])
        dimensions = aspect_ratios.get(aspect_ratio, aspect_ratios["16:9"])

        # Generate image
        result = fal_client.subscribe(
            self.model,
            arguments={
                "prompt": prompt,
                "image_size": {
                    "width": dimensions["width"],
                    "height": dimensions["height"]
                },
                "num_inference_steps": settings["num_inference_steps"],
                "guidance_scale": settings["guidance_scale"],
                "num_images": 1,
                "enable_safety_checker": safety_tolerance < 4,
                "safety_tolerance": safety_tolerance,
                "output_format": "jpeg"
            }
        )

        return result

    def _enhance_prompt_with_context(
        self,
        prompt: str,
        style: str,
        brand_context: str,
        content_type: str
    ) -> str:
        """Enhance prompt with brand context and style guidelines"""

        # Devlar brand context
        brand_contexts = {
            "devlar": {
                "colors": "modern blue and white color scheme, clean gradients",
                "style": "professional, tech-forward, minimalist, AI-focused",
                "mood": "innovative, trustworthy, developer-friendly, slightly futuristic"
            }
        }

        # Style enhancements
        style_prompts = {
            "professional": "clean, polished, corporate, high-end, sophisticated",
            "modern": "contemporary, sleek, minimalist, geometric, tech-inspired",
            "minimalist": "simple, clean lines, lots of white space, focused composition",
            "tech": "digital, futuristic, high-tech, UI elements, screens, coding",
            "creative": "artistic, unique perspective, bold colors, dynamic composition"
        }

        # Content type specific enhancements
        content_prompts = {
            "marketing": "professional marketing material, compelling visual, clear focal point",
            "product": "product showcase, clean background, studio lighting, high detail",
            "social": "social media optimized, engaging, shareable, eye-catching",
            "mockup": "realistic mockup, device integration, contextual usage, lifestyle",
            "hero": "hero section style, bold, inspiring, large-scale composition",
            "feature": "feature highlight, clear demonstration, benefits focused"
        }

        # Build enhanced prompt
        enhanced = prompt

        # Add brand context
        if brand_context in brand_contexts:
            brand_info = brand_contexts[brand_context]
            enhanced += f", {brand_info['style']}, {brand_info['colors']}, {brand_info['mood']}"

        # Add style
        if style in style_prompts:
            enhanced += f", {style_prompts[style]}"

        # Add content type context
        if content_type in content_prompts:
            enhanced += f", {content_prompts[content_type]}"

        # Add quality and technical specifications
        enhanced += ", high quality, 8k resolution, professional photography, studio lighting, sharp focus"

        return enhanced

    def _format_generation_result(
        self,
        result: Dict[str, Any],
        original_prompt: str,
        enhanced_prompt: str
    ) -> str:
        """Format the generation result"""

        if not result or 'images' not in result:
            return "Image generation completed but no image data returned"

        image_data = result['images'][0]
        image_url = image_data.get('url', 'No URL provided')

        # Extract metadata
        width = image_data.get('width', 'Unknown')
        height = image_data.get('height', 'Unknown')
        file_size = image_data.get('file_size', 'Unknown')

        formatted_result = f"""
# 🎨 Image Generated Successfully

## Image Details
**URL**: {image_url}
**Dimensions**: {width} x {height}
**File Size**: {file_size}
**Format**: JPEG
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Prompts Used
**Original Prompt**: {original_prompt}

**Enhanced Prompt**: {enhanced_prompt[:200]}...

## Usage Recommendations
- **Marketing**: Use for social media posts, website headers, promotional materials
- **Product**: Integrate into product documentation and marketing pages
- **Presentations**: Include in pitch decks and investor materials
- **Web**: Optimize for web usage by compressing if needed

## Next Steps
1. Download the image from the URL above
2. Review for brand compliance and quality
3. Optimize for intended usage platform
4. Consider generating variations if needed

---
*Generated with Flux.1 Pro via fal.ai*
"""

        return formatted_result

    # Devlar-specific image generation presets
    def generate_product_hero_image(
        self,
        product_name: str,
        key_features: List[str],
        target_audience: str = "developers"
    ) -> str:
        """Generate hero image for Devlar product"""

        prompt = f"""
Professional hero image for {product_name}, a productivity tool for {target_audience}.
Show {', '.join(key_features[:3])} in a clean, modern interface.
Include laptop or browser mockup with the product interface visible.
Professional workspace setting with good lighting.
"""

        return self._run(
            prompt=prompt,
            style="professional",
            aspect_ratio="16:9",
            content_type="hero"
        )

    def generate_feature_illustration(
        self,
        feature_name: str,
        feature_description: str,
        product_context: str = "productivity app"
    ) -> str:
        """Generate feature illustration for documentation"""

        prompt = f"""
Clean illustration showing {feature_name} feature for {product_context}.
{feature_description}
Isometric or flat design style, clear visual hierarchy.
Step-by-step visual flow if applicable.
Professional UI elements, modern design.
"""

        return self._run(
            prompt=prompt,
            style="modern",
            aspect_ratio="4:3",
            content_type="feature"
        )

    def generate_social_media_graphic(
        self,
        message: str,
        platform: str = "linkedin",
        include_text: bool = True
    ) -> str:
        """Generate social media graphic"""

        aspect_ratios = {
            "linkedin": "16:9",
            "twitter": "16:9",
            "instagram": "1:1",
            "facebook": "16:9"
        }

        prompt = f"""
Social media graphic for {platform} featuring: {message}
Modern, engaging design with Devlar branding.
{"Include text overlay with the message" if include_text else "Visual representation without text overlay"}
Professional but approachable style, optimized for social media engagement.
"""

        return self._run(
            prompt=prompt,
            style="modern",
            aspect_ratio=aspect_ratios.get(platform, "16:9"),
            content_type="social"
        )

    def generate_app_mockup(
        self,
        app_name: str,
        app_type: str,
        key_screens: List[str]
    ) -> str:
        """Generate app mockup for marketing"""

        prompt = f"""
Professional mockup of {app_name} {app_type} showing {', '.join(key_screens[:2])}.
Multiple device views (desktop, mobile) with realistic shadows and reflections.
Clean background, professional photography style.
Modern UI design with good typography and spacing.
"""

        return self._run(
            prompt=prompt,
            style="professional",
            aspect_ratio="16:9",
            content_type="mockup"
        )

    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of generated images (placeholder for tracking)"""
        # In a real implementation, this would retrieve from a database
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "prompt": "Example generated image",
                "style": "professional",
                "url": "https://example.com/image.jpg",
                "status": "completed"
            }
        ]

    def estimate_generation_cost(
        self,
        num_images: int = 1,
        quality: str = "high",
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """Estimate cost for image generation"""

        # Simplified cost estimation
        base_cost_per_image = {
            "low": 0.05,
            "medium": 0.08,
            "high": 0.12
        }

        # Aspect ratio cost multipliers
        aspect_multipliers = {
            "1:1": 1.0,
            "16:9": 1.1,
            "9:16": 1.1,
            "4:3": 1.0,
            "3:4": 1.0
        }

        base_cost = base_cost_per_image.get(quality, 0.08)
        multiplier = aspect_multipliers.get(aspect_ratio, 1.0)
        total_cost = base_cost * multiplier * num_images

        return {
            "num_images": num_images,
            "cost_per_image": base_cost * multiplier,
            "total_cost": total_cost,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "currency": "USD"
        }