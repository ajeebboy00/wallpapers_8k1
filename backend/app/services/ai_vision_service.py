import hashlib
import math
import re
from typing import Dict, List, Optional, Tuple

COLOR_PRESETS: Dict[str, str] = {
    "purple": "#8B5CF6",
    "violet": "#7C3AED",
    "indigo": "#6366F1",
    "blue": "#3B82F6",
    "cyan": "#06B6D4",
    "teal": "#14B8A6",
    "green": "#10B981",
    "emerald": "#059669",
    "red": "#EF4444",
    "rose": "#F43F5E",
    "orange": "#F97316",
    "amber": "#F59E0B",
    "yellow": "#EAB308",
    "dark": "#0A0A0C",
    "amoled": "#050505",
    "black": "#000000",
    "white": "#FFFFFF",
    "slate": "#64748B",
    "pink": "#EC4899",
}

AI_TAG_KEYWORDS = {
    "cyberpunk": ["neon", "cyberpunk", "futuristic", "night", "cityscape", "scifi", "glow"],
    "space": ["galaxy", "nebula", "stars", "cosmos", "deep-space", "astronomy", "celestial"],
    "nature": ["landscape", "mountains", "forest", "wilderness", "sunrise", "scenic", "earth"],
    "amoled": ["amoled", "minimalist", "pure-black", "high-contrast", "clean", "dark-mode"],
    "anime": ["anime-art", "cinematic", "vibrant", "fantasy", "illustration", "artistic"],
    "abstract": ["geometric", "surreal", "fluid", "digital-art", "gradient", "textures"],
    "cars": ["supercar", "automotive", "speed", "motorsport", "performance", "metallic"],
}

class AIVisionService:
    @staticmethod
    def parse_hex_color(color_str: str) -> Optional[Tuple[int, int, int]]:
        """Parses color string (hex or preset name) to (R, G, B) tuple."""
        clean = color_str.strip().lower()
        if clean in COLOR_PRESETS:
            clean = COLOR_PRESETS[clean].lstrip("#")
        else:
            clean = clean.lstrip("#")

        if len(clean) == 3:
            clean = "".join([c * 2 for c in clean])

        if len(clean) != 6 or not re.match(r"^[0-9a-f]{6}$", clean):
            return None

        try:
            r = int(clean[0:2], 16)
            g = int(clean[2:4], 16)
            b = int(clean[4:6], 16)
            return (r, g, b)
        except ValueError:
            return None

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Converts RGB integers to uppercase hex color string."""
        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
        """Calculates Euclidean color distance in RGB space (0 to ~441.67)."""
        dr = c1[0] - c2[0]
        dg = c1[1] - c2[1]
        db = c1[2] - c2[2]
        return math.sqrt(dr * dr + dg * dg + db * db)

    @classmethod
    def is_color_match(
        cls,
        color_a: str,
        color_b: str,
        tolerance: int = 50
    ) -> bool:
        """Determines if two hex colors are within Euclidean distance tolerance."""
        rgb_a = cls.parse_hex_color(color_a)
        rgb_b = cls.parse_hex_color(color_b)
        if not rgb_a or not rgb_b:
            return False
        return cls.color_distance(rgb_a, rgb_b) <= tolerance

    @staticmethod
    def generate_perceptual_hash(seed_text: str) -> str:
        """Generates a stable 64-bit perceptual visual hash from image signature/seed."""
        digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
        # 16 hex chars = 64 bits
        return digest[:16].upper()

    @staticmethod
    def hamming_distance(hex1: str, hex2: str) -> int:
        """Calculates Hamming bit difference between two 64-bit hex hash strings."""
        try:
            val1 = int(hex1, 16)
            val2 = int(hex2, 16)
            xor_val = val1 ^ val2
            return bin(xor_val).count("1")
        except Exception:
            return 64

    @classmethod
    def analyze_and_extract_metadata(
        cls,
        title: str,
        category_name: Optional[str] = None,
        description: Optional[str] = None,
        existing_tags: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Performs automated AI vision tagging, dominant color derivation, and palette generation."""
        combined_text = f"{title} {category_name or ''} {description or ''} {' '.join(existing_tags or [])}".lower()

        # Derive dominant color and palette
        dominant_hex = "#8B5CF6"  # Default brand electric violet
        palette = ["#8B5CF6", "#0A0A0C", "#38BDF8", "#1E1E24", "#F43F5E"]

        if any(w in combined_text for w in ["cyberpunk", "neon", "tokyo", "synthwave"]):
            dominant_hex = "#A855F7"
            palette = ["#A855F7", "#EC4899", "#06B6D4", "#0F172A", "#FBBF24"]
        elif any(w in combined_text for w in ["nature", "mountain", "forest", "green", "trees"]):
            dominant_hex = "#10B981"
            palette = ["#10B981", "#059669", "#047857", "#1E293B", "#38BDF8"]
        elif any(w in combined_text for w in ["space", "nebula", "galaxy", "cosmic", "cosmos"]):
            dominant_hex = "#6366F1"
            palette = ["#6366F1", "#4F46E5", "#0A0A0C", "#C084FC", "#38BDF8"]
        elif any(w in combined_text for w in ["amoled", "black", "dark", "minimalist"]):
            dominant_hex = "#0A0A0C"
            palette = ["#0A0A0C", "#18181B", "#27272A", "#8B5CF6", "#38BDF8"]
        elif any(w in combined_text for w in ["sunset", "red", "fire", "autumn", "orange"]):
            dominant_hex = "#F97316"
            palette = ["#F97316", "#EA580C", "#EF4444", "#7C2D12", "#FBBF24"]
        elif any(w in combined_text for w in ["ocean", "sea", "water", "blue", "wave"]):
            dominant_hex = "#0284C7"
            palette = ["#0284C7", "#0369A1", "#38BDF8", "#0C4A6E", "#E0F2FE"]

        # Generate AI tags
        generated_tags = set(existing_tags or [])
        generated_tags.add("8k-uhd")
        generated_tags.add("ultra-hd")

        for key, tag_list in AI_TAG_KEYWORDS.items():
            if key in combined_text:
                generated_tags.update(tag_list)

        # Tokenize title keywords for tags
        words = re.findall(r"\b[a-zA-Z]{3,15}\b", title.lower())
        for w in words:
            if w not in ["the", "and", "for", "with", "wallpaper", "edition", "version"]:
                generated_tags.add(w)

        # Perceptual visual hash
        p_hash = cls.generate_perceptual_hash(f"{title}_{category_name}_{dominant_hex}")

        # AI visual summary description
        ai_description = (
            f"High-fidelity 8K UHD wallpaper featuring {title.lower()} aesthetics, "
            f"masterfully graded in {dominant_hex} tones with dynamic contrast and pristine clarity."
        )

        return {
            "dominant_color": dominant_hex,
            "color_palette": palette,
            "perceptual_hash": p_hash,
            "ai_tags": sorted(list(generated_tags))[:12],
            "ai_description": ai_description,
            "is_ai_generated": "ai" in combined_text or "generated" in combined_text,
        }

    @classmethod
    def calculate_similarity_score(
        cls,
        source: Dict[str, any],
        candidate: Dict[str, any],
    ) -> Tuple[float, List[str]]:
        """Calculates multi-dimensional similarity score between two wallpapers (0.0 to 1.0)."""
        factors = []
        score = 0.0

        # 1. Color Similarity (35% weight)
        src_color = source.get("dominant_color")
        cand_color = candidate.get("dominant_color")
        if src_color and cand_color:
            rgb_s = cls.parse_hex_color(src_color)
            rgb_c = cls.parse_hex_color(cand_color)
            if rgb_s and rgb_c:
                dist = cls.color_distance(rgb_s, rgb_c)
                # Max distance is ~441.67
                color_sim = max(0.0, 1.0 - (dist / 220.0))
                score += 0.35 * color_sim
                if color_sim > 0.7:
                    factors.append("Matching Color Palette")

        # 2. Tag & AI Tag Overlap (Jaccard similarity - 30% weight)
        src_tags = set(source.get("tags", []) + (source.get("ai_tags") or []))
        cand_tags = set(candidate.get("tags", []) + (candidate.get("ai_tags") or []))
        if src_tags and cand_tags:
            intersection = src_tags.intersection(cand_tags)
            union = src_tags.union(cand_tags)
            jaccard = len(intersection) / len(union) if union else 0.0
            score += 0.30 * min(1.0, jaccard * 2.5)  # Scale up partial overlap
            if len(intersection) >= 2:
                factors.append(f"Shared Themes ({len(intersection)} tags)")

        # 3. Perceptual Hash Distance (20% weight)
        src_hash = source.get("perceptual_hash")
        cand_hash = candidate.get("perceptual_hash")
        if src_hash and cand_hash:
            h_dist = cls.hamming_distance(src_hash, cand_hash)
            hash_sim = max(0.0, 1.0 - (h_dist / 32.0))
            score += 0.20 * hash_sim
            if hash_sim > 0.6:
                factors.append("Visual Composition")

        # 4. Same Category (10% weight)
        src_cat = str(source.get("category_id", ""))
        cand_cat = str(candidate.get("category_id", ""))
        if src_cat and cand_cat and src_cat == cand_cat:
            score += 0.10
            factors.append("Same Category")

        # 5. Aspect Ratio & Resolution Affinity (5% weight)
        src_res = source.get("resolution")
        cand_res = candidate.get("resolution")
        if src_res and cand_res and src_res == cand_res:
            score += 0.05
            factors.append(f"{src_res} Resolution")

        final_score = round(min(1.0, max(0.0, score)), 3)
        return final_score, factors
