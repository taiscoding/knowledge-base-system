#!/usr/bin/env python3
"""
Privacy Certification Framework for Knowledge Base System.

This module provides privacy certification and compliance capabilities including:
1. Compliance checking against standards (GDPR, CCPA, HIPAA)
2. Privacy impact assessment tools
3. Certification report generation
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class ComplianceStandard(str, Enum):
    """Supported compliance standards."""
    GDPR = "gdpr"           # General Data Protection Regulation
    CCPA = "ccpa"           # California Consumer Privacy Act
    HIPAA = "hipaa"         # Health Insurance Portability and Accountability Act
    SOC2 = "soc2"           # Service Organization Control 2
    ISO27001 = "iso27001"   # ISO/IEC 27001
    CUSTOM = "custom"       # Custom compliance framework


class ComplianceLevel(str, Enum):
    """Compliance assessment levels."""
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    MOSTLY_COMPLIANT = "mostly_compliant"
    FULLY_COMPLIANT = "fully_compliant"


class RiskLevel(str, Enum):
    """Risk level assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRequirement:
    """A specific compliance requirement."""
    requirement_id: str
    title: str
    description: str
    standard: ComplianceStandard
    category: str
    mandatory: bool = True
    assessment_criteria: List[str] = field(default_factory=list)
    evidence_requirements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert requirement to dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "standard": self.standard.value,
            "category": self.category,
            "mandatory": self.mandatory,
            "assessment_criteria": self.assessment_criteria,
            "evidence_requirements": self.evidence_requirements
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceRequirement':
        """Create requirement from dictionary."""
        return cls(
            requirement_id=data["requirement_id"],
            title=data["title"],
            description=data["description"],
            standard=ComplianceStandard(data["standard"]),
            category=data["category"],
            mandatory=data.get("mandatory", True),
            assessment_criteria=data.get("assessment_criteria", []),
            evidence_requirements=data.get("evidence_requirements", [])
        )


@dataclass
class ComplianceAssessment:
    """Assessment result for a compliance requirement."""
    requirement_id: str
    compliance_level: ComplianceLevel
    evidence_provided: List[str] = field(default_factory=list)
    gaps_identified: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    assessed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assessor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "compliance_level": self.compliance_level.value,
            "evidence_provided": self.evidence_provided,
            "gaps_identified": self.gaps_identified,
            "recommendations": self.recommendations,
            "risk_level": self.risk_level.value,
            "assessed_at": self.assessed_at,
            "assessor": self.assessor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceAssessment':
        """Create assessment from dictionary."""
        return cls(
            requirement_id=data["requirement_id"],
            compliance_level=ComplianceLevel(data["compliance_level"]),
            evidence_provided=data.get("evidence_provided", []),
            gaps_identified=data.get("gaps_identified", []),
            recommendations=data.get("recommendations", []),
            risk_level=RiskLevel(data.get("risk_level", "low")),
            assessed_at=data.get("assessed_at", datetime.now().isoformat()),
            assessor=data.get("assessor")
        )


@dataclass
class PrivacyImpactAssessment:
    """Privacy Impact Assessment (PIA) results."""
    pia_id: str
    title: str
    scope: str
    data_categories: List[str]
    processing_purposes: List[str]
    legal_basis: List[str]
    risk_assessment: Dict[str, Any]
    mitigation_measures: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "draft"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PIA to dictionary."""
        return {
            "pia_id": self.pia_id,
            "title": self.title,
            "scope": self.scope,
            "data_categories": self.data_categories,
            "processing_purposes": self.processing_purposes,
            "legal_basis": self.legal_basis,
            "risk_assessment": self.risk_assessment,
            "mitigation_measures": self.mitigation_measures,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacyImpactAssessment':
        """Create PIA from dictionary."""
        return cls(
            pia_id=data["pia_id"],
            title=data["title"],
            scope=data["scope"],
            data_categories=data["data_categories"],
            processing_purposes=data["processing_purposes"],
            legal_basis=data["legal_basis"],
            risk_assessment=data["risk_assessment"],
            mitigation_measures=data["mitigation_measures"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            status=data.get("status", "draft")
        )


class ComplianceChecker:
    """
    Checks compliance against various privacy standards.
    
    This class provides:
    1. Standard-based compliance verification
    2. Gap analysis and recommendations
    3. Evidence collection and validation
    """
    
    def __init__(self, requirements_dir: str = None):
        """
        Initialize the compliance checker.
        
        Args:
            requirements_dir: Directory containing compliance requirements
        """
        # Set up requirements directory
        if requirements_dir:
            self.requirements_dir = Path(requirements_dir)
        else:
            self.requirements_dir = Path(__file__).parent / "compliance_requirements"
            
        self.requirements_dir.mkdir(parents=True, exist_ok=True)
        
        # Load compliance requirements
        self.requirements: Dict[str, Dict[str, ComplianceRequirement]] = {}
        self._load_requirements()
    
    def _load_requirements(self) -> None:
        """Load compliance requirements from files."""
        # Initialize with built-in requirements
        self._create_default_requirements()
        
        # Load additional requirements from files
        for req_file in self.requirements_dir.glob("*.json"):
            try:
                with open(req_file, 'r') as f:
                    requirements_data = json.load(f)
                    
                for req_data in requirements_data:
                    requirement = ComplianceRequirement.from_dict(req_data)
                    standard = requirement.standard.value
                    
                    if standard not in self.requirements:
                        self.requirements[standard] = {}
                        
                    self.requirements[standard][requirement.requirement_id] = requirement
                    
            except Exception as e:
                logger.error(f"Error loading requirements from {req_file}: {e}")
    
    def _create_default_requirements(self) -> None:
        """Create default compliance requirements for supported standards."""
        # GDPR Requirements
        gdpr_requirements = [
            ComplianceRequirement(
                requirement_id="gdpr_consent",
                title="Lawful Basis for Processing",
                description="Ensure lawful basis exists for all personal data processing",
                standard=ComplianceStandard.GDPR,
                category="legal_basis",
                assessment_criteria=[
                    "Legal basis documented for each processing activity",
                    "Consent mechanisms implemented where required",
                    "Data subjects can withdraw consent"
                ],
                evidence_requirements=[
                    "Privacy policy documentation",
                    "Consent management system evidence",
                    "Processing activity records"
                ]
            ),
            ComplianceRequirement(
                requirement_id="gdpr_data_minimization",
                title="Data Minimization",
                description="Collect and process only necessary personal data",
                standard=ComplianceStandard.GDPR,
                category="data_protection",
                assessment_criteria=[
                    "Data collection limited to stated purposes",
                    "Regular review of data retention periods",
                    "Automated deletion of unnecessary data"
                ],
                evidence_requirements=[
                    "Data retention policies",
                    "Automated deletion logs",
                    "Data mapping documentation"
                ]
            ),
            ComplianceRequirement(
                requirement_id="gdpr_security",
                title="Security of Processing",
                description="Implement appropriate technical and organizational measures",
                standard=ComplianceStandard.GDPR,
                category="security",
                assessment_criteria=[
                    "Encryption in transit and at rest",
                    "Access controls and authentication",
                    "Regular security assessments"
                ],
                evidence_requirements=[
                    "Encryption implementation evidence",
                    "Access control documentation",
                    "Security audit reports"
                ]
            ),
            ComplianceRequirement(
                requirement_id="gdpr_rights",
                title="Data Subject Rights",
                description="Enable data subjects to exercise their rights",
                standard=ComplianceStandard.GDPR,
                category="rights",
                assessment_criteria=[
                    "Access request mechanisms available",
                    "Data portability features implemented",
                    "Deletion capabilities provided"
                ],
                evidence_requirements=[
                    "Rights exercise procedures",
                    "Data portability tools",
                    "Deletion capability evidence"
                ]
            )
        ]
        
        # CCPA Requirements
        ccpa_requirements = [
            ComplianceRequirement(
                requirement_id="ccpa_disclosure",
                title="Consumer Disclosure",
                description="Provide clear disclosure of data collection and use",
                standard=ComplianceStandard.CCPA,
                category="disclosure",
                assessment_criteria=[
                    "Privacy policy clearly describes data practices",
                    "Collection notice provided at point of collection",
                    "Categories of personal information disclosed"
                ],
                evidence_requirements=[
                    "Privacy policy documentation",
                    "Collection notices",
                    "Data category documentation"
                ]
            ),
            ComplianceRequirement(
                requirement_id="ccpa_opt_out",
                title="Right to Opt-Out",
                description="Provide consumers ability to opt-out of sale",
                standard=ComplianceStandard.CCPA,
                category="consumer_rights",
                assessment_criteria=[
                    "Clear opt-out mechanism available",
                    "Do Not Sell My Personal Information link present",
                    "Opt-out requests processed within required timeframe"
                ],
                evidence_requirements=[
                    "Opt-out mechanism documentation",
                    "Response time metrics",
                    "Opt-out processing procedures"
                ]
            )
        ]
        
        # HIPAA Requirements (simplified for illustration)
        hipaa_requirements = [
            ComplianceRequirement(
                requirement_id="hipaa_safeguards",
                title="Administrative Safeguards",
                description="Implement administrative safeguards for PHI",
                standard=ComplianceStandard.HIPAA,
                category="safeguards",
                assessment_criteria=[
                    "Security officer designated",
                    "Workforce training completed",
                    "Access management procedures in place"
                ],
                evidence_requirements=[
                    "Security officer documentation",
                    "Training records",
                    "Access management policies"
                ]
            )
        ]
        
        # Organize requirements by standard
        self.requirements = {
            ComplianceStandard.GDPR.value: {req.requirement_id: req for req in gdpr_requirements},
            ComplianceStandard.CCPA.value: {req.requirement_id: req for req in ccpa_requirements},
            ComplianceStandard.HIPAA.value: {req.requirement_id: req for req in hipaa_requirements}
        }
    
    def assess_compliance(self, 
                         standard: ComplianceStandard,
                         evidence: Dict[str, Any] = None) -> Dict[str, ComplianceAssessment]:
        """
        Assess compliance against a specific standard.
        
        Args:
            standard: Compliance standard to assess against
            evidence: Evidence provided for assessment
            
        Returns:
            Dictionary of requirement ID to assessment results
        """
        evidence = evidence or {}
        assessments = {}
        
        # Get requirements for the standard
        requirements = self.requirements.get(standard.value, {})
        
        for req_id, requirement in requirements.items():
            assessment = self._assess_requirement(requirement, evidence)
            assessments[req_id] = assessment
            
        return assessments
    
    def _assess_requirement(self, 
                          requirement: ComplianceRequirement,
                          evidence: Dict[str, Any]) -> ComplianceAssessment:
        """
        Assess compliance for a specific requirement.
        
        Args:
            requirement: Compliance requirement to assess
            evidence: Available evidence
            
        Returns:
            Compliance assessment result
        """
        req_id = requirement.requirement_id
        evidence_provided = []
        gaps_identified = []
        recommendations = []
        
        # Check each evidence requirement
        evidence_score = 0
        for evidence_req in requirement.evidence_requirements:
            evidence_key = evidence_req.lower().replace(" ", "_")
            if evidence_key in evidence and evidence[evidence_key]:
                evidence_provided.append(evidence_req)
                evidence_score += 1
            else:
                gaps_identified.append(f"Missing evidence: {evidence_req}")
        
        # Calculate compliance level based on evidence
        total_evidence_reqs = len(requirement.evidence_requirements)
        if total_evidence_reqs == 0:
            compliance_ratio = 1.0  # No evidence requirements
        else:
            compliance_ratio = evidence_score / total_evidence_reqs
        
        # Determine compliance level
        if compliance_ratio >= 1.0:
            compliance_level = ComplianceLevel.FULLY_COMPLIANT
            risk_level = RiskLevel.LOW
        elif compliance_ratio >= 0.8:
            compliance_level = ComplianceLevel.MOSTLY_COMPLIANT
            risk_level = RiskLevel.LOW
        elif compliance_ratio >= 0.5:
            compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
            risk_level = RiskLevel.MEDIUM
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
            risk_level = RiskLevel.HIGH if requirement.mandatory else RiskLevel.MEDIUM
        
        # Generate recommendations based on gaps
        if gaps_identified:
            recommendations.append(f"Address {len(gaps_identified)} evidence gaps")
            for gap in gaps_identified[:3]:  # Top 3 gaps
                recommendations.append(f"Provide: {gap}")
        
        return ComplianceAssessment(
            requirement_id=req_id,
            compliance_level=compliance_level,
            evidence_provided=evidence_provided,
            gaps_identified=gaps_identified,
            recommendations=recommendations,
            risk_level=risk_level
        )
    
    def generate_gap_analysis(self, 
                            assessments: Dict[str, ComplianceAssessment]) -> Dict[str, Any]:
        """
        Generate gap analysis from compliance assessments.
        
        Args:
            assessments: Compliance assessment results
            
        Returns:
            Gap analysis report
        """
        # Aggregate results
        total_requirements = len(assessments)
        fully_compliant = sum(1 for a in assessments.values() 
                            if a.compliance_level == ComplianceLevel.FULLY_COMPLIANT)
        mostly_compliant = sum(1 for a in assessments.values() 
                             if a.compliance_level == ComplianceLevel.MOSTLY_COMPLIANT)
        partially_compliant = sum(1 for a in assessments.values() 
                                if a.compliance_level == ComplianceLevel.PARTIALLY_COMPLIANT)
        non_compliant = sum(1 for a in assessments.values() 
                          if a.compliance_level == ComplianceLevel.NON_COMPLIANT)
        
        # Calculate overall compliance score
        compliance_score = (
            (fully_compliant * 1.0) +
            (mostly_compliant * 0.8) +
            (partially_compliant * 0.5) +
            (non_compliant * 0.0)
        ) / total_requirements if total_requirements > 0 else 0
        
        # Identify high-risk gaps
        high_risk_gaps = [
            assessment for assessment in assessments.values()
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
        
        # Aggregate all recommendations
        all_recommendations = []
        for assessment in assessments.values():
            all_recommendations.extend(assessment.recommendations)
        
        # Count recommendation frequency
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        # Get top recommendations
        top_recommendations = sorted(
            recommendation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "summary": {
                "total_requirements": total_requirements,
                "compliance_score": compliance_score,
                "compliance_percentage": compliance_score * 100,
                "fully_compliant": fully_compliant,
                "mostly_compliant": mostly_compliant,
                "partially_compliant": partially_compliant,
                "non_compliant": non_compliant
            },
            "risk_analysis": {
                "high_risk_gaps": len(high_risk_gaps),
                "high_risk_requirements": [gap.requirement_id for gap in high_risk_gaps]
            },
            "top_recommendations": [rec for rec, count in top_recommendations],
            "generated_at": datetime.now().isoformat()
        }


class PrivacyImpactAssessmentTool:
    """
    Tool for conducting Privacy Impact Assessments.
    
    This class provides:
    1. Structured PIA workflow
    2. Risk scoring and assessment
    3. Mitigation recommendation generation
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the PIA tool.
        
        Args:
            storage_dir: Directory for storing PIA results
        """
        # Set up storage location
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".kb_privacy" / "pia"
            
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing PIAs
        self.pias: Dict[str, PrivacyImpactAssessment] = {}
        self._load_pias()
    
    def _load_pias(self) -> None:
        """Load existing PIAs from storage."""
        try:
            for pia_file in self.storage_dir.glob("pia_*.json"):
                try:
                    with open(pia_file, 'r') as f:
                        pia_data = json.load(f)
                        pia = PrivacyImpactAssessment.from_dict(pia_data)
                        self.pias[pia.pia_id] = pia
                        logger.debug(f"Loaded PIA: {pia.pia_id}")
                except Exception as e:
                    logger.error(f"Error loading PIA from {pia_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading PIAs: {e}")
    
    def create_pia(self, 
                  title: str,
                  scope: str,
                  data_categories: List[str],
                  processing_purposes: List[str],
                  legal_basis: List[str]) -> PrivacyImpactAssessment:
        """
        Create a new Privacy Impact Assessment.
        
        Args:
            title: PIA title
            scope: Scope of the assessment
            data_categories: Categories of data being processed
            processing_purposes: Purposes for processing
            legal_basis: Legal basis for processing
            
        Returns:
            New PIA instance
        """
        import uuid
        
        # Generate unique PIA ID
        pia_id = f"pia-{uuid.uuid4().hex[:8]}"
        
        # Conduct initial risk assessment
        risk_assessment = self._conduct_risk_assessment(
            data_categories, processing_purposes
        )
        
        # Generate initial mitigation measures
        mitigation_measures = self._generate_mitigation_measures(risk_assessment)
        
        # Create PIA
        pia = PrivacyImpactAssessment(
            pia_id=pia_id,
            title=title,
            scope=scope,
            data_categories=data_categories,
            processing_purposes=processing_purposes,
            legal_basis=legal_basis,
            risk_assessment=risk_assessment,
            mitigation_measures=mitigation_measures
        )
        
        # Store PIA
        self.pias[pia_id] = pia
        self._save_pia(pia)
        
        return pia
    
    def _save_pia(self, pia: PrivacyImpactAssessment) -> None:
        """
        Save PIA to storage.
        
        Args:
            pia: PIA to save
        """
        pia_path = self.storage_dir / f"pia_{pia.pia_id}.json"
        
        try:
            with open(pia_path, 'w') as f:
                json.dump(pia.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving PIA {pia.pia_id}: {e}")
    
    def _conduct_risk_assessment(self, 
                               data_categories: List[str],
                               processing_purposes: List[str]) -> Dict[str, Any]:
        """
        Conduct risk assessment for the PIA.
        
        Args:
            data_categories: Categories of data
            processing_purposes: Processing purposes
            
        Returns:
            Risk assessment results
        """
        # Define risk factors and their weights
        risk_factors = {
            "sensitive_data": {
                "weight": 0.3,
                "score": self._assess_sensitive_data_risk(data_categories)
            },
            "processing_scope": {
                "weight": 0.2,
                "score": self._assess_processing_scope_risk(processing_purposes)
            },
            "data_subject_impact": {
                "weight": 0.25,
                "score": self._assess_data_subject_impact(data_categories, processing_purposes)
            },
            "technical_complexity": {
                "weight": 0.15,
                "score": self._assess_technical_complexity(processing_purposes)
            },
            "third_party_involvement": {
                "weight": 0.1,
                "score": self._assess_third_party_risk(processing_purposes)
            }
        }
        
        # Calculate overall risk score
        overall_risk = sum(
            factor["weight"] * factor["score"]
            for factor in risk_factors.values()
        )
        
        # Determine risk level
        if overall_risk >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif overall_risk >= 0.6:
            risk_level = RiskLevel.HIGH
        elif overall_risk >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level.value,
            "risk_factors": risk_factors,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _assess_sensitive_data_risk(self, data_categories: List[str]) -> float:
        """Assess risk based on sensitivity of data categories."""
        sensitive_categories = [
            "health", "medical", "biometric", "genetic",
            "financial", "payment", "credit",
            "ethnic", "racial", "religious", "political",
            "sexual", "orientation", "children"
        ]
        
        sensitive_count = sum(
            1 for category in data_categories
            if any(sensitive in category.lower() for sensitive in sensitive_categories)
        )
        
        return min(sensitive_count / len(data_categories) if data_categories else 0, 1.0)
    
    def _assess_processing_scope_risk(self, processing_purposes: List[str]) -> float:
        """Assess risk based on scope of processing."""
        high_risk_purposes = [
            "profiling", "automated decision", "tracking",
            "monitoring", "surveillance", "behavioral analysis"
        ]
        
        high_risk_count = sum(
            1 for purpose in processing_purposes
            if any(risk_term in purpose.lower() for risk_term in high_risk_purposes)
        )
        
        return min(high_risk_count / len(processing_purposes) if processing_purposes else 0, 1.0)
    
    def _assess_data_subject_impact(self, 
                                  data_categories: List[str],
                                  processing_purposes: List[str]) -> float:
        """Assess potential impact on data subjects."""
        # Simplified impact assessment
        # In practice, this would be more sophisticated
        impact_score = 0.0
        
        # Higher impact for sensitive data
        if any("health" in cat.lower() or "financial" in cat.lower() 
               for cat in data_categories):
            impact_score += 0.4
        
        # Higher impact for automated decision making
        if any("automated" in purpose.lower() or "decision" in purpose.lower()
               for purpose in processing_purposes):
            impact_score += 0.3
        
        # Base impact for any personal data processing
        impact_score += 0.2
        
        return min(impact_score, 1.0)
    
    def _assess_technical_complexity(self, processing_purposes: List[str]) -> float:
        """Assess technical complexity risk."""
        complex_purposes = [
            "machine learning", "ai", "artificial intelligence",
            "algorithm", "automated", "real-time"
        ]
        
        complexity_count = sum(
            1 for purpose in processing_purposes
            if any(complex_term in purpose.lower() for complex_term in complex_purposes)
        )
        
        return min(complexity_count / max(len(processing_purposes), 1), 1.0)
    
    def _assess_third_party_risk(self, processing_purposes: List[str]) -> float:
        """Assess third-party involvement risk."""
        third_party_indicators = [
            "sharing", "transfer", "third party", "external",
            "cloud", "service provider", "vendor"
        ]
        
        third_party_count = sum(
            1 for purpose in processing_purposes
            if any(indicator in purpose.lower() for indicator in third_party_indicators)
        )
        
        return min(third_party_count / max(len(processing_purposes), 1), 1.0)
    
    def _generate_mitigation_measures(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """
        Generate mitigation measures based on risk assessment.
        
        Args:
            risk_assessment: Risk assessment results
            
        Returns:
            List of recommended mitigation measures
        """
        measures = []
        risk_level = RiskLevel(risk_assessment["risk_level"])
        risk_factors = risk_assessment["risk_factors"]
        
        # General measures for all risk levels
        measures.extend([
            "Implement data minimization principles",
            "Establish clear data retention policies",
            "Provide comprehensive privacy notices"
        ])
        
        # Measures based on specific risk factors
        if risk_factors["sensitive_data"]["score"] > 0.5:
            measures.extend([
                "Implement enhanced encryption for sensitive data",
                "Establish strict access controls",
                "Consider pseudonymization techniques"
            ])
        
        if risk_factors["processing_scope"]["score"] > 0.5:
            measures.extend([
                "Implement human oversight for automated decisions",
                "Provide opt-out mechanisms",
                "Establish regular algorithmic audits"
            ])
        
        if risk_factors["data_subject_impact"]["score"] > 0.7:
            measures.extend([
                "Implement impact monitoring systems",
                "Establish data subject complaint mechanisms",
                "Provide enhanced transparency measures"
            ])
        
        # Risk level specific measures
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            measures.extend([
                "Conduct regular privacy audits",
                "Implement privacy by design principles",
                "Establish incident response procedures",
                "Consider appointment of Data Protection Officer"
            ])
        
        if risk_level == RiskLevel.CRITICAL:
            measures.extend([
                "Seek regulatory consultation",
                "Implement continuous monitoring",
                "Establish emergency response procedures"
            ])
        
        return list(set(measures))  # Remove duplicates
    
    def update_pia(self, 
                  pia_id: str,
                  updates: Dict[str, Any]) -> Optional[PrivacyImpactAssessment]:
        """
        Update an existing PIA.
        
        Args:
            pia_id: PIA ID to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated PIA or None if not found
        """
        pia = self.pias.get(pia_id)
        if not pia:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(pia, key):
                setattr(pia, key, value)
        
        # Update timestamp
        pia.updated_at = datetime.now().isoformat()
        
        # Re-assess risk if data or processing changed
        if any(key in updates for key in ["data_categories", "processing_purposes"]):
            pia.risk_assessment = self._conduct_risk_assessment(
                pia.data_categories, pia.processing_purposes
            )
            pia.mitigation_measures = self._generate_mitigation_measures(pia.risk_assessment)
        
        # Save updated PIA
        self._save_pia(pia)
        
        return pia


class CertificationReporter:
    """
    Generates certification reports and documentation.
    
    This class provides:
    1. Comprehensive compliance reports
    2. Certification documentation
    3. Continuous compliance monitoring
    """
    
    def __init__(self, 
                 compliance_checker: ComplianceChecker,
                 pia_tool: PrivacyImpactAssessmentTool):
        """
        Initialize the certification reporter.
        
        Args:
            compliance_checker: Compliance checker instance
            pia_tool: PIA tool instance
        """
        self.compliance_checker = compliance_checker
        self.pia_tool = pia_tool
    
    def generate_certification_report(self,
                                    standard: ComplianceStandard,
                                    evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive certification report.
        
        Args:
            standard: Compliance standard to report on
            evidence: Evidence for compliance assessment
            
        Returns:
            Certification report dictionary
        """
        evidence = evidence or {}
        
        # Assess compliance
        assessments = self.compliance_checker.assess_compliance(standard, evidence)
        
        # Generate gap analysis
        gap_analysis = self.compliance_checker.generate_gap_analysis(assessments)
        
        # Get relevant PIAs
        relevant_pias = [
            pia.to_dict() for pia in self.pia_tool.pias.values()
            if pia.status != "draft"
        ]
        
        # Create certification report
        report = {
            "report_type": "certification_report",
            "standard": standard.value,
            "generated_at": datetime.now().isoformat(),
            "compliance_summary": gap_analysis["summary"],
            "detailed_assessments": {
                req_id: assessment.to_dict()
                for req_id, assessment in assessments.items()
            },
            "gap_analysis": gap_analysis,
            "privacy_impact_assessments": relevant_pias,
            "certification_status": self._determine_certification_status(gap_analysis),
            "recommendations": gap_analysis["top_recommendations"],
            "next_review_date": (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        return report
    
    def _determine_certification_status(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine certification status based on gap analysis.
        
        Args:
            gap_analysis: Gap analysis results
            
        Returns:
            Certification status information
        """
        compliance_score = gap_analysis["summary"]["compliance_score"]
        high_risk_gaps = gap_analysis["risk_analysis"]["high_risk_gaps"]
        
        # Determine certification level
        if compliance_score >= 0.95 and high_risk_gaps == 0:
            status = "certified"
            level = "full_compliance"
        elif compliance_score >= 0.85 and high_risk_gaps <= 1:
            status = "conditionally_certified"
            level = "substantial_compliance"
        elif compliance_score >= 0.70:
            status = "improvement_required"
            level = "partial_compliance"
        else:
            status = "non_certified"
            level = "non_compliance"
        
        return {
            "status": status,
            "level": level,
            "compliance_score": compliance_score,
            "compliance_percentage": compliance_score * 100,
            "high_risk_gaps": high_risk_gaps,
            "determination_date": datetime.now().isoformat()
        }
    
    def generate_continuous_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate a continuous monitoring report.
        
        Returns:
            Monitoring report dictionary
        """
        # Get all PIAs
        all_pias = list(self.pia_tool.pias.values())
        
        # Analyze PIA status
        draft_pias = [pia for pia in all_pias if pia.status == "draft"]
        completed_pias = [pia for pia in all_pias if pia.status == "completed"]
        
        # Analyze risk levels
        high_risk_pias = [
            pia for pia in completed_pias
            if pia.risk_assessment.get("risk_level") in ["high", "critical"]
        ]
        
        # Check for overdue reviews (PIAs older than 1 year)
        one_year_ago = datetime.now() - timedelta(days=365)
        overdue_pias = [
            pia for pia in completed_pias
            if datetime.fromisoformat(pia.updated_at) < one_year_ago
        ]
        
        return {
            "report_type": "continuous_monitoring",
            "generated_at": datetime.now().isoformat(),
            "pia_summary": {
                "total_pias": len(all_pias),
                "draft_pias": len(draft_pias),
                "completed_pias": len(completed_pias),
                "high_risk_pias": len(high_risk_pias),
                "overdue_reviews": len(overdue_pias)
            },
            "alerts": self._generate_monitoring_alerts(
                draft_pias, high_risk_pias, overdue_pias
            ),
            "recommendations": self._generate_monitoring_recommendations(
                draft_pias, high_risk_pias, overdue_pias
            )
        }
    
    def _generate_monitoring_alerts(self,
                                  draft_pias: List[PrivacyImpactAssessment],
                                  high_risk_pias: List[PrivacyImpactAssessment],
                                  overdue_pias: List[PrivacyImpactAssessment]) -> List[Dict[str, Any]]:
        """Generate monitoring alerts."""
        alerts = []
        
        if len(draft_pias) > 5:
            alerts.append({
                "level": "warning",
                "type": "incomplete_pias",
                "message": f"{len(draft_pias)} PIAs are still in draft status",
                "action_required": "Complete pending PIA assessments"
            })
        
        if high_risk_pias:
            alerts.append({
                "level": "high",
                "type": "high_risk_processing",
                "message": f"{len(high_risk_pias)} high-risk processing activities identified",
                "action_required": "Review and enhance mitigation measures"
            })
        
        if overdue_pias:
            alerts.append({
                "level": "medium",
                "type": "overdue_reviews",
                "message": f"{len(overdue_pias)} PIAs require review",
                "action_required": "Conduct overdue PIA reviews"
            })
        
        return alerts
    
    def _generate_monitoring_recommendations(self,
                                          draft_pias: List[PrivacyImpactAssessment],
                                          high_risk_pias: List[PrivacyImpactAssessment],
                                          overdue_pias: List[PrivacyImpactAssessment]) -> List[str]:
        """Generate monitoring recommendations."""
        recommendations = []
        
        if draft_pias:
            recommendations.append("Establish deadlines for completing draft PIAs")
        
        if high_risk_pias:
            recommendations.append("Implement enhanced monitoring for high-risk activities")
            recommendations.append("Consider additional safeguards for high-risk processing")
        
        if overdue_pias:
            recommendations.append("Establish regular PIA review schedule")
            recommendations.append("Set up automated reminders for PIA reviews")
        
        recommendations.extend([
            "Maintain documentation of all privacy decisions",
            "Regular training on privacy compliance requirements",
            "Establish privacy governance committee"
        ])
        
        return recommendations
