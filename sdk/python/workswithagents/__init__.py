"""
Works With Agents — Python SDK
Reference implementations for all Agent OSI Model protocols.
Zero dependencies beyond stdlib. Copy-pasteable. CC BY 4.0.
"""
__version__ = "0.3.0"

from .trust_score import TrustScoreClient
from .deployment import DeploymentManifest
from .sla import SLAMetrics
from .identity import AgentIdentity
from .compliance import ComplianceEngine
from .onboarding import OnboardingClient
from .iacp import IACPClient
from .economics import EconomicsClient
from .reputation import ReputationClient
from .coordination import CoordinationClient
from .transaction import TransactionLedger
from .fleet_insurance import FleetInsurance

__all__ = [
    "TrustScoreClient",
    "DeploymentManifest",
    "SLAMetrics",
    "AgentIdentity",
    "ComplianceEngine",
    "OnboardingClient",
    "IACPClient",
    "EconomicsClient",
    "ReputationClient",
    "CoordinationClient",
    "TransactionLedger",
    "FleetInsurance",
]
