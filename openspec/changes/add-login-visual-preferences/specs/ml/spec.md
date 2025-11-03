# ML Specification - Delta

## ADDED Requirements

### Requirement: 80-Feature Processing
The system SHALL expand feature processing from 45 to 80 features including profile and visual preferences.

#### Scenario: Feature Processing v4 for Authenticated User
- **WHEN** UserContext contains user_id (authenticated)
- **THEN** FeatureProcessor SHALL extract 45 automatic features from ephemeral context
- **AND** extract 15 profile features from user model
- **AND** extract 20 visual preference features from user model
- **AND** return numpy array with 80 features in consistent order
- **AND** handle missing values with defaults (for partial profiles)

#### Scenario: Profile Features Extraction
- **WHEN** processing profile data
- **THEN** system SHALL create feature es_empresa: bool from tipo_cliente
- **AND** create rango_edad: int (18-24, 25-34, 35-44, 45-54, 55-64, 65+) from fecha_nacimiento
- **AND** create region_norte/centro/sur: bool from region (one-hot encoding)
- **AND** create interesa_lujo/comercial/pesado: bool from interes_principal
- **AND** create presupuesto_alto/medio/bajo: bool from presupuesto ranges
- **AND** create tiene_trade_in: bool from tiene_vehiculo_actual
- **AND** create edad_exacta: int from fecha_nacimiento
- **AND** create tamano_flota_normalizado: float (0-1) from tamano_flota
- **AND** create uso_es_comercial: bool from uso_previsto (transporte/minería/construcción/agrícola)

#### Scenario: Visual Preference Features Extraction
- **WHEN** processing visual preferences
- **THEN** system SHALL create esquema_colores_encoded: int (0-6) from esquema_colores
- **AND** create color_favorito_encoded: int (0-8) from color_favorito
- **AND** create prefiere_colores_oscuros: bool (oscuro_premium, alto_contraste)
- **AND** create prefiere_colores_premium: bool (dorado, plateado)
- **AND** create densidad_ui_normalizada: float (0-1) from densidad_informacion
- **AND** create prefiere_minimalismo: bool (densidad < 0.3)
- **AND** create es_usuario_experto_ui: bool (densidad > 0.7)
- **AND** create prefiere_serif: bool from estilo_tipografia
- **AND** create sin_animaciones: bool (nivel_animaciones == "ninguna")
- **AND** create prioriza_consumo: bool from prioridades_info.consumo rank
- **AND** create prioriza_tecnologia: bool from prioridades_info.tecnologia rank
- **AND** create prioriza_precio: bool from prioridades_info.precio rank
- **AND** create prioriza_seguridad: bool from prioridades_info.seguridad rank

#### Scenario: Anonymous User Feature Processing
- **WHEN** UserContext contains user_id=None (anonymous)
- **THEN** FeatureProcessor SHALL extract 45 automatic features
- **AND** set profile features to default values (es_empresa=False, rango_edad=35-44, region_centro=True, etc.)
- **AND** set visual preference features to defaults (esquema_automatico, color_azul, densidad_comoda, etc.)
- **AND** return 80-feature array with defaults for missing data
- **AND** prediction SHALL still work with reduced accuracy

### Requirement: 80-Feature Dataset Generation
The system SHALL generate synthetic dataset with 80 features for model training.

#### Scenario: Synthetic Data Generation
- **WHEN** generate_80_features_dataset.py script runs
- **THEN** system SHALL generate 10,000 samples
- **AND** distribute samples across customer segments: 40% persona_lujo, 30% empresa_comercial, 30% empresa_pesado
- **AND** create realistic correlations:
  - empresa → large fleet → high budget → interest heavy trucks
  - persona + young (25-34) → interest SUV/electric → budget medium
  - region_norte → interest mining trucks (Freightliner) → uso minería
  - alto presupuesto → prefiere_colores_premium (dorado/plateado)
- **AND** add realistic noise (10% random variance)
- **AND** save to CSV with column headers matching feature names

#### Scenario: Feature Correlation Validation
- **WHEN** dataset generated
- **THEN** system SHALL validate correlations make business sense
- **AND** ensure es_empresa correlates with tamano_flota > 0
- **AND** ensure persona correlates with edad_exacta > 0
- **AND** ensure region_norte correlates with interesa_pesado (mining)
- **AND** ensure presupuesto_alto correlates with interesa_lujo
- **AND** log correlation matrix to validate.log

### Requirement: XGBoost Model Retraining with 80 Features
The system SHALL train classifier and regressor with expanded 80-feature dataset.

#### Scenario: Classifier Training
- **WHEN** train_xgboost_80_features.py script runs for classifier
- **THEN** system SHALL load 80-feature dataset (10,000 samples)
- **AND** split 80% train, 20% test (stratified by tipo_cliente)
- **AND** train XGBoostClassifier with parameters:
  - n_estimators=200
  - max_depth=8
  - learning_rate=0.05
  - reg_lambda=1.0 (L2 regularization)
  - scale_pos_weight for class imbalance
- **AND** perform 5-fold cross-validation
- **AND** achieve F1-Score ≥ 0.90 on test set
- **AND** save model to xgboost_classifier_80f_v4.json

#### Scenario: Regressor Training
- **WHEN** train_xgboost_80_features.py script runs for regressor
- **THEN** system SHALL load 80-feature dataset
- **AND** split 80% train, 20% test
- **AND** train XGBoostRegressor with parameters:
  - n_estimators=200
  - max_depth=8
  - learning_rate=0.05
  - reg_lambda=1.0
- **AND** perform 5-fold cross-validation
- **AND** achieve R² ≥ 0.80 on test set
- **AND** save model to xgboost_regressor_80f_v4.json

#### Scenario: Feature Importance Analysis
- **WHEN** model training completes
- **THEN** system SHALL extract feature importance scores
- **AND** rank features by importance
- **AND** identify top 60 features contributing 95% of importance
- **AND** save feature importance to feature_importance_80f.csv
- **AND** log low-importance features for potential removal

### Requirement: Model Performance Validation
The system SHALL validate new 80-feature models outperform baseline 45-feature models.

#### Scenario: Performance Comparison
- **WHEN** 80-feature models trained
- **THEN** system SHALL load baseline 45-feature classifier (F1=0.75)
- **AND** load baseline 45-feature regressor (R²=0.46)
- **AND** compare with new 80-feature models
- **AND** assert new classifier F1-Score > baseline + 0.10 (≥ 0.85)
- **AND** assert new regressor R² > baseline + 0.25 (≥ 0.71)
- **AND** log improvement percentages
- **AND** generate comparison report in validation_report_80f.md

#### Scenario: Cross-Segment Performance
- **WHEN** validating model performance
- **THEN** system SHALL compute metrics per customer segment:
  - persona_lujo: F1-Score, R² for luxury car predictions
  - empresa_comercial: F1-Score, R² for van/light truck predictions
  - empresa_pesado: F1-Score, R² for heavy truck predictions
- **AND** ensure no segment has F1 < 0.85 or R² < 0.75
- **AND** flag any segment with poor performance for additional training data

### Requirement: Production Model Deployment
The system SHALL deploy new 80-feature models to production with backward compatibility.

#### Scenario: Model Loading with Feature Compatibility Check
- **WHEN** adaptive_service.py loads ML models
- **THEN** system SHALL check model version metadata
- **AND** load xgboost_classifier_80f_v4.json and xgboost_regressor_80f_v4.json
- **AND** verify models expect 80 features
- **AND** set feature_processor_version to "v4"
- **AND** log model version and expected feature count

#### Scenario: Prediction with 80 Features (Authenticated)
- **WHEN** prediction requested for authenticated user
- **THEN** system SHALL use prepare_features_v4() to generate 80-feature array
- **AND** pass to classifier.predict() and regressor.predict()
- **AND** return prediction confidence scores
- **AND** log feature values for debugging (anonymized)

#### Scenario: Prediction with 45 Features (Anonymous)
- **WHEN** prediction requested for anonymous user
- **THEN** system SHALL use prepare_features_v4() with default profile/visual features
- **AND** still generate 80-feature array (with defaults)
- **AND** pass to models
- **AND** prediction SHALL work with slightly lower accuracy
- **AND** log that defaults were used

#### Scenario: Model Rollback
- **WHEN** 80-feature model causes errors in production
- **THEN** system SHALL have rollback mechanism to load 45-feature models
- **AND** switch feature_processor_version to "v3"
- **AND** continue serving predictions without downtime
- **AND** alert engineering team of rollback

---

## MODIFIED Requirements

### Requirement: Feature Processing Architecture
The system SHALL support versioned feature processors for different feature sets.

**Changes from previous version**:
- Added prepare_features_v4() supporting 80 features (previous: prepare_features_v3() with 45)
- Feature processor now accepts optional User model parameter
- Default values provided for anonymous users to maintain 80-feature compatibility

#### Scenario: Feature Processor Version Selection
- **WHEN** adaptive service initializes
- **THEN** system SHALL detect model version from model metadata
- **AND** select matching feature processor version
- **AND** v4 models → prepare_features_v4()
- **AND** v3 models → prepare_features_v3()
- **AND** log selected processor version

---

## REMOVED Requirements

None. All existing ML requirements are preserved and extended.
