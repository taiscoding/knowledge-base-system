#!/usr/bin/env python3
"""
Personal Data Intelligence Tracker
Tracks historical patterns, measurements, and contextual data to provide 
specific intelligence for AI context enhancement.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class MeasurementReading:
    """Represents a single measurement reading with timestamp."""
    value: str  # e.g., "140/80", "98.6°F", "150 lbs"
    timestamp: datetime
    measurement_type: str  # e.g., "blood_pressure", "temperature", "weight"
    context: Dict[str, Any]  # Additional context like device used, location, etc.

@dataclass
class VisitPattern:
    """Represents patterns in healthcare visits or appointments."""
    provider_token: str  # e.g., "[PHYSICIAN]", "[SPECIALIST]"
    visit_count: int
    time_period: str  # e.g., "past_month", "past_3_months"
    visit_dates: List[datetime]
    purposes: List[str]  # Reasons for visits
    frequency_pattern: str  # e.g., "weekly", "monthly", "as_needed"

@dataclass
class EquipmentResource:
    """Represents available equipment or resources."""
    name: str  # e.g., "automatic blood pressure cuff", "glucose meter"
    category: str  # e.g., "medical_device", "fitness_equipment"
    availability: str  # e.g., "owned", "access_through_provider", "needs_purchase"
    last_used: Optional[datetime]
    capabilities: List[str]  # What it can measure/do

class PersonalDataIntelligenceTracker:
    """Tracks and analyzes personal data patterns for intelligent context generation."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.intelligence_dir = self.base_path / "data" / "intelligence"
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files for different types of intelligence
        self.measurements_file = self.intelligence_dir / "measurements.json"
        self.visit_patterns_file = self.intelligence_dir / "visit_patterns.json" 
        self.equipment_file = self.intelligence_dir / "equipment.json"
        self.context_history_file = self.intelligence_dir / "context_history.json"
        
        # Load existing data
        self.measurements = self._load_measurements()
        self.visit_patterns = self._load_visit_patterns()
        self.equipment = self._load_equipment()
        self.context_history = self._load_context_history()
    
    def extract_and_store_measurement(self, content: str, content_metadata: Dict[str, Any]) -> List[MeasurementReading]:
        """Extract measurement readings from content and store them."""
        readings = []
        timestamp = datetime.fromisoformat(content_metadata.get('created', datetime.now().isoformat()))
        
        # Blood pressure patterns
        bp_pattern = r'(\d{2,3})/(\d{2,3})(?:\s*mmHg)?'
        bp_matches = re.findall(bp_pattern, content, re.IGNORECASE)
        for systolic, diastolic in bp_matches:
            reading = MeasurementReading(
                value=f"{systolic}/{diastolic}",
                timestamp=timestamp,
                measurement_type="blood_pressure",
                context={
                    "unit": "mmHg",
                    "source": content_metadata.get('id', 'unknown'),
                    "content_type": content_metadata.get('type', 'unknown')
                }
            )
            readings.append(reading)
            self._store_measurement(reading)
        
        # Temperature patterns
        temp_pattern = r'(\d{2,3}(?:\.\d)?)\s*°?[Ff]?(?:\s*(?:degrees?|°|temp))?'
        temp_matches = re.findall(temp_pattern, content, re.IGNORECASE)
        for temp_value in temp_matches:
            try:
                if 95 <= float(temp_value) <= 110:  # Reasonable human temperature range
                    reading = MeasurementReading(
                        value=f"{temp_value}°F",
                        timestamp=timestamp,
                        measurement_type="temperature",
                        context={
                            "unit": "fahrenheit",
                            "source": content_metadata.get('id', 'unknown')
                        }
                    )
                    readings.append(reading)
                    self._store_measurement(reading)
            except ValueError:
                continue
        
        # Weight patterns
        weight_pattern = r'(\d{2,3}(?:\.\d)?)\s*(?:lbs?|pounds?|kg|kilograms?)'
        weight_matches = re.findall(weight_pattern, content, re.IGNORECASE)
        for weight_value in weight_matches:
            reading = MeasurementReading(
                value=weight_value,
                timestamp=timestamp,
                measurement_type="weight", 
                context={
                    "unit": "lbs" if "lb" in content.lower() else "kg",
                    "source": content_metadata.get('id', 'unknown')
                }
            )
            readings.append(reading)
            self._store_measurement(reading)
        
        return readings
    
    def track_visit_pattern(self, content: str, content_metadata: Dict[str, Any]) -> Optional[VisitPattern]:
        """Track healthcare visit patterns from content."""
        timestamp = datetime.fromisoformat(content_metadata.get('created', datetime.now().isoformat()))
        
        # Look for provider tokens and visit indicators
        provider_pattern = r'\[PHYSICIAN\]|\[DOCTOR\]|\[SPECIALIST\]|\[PROVIDER\]'
        visit_indicators = ['appointment', 'visit', 'checkup', 'consultation', 'follow.?up']
        
        provider_matches = re.findall(provider_pattern, content, re.IGNORECASE)
        has_visit_indicator = any(re.search(indicator, content, re.IGNORECASE) for indicator in visit_indicators)
        
        if provider_matches and has_visit_indicator:
            provider_token = provider_matches[0]
            
            # Update or create visit pattern
            pattern_key = f"{provider_token}_visits"
            if pattern_key not in self.visit_patterns:
                self.visit_patterns[pattern_key] = {
                    "provider_token": provider_token,
                    "visits": [],
                    "purposes": []
                }
            
            # Add this visit
            visit_data = {
                "date": timestamp.isoformat(),
                "purpose": self._extract_visit_purpose(content),
                "source": content_metadata.get('id', 'unknown')
            }
            
            self.visit_patterns[pattern_key]["visits"].append(visit_data)
            self._save_visit_patterns()
            
            return self._calculate_visit_pattern(pattern_key)
        
        return None
    
    def track_equipment_mention(self, content: str, content_metadata: Dict[str, Any]) -> List[EquipmentResource]:
        """Track mentions of medical equipment or resources."""
        equipment_found = []
        timestamp = datetime.fromisoformat(content_metadata.get('created', datetime.now().isoformat()))
        
        # Medical equipment patterns
        equipment_patterns = {
            "blood_pressure_cuff": [
                r'(?:automatic\s+)?blood\s+pressure\s+(?:cuff|monitor|machine)',
                r'bp\s+(?:cuff|monitor)',
                r'sphygmomanometer'
            ],
            "glucose_meter": [
                r'glucose\s+(?:meter|monitor)',
                r'blood\s+sugar\s+(?:meter|tester)',
                r'glucometer'
            ],
            "thermometer": [
                r'(?:digital\s+)?thermometer',
                r'temp\s+(?:gun|scanner)'
            ],
            "scale": [
                r'(?:digital\s+)?(?:bathroom\s+)?scale',
                r'weight\s+scale'
            ]
        }
        
        for equipment_type, patterns in equipment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Determine availability from context
                    availability = "owned"  # Default assumption
                    if any(word in content.lower() for word in ["need", "buy", "get", "purchase"]):
                        availability = "needs_purchase"
                    elif any(word in content.lower() for word in ["borrowed", "clinic", "office"]):
                        availability = "access_through_provider"
                    
                    equipment = EquipmentResource(
                        name=equipment_type.replace("_", " "),
                        category="medical_device",
                        availability=availability,
                        last_used=timestamp if availability == "owned" else None,
                        capabilities=self._get_equipment_capabilities(equipment_type)
                    )
                    
                    equipment_found.append(equipment)
                    self._store_equipment(equipment)
        
        return equipment_found
    
    def generate_contextual_intelligence(self, query: str, privacy_tokens: Dict[str, str]) -> Dict[str, Any]:
        """Generate specific contextual intelligence for a given query."""
        intelligence = {
            "relevant_measurements": [],
            "visit_patterns": [],
            "available_equipment": [],
            "historical_context": "",
            "specific_recommendations": []
        }
        
        query_lower = query.lower()
        
        # Blood pressure context
        if "blood pressure" in query_lower or "[CONDITION]" in query:
            # Get recent BP readings
            recent_bp = self._get_recent_measurements("blood_pressure", days=30)
            if recent_bp:
                intelligence["relevant_measurements"] = [
                    f"{reading['value']}" for reading in recent_bp[-3:]  # Last 3 readings
                ]
                
            # Get visit patterns for physicians
            physician_visits = self._get_provider_visit_pattern("[PHYSICIAN]", days=30)
            if physician_visits:
                intelligence["visit_patterns"] = physician_visits
        
        # Generate comprehensive context string
        context_parts = []
        
        if intelligence["visit_patterns"]:
            visit_info = intelligence["visit_patterns"]
            context_parts.append(
                f"[PATIENT] has visited [PHYSICIAN] {visit_info['count']} times in the past month for blood pressure checks"
            )
        
        if intelligence["relevant_measurements"]:
            readings_text = ", ".join(intelligence["relevant_measurements"])
            context_parts.append(f"These were the past readings: {readings_text}")
        
        # Check for equipment
        bp_equipment = self._get_equipment_by_type("blood_pressure_cuff")
        if bp_equipment:
            context_parts.append("Patient has an automatic blood pressure cuff")
        
        intelligence["contextual_summary"] = ". ".join(context_parts) if context_parts else ""
        
        return intelligence
    
    def _store_measurement(self, reading: MeasurementReading):
        """Store a measurement reading."""
        if reading.measurement_type not in self.measurements:
            self.measurements[reading.measurement_type] = []
        
        self.measurements[reading.measurement_type].append({
            "value": reading.value,
            "timestamp": reading.timestamp.isoformat(),
            "context": reading.context
        })
        
        self._save_measurements()
    
    def _store_equipment(self, equipment: EquipmentResource):
        """Store equipment information."""
        equipment_key = equipment.name.replace(" ", "_")
        self.equipment[equipment_key] = {
            "name": equipment.name,
            "category": equipment.category,
            "availability": equipment.availability,
            "last_used": equipment.last_used.isoformat() if equipment.last_used else None,
            "capabilities": equipment.capabilities
        }
        
        self._save_equipment()
    
    def _get_recent_measurements(self, measurement_type: str, days: int = 30) -> List[Dict]:
        """Get recent measurements of a specific type."""
        if measurement_type not in self.measurements:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []
        
        for measurement in self.measurements[measurement_type]:
            measurement_date = datetime.fromisoformat(measurement["timestamp"])
            if measurement_date >= cutoff_date:
                recent.append(measurement)
        
        return sorted(recent, key=lambda x: x["timestamp"])
    
    def _get_provider_visit_pattern(self, provider_token: str, days: int = 30) -> Optional[Dict]:
        """Get visit pattern for a specific provider."""
        pattern_key = f"{provider_token}_visits"
        if pattern_key not in self.visit_patterns:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_visits = []
        
        for visit in self.visit_patterns[pattern_key]["visits"]:
            visit_date = datetime.fromisoformat(visit["date"])
            if visit_date >= cutoff_date:
                recent_visits.append(visit)
        
        if recent_visits:
            return {
                "provider": provider_token,
                "count": len(recent_visits),
                "period": f"past {days} days" if days != 30 else "past month",
                "visits": recent_visits
            }
        
        return None
    
    def _get_equipment_by_type(self, equipment_type: str) -> List[Dict]:
        """Get equipment by type."""
        matching_equipment = []
        
        for equipment_key, equipment_data in self.equipment.items():
            if equipment_type in equipment_key or equipment_type in equipment_data.get("name", ""):
                matching_equipment.append(equipment_data)
        
        return matching_equipment
    
    def _calculate_visit_pattern(self, pattern_key: str) -> VisitPattern:
        """Calculate visit pattern from stored data."""
        pattern_data = self.visit_patterns[pattern_key]
        visits = pattern_data["visits"]
        
        # Sort visits by date
        sorted_visits = sorted(visits, key=lambda x: x["date"])
        visit_dates = [datetime.fromisoformat(v["date"]) for v in sorted_visits]
        
        # Calculate frequency
        if len(visit_dates) >= 2:
            time_span = (visit_dates[-1] - visit_dates[0]).days
            if time_span > 0:
                frequency = len(visit_dates) / (time_span / 30)  # visits per month
                if frequency >= 4:
                    frequency_pattern = "weekly"
                elif frequency >= 1:
                    frequency_pattern = "monthly"
                else:
                    frequency_pattern = "as_needed"
            else:
                frequency_pattern = "as_needed"
        else:
            frequency_pattern = "single_visit"
        
        return VisitPattern(
            provider_token=pattern_data["provider_token"],
            visit_count=len(visits),
            time_period="recent",
            visit_dates=visit_dates,
            purposes=[v.get("purpose", "unknown") for v in visits],
            frequency_pattern=frequency_pattern
        )
    
    def _load_measurements(self) -> Dict[str, List]:
        """Load measurements from storage."""
        if self.measurements_file.exists():
            with open(self.measurements_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_measurements(self):
        """Save measurements to storage."""
        with open(self.measurements_file, 'w') as f:
            json.dump(self.measurements, f, indent=2)
    
    def _load_visit_patterns(self) -> Dict[str, Any]:
        """Load visit patterns from storage."""
        if self.visit_patterns_file.exists():
            with open(self.visit_patterns_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_visit_patterns(self):
        """Save visit patterns to storage."""
        with open(self.visit_patterns_file, 'w') as f:
            json.dump(self.visit_patterns, f, indent=2)
    
    def _load_equipment(self) -> Dict[str, Any]:
        """Load equipment data from storage."""
        if self.equipment_file.exists():
            with open(self.equipment_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_equipment(self):
        """Save equipment data to storage."""
        with open(self.equipment_file, 'w') as f:
            json.dump(self.equipment, f, indent=2)
    
    def _load_context_history(self) -> Dict[str, Any]:
        """Load context history from storage."""
        if self.context_history_file.exists():
            with open(self.context_history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_context_history(self):
        """Save context history to storage."""
        with open(self.context_history_file, 'w') as f:
            json.dump(self.context_history, f, indent=2)
    
    def track_visit_pattern(self, content: str, content_metadata: Dict[str, Any]) -> Optional[VisitPattern]:
        """Track healthcare visit patterns from content."""
        timestamp_str = content_metadata.get('created', datetime.now().isoformat())
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = timestamp_str
        
        # Look for provider tokens and visit indicators
        provider_pattern = r'\[PHYSICIAN\]|\[DOCTOR\]|\[SPECIALIST\]|\[PROVIDER\]'
        visit_indicators = ['appointment', 'visit', 'checkup', 'consultation', 'follow.?up']
        
        provider_matches = re.findall(provider_pattern, content, re.IGNORECASE)
        has_visit_indicator = any(re.search(indicator, content, re.IGNORECASE) for indicator in visit_indicators)
        
        if provider_matches and has_visit_indicator:
            provider_token = provider_matches[0]
            
            # Update or create visit pattern
            pattern_key = f"{provider_token}_visits"
            if pattern_key not in self.visit_patterns:
                self.visit_patterns[pattern_key] = {
                    "provider_token": provider_token,
                    "visits": [],
                    "purposes": []
                }
            
            # Add this visit
            visit_data = {
                "date": timestamp.isoformat(),
                "purpose": self._extract_visit_purpose(content),
                "source": content_metadata.get('id', 'unknown')
            }
            
            self.visit_patterns[pattern_key]["visits"].append(visit_data)
            self._save_visit_patterns()
            
            return self._calculate_visit_pattern(pattern_key)
        
        return None
    
    def track_equipment_mention(self, content: str, content_metadata: Dict[str, Any]) -> List[EquipmentResource]:
        """Track mentions of medical equipment or resources."""
        equipment_found = []
        timestamp_str = content_metadata.get('created', datetime.now().isoformat())
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = timestamp_str
        
        # Medical equipment patterns
        equipment_patterns = {
            "blood_pressure_cuff": [
                r'(?:automatic\s+)?blood\s+pressure\s+(?:cuff|monitor|machine)',
                r'bp\s+(?:cuff|monitor)',
                r'sphygmomanometer'
            ],
            "glucose_meter": [
                r'glucose\s+(?:meter|monitor)',
                r'blood\s+sugar\s+(?:meter|tester)',
                r'glucometer'
            ],
            "thermometer": [
                r'(?:digital\s+)?thermometer',
                r'temp\s+(?:gun|scanner)'
            ],
            "scale": [
                r'(?:digital\s+)?(?:bathroom\s+)?scale',
                r'weight\s+scale'
            ]
        }
        
        for equipment_type, patterns in equipment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Determine availability from context
                    availability = "owned"  # Default assumption
                    if any(word in content.lower() for word in ["need", "buy", "get", "purchase"]):
                        availability = "needs_purchase"
                    elif any(word in content.lower() for word in ["borrowed", "clinic", "office"]):
                        availability = "access_through_provider"
                    
                    equipment = EquipmentResource(
                        name=equipment_type.replace("_", " "),
                        category="medical_device",
                        availability=availability,
                        last_used=timestamp if availability == "owned" else None,
                        capabilities=self._get_equipment_capabilities(equipment_type)
                    )
                    
                    equipment_found.append(equipment)
                    self._store_equipment(equipment)
        
        return equipment_found
    
    def _calculate_visit_pattern(self, pattern_key: str) -> VisitPattern:
        """Calculate visit pattern from stored data."""
        pattern_data = self.visit_patterns[pattern_key]
        visits = pattern_data["visits"]
        
        # Sort visits by date
        sorted_visits = sorted(visits, key=lambda x: x["date"])
        visit_dates = [datetime.fromisoformat(v["date"]) for v in sorted_visits]
        
        # Calculate frequency
        if len(visit_dates) >= 2:
            time_span = (visit_dates[-1] - visit_dates[0]).days
            if time_span > 0:
                frequency = len(visit_dates) / (time_span / 30)  # visits per month
                if frequency >= 4:
                    frequency_pattern = "weekly"
                elif frequency >= 1:
                    frequency_pattern = "monthly"
                else:
                    frequency_pattern = "as_needed"
            else:
                frequency_pattern = "as_needed"
        else:
            frequency_pattern = "single_visit"
        
        return VisitPattern(
            provider_token=pattern_data["provider_token"],
            visit_count=len(visits),
            time_period="recent",
            visit_dates=visit_dates,
            purposes=[v.get("purpose", "unknown") for v in visits],
            frequency_pattern=frequency_pattern
        )
    
    def _extract_visit_purpose(self, content: str) -> str:
        """Extract the purpose of a healthcare visit from content."""
        purposes = []
        
        # Common visit purposes
        purpose_patterns = {
            "blood_pressure_check": ["blood pressure", "bp check", "hypertension"],
            "diabetes_management": ["diabetes", "blood sugar", "glucose", "insulin"],
            "routine_checkup": ["checkup", "physical", "routine", "annual"],
            "follow_up": ["follow up", "followup", "follow-up"],
            "medication_review": ["medication", "prescription", "refill"]
        }
        
        for purpose, keywords in purpose_patterns.items():
            if any(keyword in content.lower() for keyword in keywords):
                purposes.append(purpose.replace("_", " "))
        
        return ", ".join(purposes) if purposes else "general visit"
    
    def _get_equipment_capabilities(self, equipment_type: str) -> List[str]:
        """Get capabilities for different equipment types."""
        capabilities_map = {
            "blood_pressure_cuff": ["systolic_pressure", "diastolic_pressure", "pulse_rate"],
            "glucose_meter": ["blood_glucose", "trend_tracking"],
            "thermometer": ["body_temperature", "fever_detection"],
            "scale": ["body_weight", "weight_tracking"]
        }
        
        return capabilities_map.get(equipment_type, [])


def main():
    """Test the Personal Data Intelligence Tracker."""
    tracker = PersonalDataIntelligenceTracker()
    print("Personal Data Intelligence Tracker initialized")


if __name__ == "__main__":
    main() 