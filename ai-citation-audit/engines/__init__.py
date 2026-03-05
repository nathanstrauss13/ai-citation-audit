"""
AEO Intelligence Platform - Engines Module

Provides data processing engines for the platform.

Engines:
    - CollectionEngine: Runs queries across LLM platforms (sequential)
    - ParallelCollectionEngine: Runs queries across LLM platforms (parallel, default)
    - AnalysisEngine: Computes insights from collected data
    - DashboardEngine: Legacy dashboard generator
    - DashboardEngineV2: Production-quality dashboard generator (default)
"""

from .collection_engine import CollectionEngine
from .parallel_collection import ParallelCollectionEngine
from .analysis_engine import AnalysisEngine
from .dashboard_engine import DashboardEngine
from .dashboard_v2 import DashboardEngineV2

__all__ = [
    "CollectionEngine",
    "ParallelCollectionEngine",
    "AnalysisEngine",
    "DashboardEngine",
    "DashboardEngineV2",
]
