"""
Works With Agents — Python SDK
Reference implementations for all Agent OSI Model protocols.
Zero dependencies beyond stdlib. Copy-pasteable. CC BY 4.0.
"""
__version__ = "0.1.0"

from .trust_score import TrustScoreClient
from .deployment import DeploymentManifest
from .sla import SLAMetrics
from .identity import AgentIdentity
from .compliance import ComplianceEngine
from .onboarding import OnboardingClient

__all__ = [
    "TrustScoreClient",
    "DeploymentManifest", 
    "SLAMetrics",
    "AgentIdentity",
    "ComplianceEngine",
    "OnboardingClient",
]
