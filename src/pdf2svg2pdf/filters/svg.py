#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/filters/svg.py
"""SVG filter implementations."""

from __future__ import annotations

import re
import subprocess
from collections import Counter

from loguru import logger

from ..types import FilterConfig
from .base import Filter


class SVGOptimizeFilter(Filter):
    """Optimize SVG using SVGO."""
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "optimize"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Optimize SVG file size and structure"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"svg"}
    
    def apply(self, content: str) -> str:
        """Apply SVGO optimization to SVG.
        
        Args:
            content: SVG content as string
            
        Returns:
            Optimized SVG content
        """
        # Check if svgo is available
        try:
            subprocess.run(["svgo", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("SVGO not available, skipping optimization")
            return content
        
        try:
            # Run svgo
            result = subprocess.run(
                ["svgo", "--input", "-", "--output", "-", "--multipass"],
                input=content,
                capture_output=True,
                text=True,
                check=True,
            )
            
            optimized = result.stdout
            
            # Log optimization results
            original_size = len(content)
            optimized_size = len(optimized)
            ratio = (1 - optimized_size / original_size) * 100
            logger.debug(
                f"Optimized SVG from {original_size} to {optimized_size} chars "
                f"({ratio:.1f}% reduction)"
            )
            
            return optimized
            
        except subprocess.CalledProcessError as e:
            logger.error(f"SVGO failed: {e.stderr}")
            # Return original content on error
            return content


class SVGTransparentWhiteFilter(Filter):
    """Make white backgrounds transparent in SVG."""
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "transparent_white"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Make white backgrounds transparent"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"svg"}
    
    def apply(self, content: str) -> str:
        """Make white fills transparent.
        
        Args:
            content: SVG content as string
            
        Returns:
            Modified SVG content
        """
        # Replace various white fill patterns with transparent
        patterns = [
            (r'fill:rgb\(100%,100%,100%\);', 'fill:none;'),
            (r'fill:rgb\(255,255,255\);', 'fill:none;'),
            (r'fill:#ffffff;', 'fill:none;'),
            (r'fill:#FFFFFF;', 'fill:none;'),
            (r'fill="white"', 'fill="none"'),
            (r'fill="rgb\(255,255,255\)"', 'fill="none"'),
            (r'fill="#ffffff"', 'fill="none"'),
            (r'fill="#FFFFFF"', 'fill="none"'),
        ]
        
        modified = content
        replacements = 0
        
        for pattern, replacement in patterns:
            modified, count = re.subn(pattern, replacement, modified)
            replacements += count
        
        if replacements > 0:
            logger.debug(f"Made {replacements} white fills transparent")
        
        return modified


class SVGColorReplaceFilter(Filter):
    """Replace colors in SVG."""
    
    def __init__(self, config: FilterConfig | None = None) -> None:
        """Initialize filter.
        
        Args:
            config: Filter configuration
        """
        super().__init__(config)
        # Get color mappings from config
        self.color_map = {}
        if config and config.parameters:
            self.color_map = config.parameters.get("color_map", {})
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "color_replace"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Replace specific colors in SVG"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"svg"}
    
    def apply(self, content: str) -> str:
        """Replace colors based on mapping.
        
        Args:
            content: SVG content as string
            
        Returns:
            Modified SVG content
        """
        modified = content
        
        for old_color, new_color in self.color_map.items():
            # Replace in various formats
            patterns = [
                (f'fill:{old_color};', f'fill:{new_color};'),
                (f'fill="{old_color}"', f'fill="{new_color}"'),
                (f'stroke:{old_color};', f'stroke:{new_color};'),
                (f'stroke="{old_color}"', f'stroke="{new_color}"'),
            ]
            
            for pattern, replacement in patterns:
                modified = modified.replace(pattern, replacement)
        
        return modified


class SVGFillUnifyFilter(Filter):
    """Unify all fills to the most common or specified color."""
    
    def __init__(self, config: FilterConfig | None = None) -> None:
        """Initialize filter.
        
        Args:
            config: Filter configuration
        """
        super().__init__(config)
        # Get target color from config
        self.target_color = None
        self.use_most_common = True
        if config and config.parameters:
            self.target_color = config.parameters.get("target_color")
            self.use_most_common = config.parameters.get("use_most_common", True)
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "fill_unify"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Unify all fill colors"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"svg"}
    
    def apply(self, content: str) -> str:
        """Unify fill colors.
        
        Args:
            content: SVG content as string
            
        Returns:
            Modified SVG content
        """
        # Find all fill colors
        fill_pattern = r'fill:([^;]+);'
        fills = re.findall(fill_pattern, content)
        
        if not fills:
            return content
        
        # Determine target color
        if self.use_most_common and not self.target_color:
            # Find most common fill
            fill_counts = Counter(fills)
            # Exclude 'none' and transparent colors
            fill_counts = {
                k: v for k, v in fill_counts.items()
                if k not in ['none', 'transparent', 'rgba(0,0,0,0)']
            }
            if fill_counts:
                self.target_color = fill_counts.most_common(1)[0][0]
        
        if not self.target_color:
            return content
        
        # Replace all fills except 'none'
        def replace_fill(match):
            current_fill = match.group(1)
            if current_fill in ['none', 'transparent']:
                return match.group(0)
            return f'fill:{self.target_color};'
        
        modified = re.sub(fill_pattern, replace_fill, content)
        
        logger.debug(f"Unified fills to {self.target_color}")
        return modified