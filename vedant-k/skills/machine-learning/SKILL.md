---
name: machine-learning
description: Best practices for machine learning engineering, empirical benchmarking, leakage prevention, and model evaluation.
---

# Machine Learning Engineering Guidelines

## Core Principles
1. **Zero Hallucination / Deterministic Grounding**: Numerical results, statistical metrics, and model evaluations must be computed strictly via deterministic ML/statistical libraries (scikit-learn, scipy, numpy, pandas). LLMs never invent or estimate metrics.
2. **Strict Data Leakage Prevention**:
   - Feature scalers and encoders must be fit solely on the training fold during cross-validation, never on test or out-of-fold data.
   - Temporal order must be preserved when time features are detected (TimeSeriesSplit / Walk-Forward).
   - Group structure must be respected when grouping identifiers exist (GroupKFold).
3. **Multi-Model Benchmarking**:
   - Never assume a single model architecture is superior.
   - Baseline models (Dummy, Logistic/Ridge) must always accompany complex learners (GBDT, Random Forest).
4. **Metric Alignment**:
   - Never optimize accuracy on imbalanced datasets. Use F1-macro, PR-AUC, ROC-AUC, or balanced accuracy.
   - Regression metrics must report RMSE, MAE, and R2 with clear residual distribution checks.
5. **No Dataset-Specific Logic**:
   - Code must operate on abstract schemas, column data types, and target properties without hardcoding column names.
