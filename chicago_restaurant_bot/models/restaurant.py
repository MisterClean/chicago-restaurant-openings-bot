from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class Restaurant:
    """Represents a restaurant from the Chicago Data Portal."""
    name: str
    address: str
    zip_code: str
    license_description: str
    business_activity: Optional[str]
    square_footage: Optional[str]
    application_date: datetime
    ward: Optional[str]
    
    def format_announcement(self, config) -> str:
        """
        Format restaurant details into a social media announcement.
        
        Args:
            config: Config object containing feature flags and templates
        
        Returns:
            Formatted announcement string
        """
        template = config.post_template
        features = config.features
        
        # Start with header
        parts = [template.get('header', "🆕 New Restaurant Alert!\n")]
        
        # Add name
        name_prefix = template.get('name_prefix', "🍽️") if features.use_emojis else ""
        parts.append(f"{name_prefix} {self.name}")
        
        # Add address
        addr_prefix = template.get('address_prefix', "📍") if features.use_emojis else ""
        parts.append(f"{addr_prefix} {self.address}, Chicago IL {self.zip_code}")
        
        # Add business activity if enabled and available
        if features.include_business_activity and self.business_activity:
            activity_prefix = template.get('activity_prefix', "🍳") if features.use_emojis else ""
            parts.append(f"{activity_prefix} {self.business_activity}")
            
        # Add square footage if enabled and available
        if features.include_square_footage and self.square_footage:
            sqft_prefix = template.get('square_footage_prefix', "📐") if features.use_emojis else ""
            parts.append(f"{sqft_prefix} {self.square_footage} sq ft")
            
        # Add ward if enabled and available
        if features.include_ward and self.ward:
            ward_prefix = template.get('ward_prefix', "📍") if features.use_emojis else ""
            parts.append(f"{ward_prefix} Located in Ward {self.ward}")
        
        # Join parts with newlines
        announcement = "\n".join(parts)
        
        # Add hashtags if enabled
        if features.add_hashtags and config.hashtags:
            announcement += "\n\n" + " ".join(f"#{tag}" for tag in config.hashtags)
            
        return announcement
    
    def passes_filters(self, filters: Dict[str, list]) -> bool:
        """
        Check if restaurant passes configured filters.
        
        Args:
            filters: Dictionary of filter lists
            
        Returns:
            True if restaurant passes all filters, False otherwise
        """
        # Check excluded license types
        excluded_types = filters.get('excluded_license_types', [])
        if excluded_types and self.license_description in excluded_types:
            return False
            
        # Check included wards
        included_wards = filters.get('included_wards', [])
        if included_wards and self.ward not in included_wards:
            return False
            
        # Check included zip codes
        included_zips = filters.get('included_zip_codes', [])
        if included_zips and self.zip_code not in included_zips:
            return False
            
        return True
