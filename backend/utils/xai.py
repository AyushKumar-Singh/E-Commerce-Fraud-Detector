"""
Explainable AI utilities - confidence scores and decision reasoning
"""

from typing import Dict, List, Any

def assemble_decision(
    score_model: float,
    threshold: float,
    rule_boost: float,
    rule_reasons: List[str]
) -> Dict[str, Any]:
    """
    Assemble final decision with transparency
    
    Args:
        score_model: Raw model score (0-1)
        threshold: Decision threshold
        rule_boost: Score boost from business rules
        rule_reasons: List of triggered rule explanations
    
    Returns:
        Decision dict with scores, reasons, and final verdict
    """
    # Calculate final score (capped at 1.0)
    final_score = min(1.0, max(0.0, score_model + rule_boost))
    
    # Make decision
    is_fraud = final_score >= threshold
    
    # Calculate confidence
    distance_from_threshold = abs(final_score - threshold)
    confidence = "high" if distance_from_threshold > 0.2 else "medium" if distance_from_threshold > 0.1 else "low"
    
    return {
        "decision": bool(is_fraud),
        "confidence": confidence,
        "score_model": round(float(score_model), 4),
        "score_rules": round(float(rule_boost), 4),
        "score_final": round(float(final_score), 4),
        "threshold": float(threshold),
        "reasons": rule_reasons,
        "model_contribution": round(float(score_model / final_score * 100 if final_score > 0 else 100), 1),
        "rules_contribution": round(float(rule_boost / final_score * 100 if final_score > 0 else 0), 1)
    }

def get_feature_importance(model, feature_names: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extract feature importance from trained model
    
    Args:
        model: Trained sklearn model with coef_ or feature_importances_
        feature_names: List of feature names
        top_n: Number of top features to return
    
    Returns:
        List of {feature, importance} dicts
    """
    try:
        # For linear models
        if hasattr(model, 'coef_'):
            importances = abs(model.coef_[0])
        # For tree models
        elif hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            return []
        
        # Sort by importance
        indices = importances.argsort()[::-1][:top_n]
        
        return [
            {
                "feature": feature_names[i],
                "importance": round(float(importances[i]), 4),
                "rank": rank + 1
            }
            for rank, i in enumerate(indices)
        ]
    except Exception:
        return []