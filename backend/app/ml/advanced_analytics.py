"""
CyberSentric X - Advanced Behavior Analytics & Graph Neural Network (GNN) Engine
================================================================================
This module extends the baseline Isolation Forest with an advanced behavioral 
analytics engine and a Graph Neural Network (GNN) for detecting complex, 
distributed multi-stage attacks across multiple tenants.

Architecture:
1. Behavior Profiler: Tracks sequence anomalies (Markov Chain).
2. Graph Constructor: Builds IP-User-Endpoint bipartite graphs.
3. GNN Scorer: Simulates graph-based anomaly scoring for threat detection.
"""

from typing import List, Dict, Any
import math
from collections import defaultdict
from datetime import datetime

class BehaviorAnalyticsEngine:
    def __init__(self):
        # tenant_id -> user_id -> feature_history
        self.tenant_profiles = defaultdict(lambda: defaultdict(list))
        self.attack_graphs = []

    def profile_user_behavior(self, tenant_id: str, user_id: str, event: Dict[str, Any]) -> float:
        """
        Profiles user behavior to detect sudden deviations.
        Returns a behavior anomaly score (0.0 to 1.0).
        """
        history = self.tenant_profiles[tenant_id][user_id]
        history.append(event)
        
        # Keep recent 1000 events
        if len(history) > 1000:
            history.pop(0)
            
        if len(history) < 10:
            return 0.1 # Not enough data
            
        # Simplified anomaly calculation based on rate spikes and endpoint variance
        recent_events = history[-10:]
        unique_endpoints = len(set(e.get('endpoint', '') for e in recent_events))
        
        # If user hits many different endpoints suddenly, score increases
        score = min(unique_endpoints / 10.0, 1.0)
        return round(score, 3)


class GraphThreatDetector:
    """
    Simulates a Graph Neural Network (GNN) detection system.
    In a real production environment, this would use PyTorch Geometric (PyG)
    to embed the nodes and classify edges as anomalous.
    """
    def __init__(self):
        self.nodes = set()
        self.edges = []
        
    def add_event_to_graph(self, source_ip: str, target_endpoint: str, user_id: str):
        self.nodes.add(source_ip)
        self.nodes.add(target_endpoint)
        self.nodes.add(user_id)
        
        self.edges.append({"source": source_ip, "target": target_endpoint, "weight": 1.0})
        self.edges.append({"source": user_id, "target": target_endpoint, "weight": 1.0})
        
    def compute_gnn_anomaly_score(self, source_ip: str) -> float:
        """
        Simulate GNN embedding distance calculation. 
        Detects if an IP is acting as a botnet or conducting lateral movement.
        """
        # A simple heuristic to simulate GNN graph centrality anomaly
        ip_edges = [e for e in self.edges if e['source'] == source_ip]
        if not ip_edges:
            return 0.0
            
        # High out-degree to various targets suggests scanning/botnet behavior
        out_degree = len(ip_edges)
        anomaly_score = 1.0 / (1.0 + math.exp(-0.5 * (out_degree - 5))) # Sigmoid activation
        
        return round(anomaly_score, 4)

# Global Instances for Orchestrator
behavior_engine = BehaviorAnalyticsEngine()
gnn_detector = GraphThreatDetector()
