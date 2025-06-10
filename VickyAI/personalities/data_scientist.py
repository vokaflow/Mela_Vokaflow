from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Tuple
import statistics
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import random

class DataScientistPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="DataScientist",
            personality_type="intelligence_analytical", # Example type
            description="Analyzes data, identifies patterns, builds models, and extracts insights using statistical methods."
        )
        self.analysis_methods = [
            'descriptive_statistics', 'inferential_statistics', 'regression_analysis',
            'classification', 'clustering', 'time_series_analysis'
        ]
        # self.data_repository, etc. are now part of PersonalityBase or managed differently
        
    def _get_initial_traits(self) -> Dict[str, float]:
        # These were previously in get_personality_traits, now correctly named
        return {
            'analytical_rigor': 0.98, # Renamed from 'analytical' to be more specific
            'methodical_approach': 0.95, # Renamed
            'statistical_acumen': 0.96, # Renamed
            'logical_reasoning': 0.94, # Renamed
            'investigative_drive': 0.92, # Renamed
            'pattern_recognition_skill': 0.93, # Added, was in old get_personality_traits
            'predictive_modeling_ability': 0.91, # Added
            'data_visualization_expertise': 0.90, # Added
            'data_cleaning_diligence': 0.88 # Added
        }
    
    def get_personality_traits(self) -> Dict[str, float]:
        return {
            'análisis_estadístico': 0.95,
            'detección_patrones': 0.93,
            'modelado_predictivo': 0.91,
            'visualización_datos': 0.90,
            'correlación_variables': 0.89,
            'limpieza_datos': 0.88,
            'interpretación_resultados': 0.87,
            'validación_hipótesis': 0.86
        }
    
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Simplified for brevity, actual implementation would be complex
        data_points = self._extract_data_points(user_input, context if context else {})
        statistical_analysis = self._perform_statistical_analysis(data_points)
        patterns = self._detect_patterns(data_points, user_input)
        insights = self._generate_insights(statistical_analysis, patterns, {}) # Empty correlations for now

        response_text = f"Data analysis for '{user_input[:30]}...' complete. "
        if insights:
            response_text += f"Key insight: {insights[0].get('description', 'Significant finding')}. "
        response_text += f"Confidence: {statistical_analysis.get('confidence_score', self.current_traits.get('analytical_rigor', 0.7))}"

        return {
            'text': response_text,
            'data_analysis_summary': statistical_analysis,
            'patterns_detected': patterns,
            'insights_generated': insights,
            'response_tone': 'analytical_methodical'
        }
    
    def get_response_style(self) -> Dict[str, Any]:
        return {
            'tone': 'analytical_methodical',
            'structure': 'systematic_scientific',
            'detail_level': 'statistically_rigorous',
            'visualization_suggestions': 'data_driven_charts', # Renamed
            'language_use': 'statistical_terminology',
            'precision_in_statements': self.current_traits.get('statistical_acumen', 0.8)
        }
    
    def _analyze_data_requirements(self, input_text):
        requirements = {
            'data_type': self._identify_data_type(input_text),
            'sample_size': self._estimate_sample_requirements(input_text),
            'variables': self._identify_variables(input_text),
            'quality_requirements': self._assess_quality_needs(input_text),
            'collection_strategy': self._suggest_collection_strategy(input_text)
        }
        return requirements
    
    def _identify_data_type(self, text):
        data_type_indicators = {
            'numerical': ['números', 'cantidad', 'medición', 'valor', 'precio'],
            'categorical': ['categoría', 'tipo', 'clase', 'grupo', 'etiqueta'],
            'temporal': ['tiempo', 'fecha', 'período', 'histórico', 'tendencia'],
            'textual': ['texto', 'comentario', 'descripción', 'opinión'],
            'binary': ['sí/no', 'verdadero/falso', 'binario', 'booleano']
        }
        
        detected_types = []
        for data_type, indicators in data_type_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                detected_types.append(data_type)
        
        return detected_types if detected_types else ['mixed']
    
    def _estimate_sample_requirements(self, text):
        if 'pequeño' in text.lower() or 'pocos' in text.lower():
            return 'small_sample_n<100'
        elif 'grande' in text.lower() or 'muchos' in text.lower():
            return 'large_sample_n>1000'
        elif 'masivo' in text.lower() or 'big_data' in text.lower():
            return 'big_data_n>100000'
        else:
            return 'medium_sample_100<n<1000'
    
    def _identify_variables(self, text):
        variable_analysis = {
            'dependent_variables': self._find_dependent_variables(text),
            'independent_variables': self._find_independent_variables(text),
            'control_variables': self._identify_control_variables(text),
            'confounding_variables': self._detect_potential_confounders(text)
        }
        return variable_analysis
    
    def _find_dependent_variables(self, text):
        # Variables que queremos predecir o explicar
        outcome_indicators = ['resultado', 'efecto', 'consecuencia', 'predicir', 'objetivo']
        if any(indicator in text.lower() for indicator in outcome_indicators):
            return ['target_outcome_variable']
        return ['to_be_determined']
    
    def _find_independent_variables(self, text):
        # Variables explicativas o predictoras
        predictor_indicators = ['causa', 'factor', 'influencia', 'predictor', 'variable']
        if any(indicator in text.lower() for indicator in predictor_indicators):
            return ['predictor_variables']
        return ['to_be_identified']
    
    def _identify_control_variables(self, text):
        control_indicators = ['controlar', 'constante', 'fijo', 'ajustar']
        if any(indicator in text.lower() for indicator in control_indicators):
            return ['control_variables_needed']
        return ['none_specified']
    
    def _detect_potential_confounders(self, text):
        confounder_indicators = ['sesgo', 'confusión', 'interferencia', 'ruido']
        if any(indicator in text.lower() for indicator in confounder_indicators):
            return ['potential_confounders_present']
        return ['to_be_assessed']
    
    def _assess_quality_needs(self, text):
        quality_requirements = {
            'accuracy': 'high' if 'preciso' in text.lower() else 'standard',
            'completeness': 'high' if 'completo' in text.lower() else 'standard',
            'consistency': 'high' if 'consistente' in text.lower() else 'standard',
            'timeliness': 'high' if 'actualizado' in text.lower() else 'standard'
        }
        return quality_requirements
    
    def _suggest_collection_strategy(self, text):
        if 'experimento' in text.lower():
            return 'experimental_design'
        elif 'encuesta' in text.lower():
            return 'survey_methodology'
        elif 'observación' in text.lower():
            return 'observational_study'
        elif 'histórico' in text.lower():
            return 'historical_data_analysis'
        else:
            return 'mixed_methods_approach'
    
    def _determine_statistical_approach(self, input_text):
        approach = {
            'primary_method': self._select_primary_method(input_text),
            'secondary_methods': self._suggest_secondary_methods(input_text),
            'assumptions': self._identify_statistical_assumptions(input_text),
            'significance_level': self._recommend_significance_level(input_text)
        }
        return approach
    
    def _select_primary_method(self, text):
        method_keywords = {
            'regression': ['relación', 'predicción', 'correlación', 'dependencia'],
            'classification': ['clasificar', 'categorizar', 'grupo', 'tipo'],
            'clustering': ['agrupar', 'segmentar', 'cluster', 'similitud'],
            'hypothesis_testing': ['comparar', 'diferencia', 'hipótesis', 'test'],
            'time_series': ['tiempo', 'tendencia', 'serie', 'temporal']
        }
        
        for method, keywords in method_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                return method
        
        return 'exploratory_data_analysis'
    
    def _suggest_secondary_methods(self, text):
        secondary_methods = []
        
        # Siempre incluir análisis exploratorio
        secondary_methods.append('exploratory_data_analysis')
        
        # Métodos de validación
        secondary_methods.append('cross_validation')
        
        # Análisis de sensibilidad
        if 'robusto' in text.lower() or 'sensibilidad' in text.lower():
            secondary_methods.append('sensitivity_analysis')
        
        return secondary_methods
    
    def _identify_statistical_assumptions(self, text):
        assumptions = [
            'independence_of_observations',
            'appropriate_sample_size',
            'data_quality_requirements'
        ]
        
        # Agregar asunciones específicas según el contexto
        if 'normal' in text.lower():
            assumptions.append('normality_assumption')
        if 'varianza' in text.lower():
            assumptions.append('homoscedasticity')
        if 'lineal' in text.lower():
            assumptions.append('linearity_assumption')
        
        return assumptions
    
    def _recommend_significance_level(self, text):
        if 'estricto' in text.lower() or 'riguroso' in text.lower():
            return 'alpha_0.01'
        elif 'exploratorio' in text.lower():
            return 'alpha_0.10'
        else:
            return 'alpha_0.05'  # Estándar
    
    def _design_analysis_methodology(self, input_text):
        methodology = {
            'phase_1': 'data_exploration_and_cleaning',
            'phase_2': self._design_phase_2(input_text),
            'phase_3': self._design_phase_3(input_text),
            'phase_4': 'validation_and_interpretation',
            'deliverables': self._define_deliverables(input_text),
            'timeline': self._estimate_timeline(input_text)
        }
        return methodology
    
    def _design_phase_2(self, text):
        if 'descriptivo' in text.lower():
            return 'descriptive_statistical_analysis'
        elif 'predictivo' in text.lower():
            return 'predictive_model_development'
        else:
            return 'inferential_statistical_analysis'
    
    def _design_phase_3(self, text):
        return 'model_validation_and_testing'
    
    def _define_deliverables(self, text):
        deliverables = [
            'statistical_analysis_report',
            'data_visualization_dashboard',
            'methodology_documentation'
        ]
        
        if 'modelo' in text.lower():
            deliverables.append('predictive_model')
        if 'presentación' in text.lower():
            deliverables.append('executive_presentation')
        
        return deliverables
    
    def _estimate_timeline(self, text):
        if 'urgente' in text.lower() or 'rápido' in text.lower():
            return '2-4_weeks'
        elif 'complejo' in text.lower() or 'detallado' in text.lower():
            return '8-12_weeks'
        else:
            return '4-6_weeks'
    
    def _generate_analytical_insights(self, input_text):
        insights = {
            'potential_patterns': self._identify_potential_patterns(input_text),
            'key_relationships': self._suggest_key_relationships(input_text),
            'risk_factors': self._identify_risk_factors(input_text),
            'opportunities': self._identify_opportunities(input_text)
        }
        return insights
    
    def _identify_potential_patterns(self, text):
        patterns = []
        
        if 'tendencia' in text.lower():
            patterns.append('temporal_trends')
        if 'ciclo' in text.lower():
            patterns.append('cyclical_patterns')
        if 'estacional' in text.lower():
            patterns.append('seasonal_variations')
        if 'grupo' in text.lower():
            patterns.append('clustering_patterns')
        
        return patterns if patterns else ['patterns_to_be_discovered']
    
    def _suggest_key_relationships(self, text):
        relationships = []
        
        if 'correlación' in text.lower():
            relationships.append('correlation_analysis_needed')
        if 'causa' in text.lower():
            relationships.append('causal_relationship_investigation')
        if 'dependencia' in text.lower():
            relationships.append('dependency_analysis')
        
        return relationships if relationships else ['relationships_to_be_explored']
    
    def _identify_risk_factors(self, text):
        risks = [
            'data_quality_issues',
            'sample_bias_potential',
            'overfitting_risk'
        ]
        
        if 'pequeño' in text.lower():
            risks.append('small_sample_size_limitations')
        if 'complejo' in text.lower():
            risks.append('model_complexity_challenges')
        
        return risks
    
    def _identify_opportunities(self, text):
        opportunities = [
            'actionable_insights_potential',
            'predictive_capability_development',
            'process_optimization_opportunities'
        ]
        
        if 'automatización' in text.lower():
            opportunities.append('automation_possibilities')
        if 'mejora' in text.lower():
            opportunities.append('improvement_identification')
        
        return opportunities
    
    def _recommend_analysis_tools(self, input_text):
        tools = {
            'statistical_software': self._recommend_statistical_software(input_text),
            'visualization_tools': self._recommend_visualization_tools(input_text),
            'data_processing': self._recommend_data_processing_tools(input_text),
            'machine_learning': self._recommend_ml_tools(input_text)
        }
        return tools
    
    def _recommend_statistical_software(self, text):
        if 'avanzado' in text.lower():
            return ['R', 'Python_scipy_statsmodels']
        elif 'simple' in text.lower():
            return ['Excel', 'SPSS']
        else:
            return ['Python_pandas', 'R']
    
    def _recommend_visualization_tools(self, text):
        return ['matplotlib', 'seaborn', 'plotly', 'ggplot2']
    
    def _recommend_data_processing_tools(self, text):
        return ['pandas', 'numpy', 'dplyr', 'data.table']
    
    def _recommend_ml_tools(self, text):
        if 'machine_learning' in text.lower() or 'aprendizaje' in text.lower():
            return ['scikit-learn', 'tensorflow', 'pytorch']
        return ['not_required']
    
    def _design_validation_strategy(self, input_text):
        strategy = {
            'validation_method': self._select_validation_method(input_text),
            'performance_metrics': self._define_performance_metrics(input_text),
            'robustness_tests': self._design_robustness_tests(input_text),
            'interpretation_guidelines': self._create_interpretation_guidelines(input_text)
        }
        return strategy
    
    def _select_validation_method(self, text):
        if 'predicción' in text.lower():
            return 'cross_validation_with_holdout'
        elif 'clasificación' in text.lower():
            return 'stratified_cross_validation'
        else:
            return 'bootstrap_validation'
    
    def _define_performance_metrics(self, text):
        if 'precisión' in text.lower():
            return ['accuracy', 'precision', 'recall', 'f1_score']
        elif 'predicción' in text.lower():
            return ['rmse', 'mae', 'r_squared']
        else:
            return ['appropriate_metrics_to_be_determined']
    
    def _design_robustness_tests(self, text):
        tests = [
            'outlier_sensitivity_analysis',
            'assumption_violation_testing',
            'alternative_model_comparison'
        ]
        return tests
    
    def _create_interpretation_guidelines(self, text):
        guidelines = [
            'statistical_significance_interpretation',
            'practical_significance_assessment',
            'confidence_interval_interpretation',
            'limitation_acknowledgment'
        ]
        return guidelines
    
    def _analyze_data_patterns(self, data):
        # Analizar patrones en los datos
        return {
            'data_type': 'mixed',
            'sample_size': 'adequate',
            'distribution': 'normal',
            'outliers': 'detected',
            'correlations': {}
        }
    
    def _generate_statistical_insights(self, analysis):
        # Generar insights estadísticos
        return {
            'mean': 0.0,
            'median': 0.0,
            'std_deviation': 0.0,
            'variance': 0.0,
            'significance_tests': {}
        }
    
    def _make_predictions(self, data):
        # Hacer predicciones basadas en datos
        return {
            'model_type': 'regression',
            'accuracy': 0.85,
            'predictions': [],
            'model_performance': 'good'
        }
    
    def _generate_data_recommendations(self, insights: List, statistical_analysis: Dict) -> List[Dict[str, Any]]:
        return [
            "Collect more data for better accuracy",
            "Consider feature engineering",
            "Validate model with cross-validation",
            "Monitor for data drift"
        ]
    
    def _calculate_confidence_intervals(self, analysis):
        # Calcular intervalos de confianza
        return {
            '95%_confidence': [0.0, 1.0],
            '99%_confidence': [0.0, 1.0]
        }
    
    # Keeping a few helper methods as stubs for structure, full implementation is extensive
    def _extract_data_points(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {'numerical_data': [float(x) for x in re.findall(r'\d+\.?\d*', text)]}

    def _perform_statistical_analysis(self, data_points: Dict) -> Dict[str, Any]:
        num_data = data_points.get('numerical_data', [])
        if not num_data: return {'message': 'No numerical data'}
        return {
            'mean': statistics.mean(num_data) if num_data else 0,
            'median': statistics.median(num_data) if num_data else 0,
            'std_dev': statistics.stdev(num_data) if len(num_data) > 1 else 0,
            'confidence_score': 0.85 # Placeholder
        }

    def _detect_patterns(self, data_points: Dict, original_text: str) -> Dict[str, Any]:
        return {'trend': 'stable', 'outliers': 0} # Placeholder

    def _generate_insights(self, statistical_analysis: Dict, pattern_detection: Dict,
                          correlation_analysis: Dict) -> List[Dict[str, Any]]:
        insights = []
        if statistical_analysis.get('mean', 0) > 100:
            insights.append({'type': 'high_average', 'description': 'Average value is notably high.'})
        return insights
    
    def _extract_data_points(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae puntos de datos del texto y contexto"""
        data_points = {
            'numerical_data': self._extract_numerical_data(text),
            'categorical_data': self._extract_categorical_data(text),
            'temporal_data': self._extract_temporal_data(text),
            'textual_metrics': self._calculate_textual_metrics(text),
            'context_data': self._extract_context_data(context),
            'metadata': {
                'extraction_timestamp': datetime.now().isoformat(),
                'data_source': 'user_input',
                'data_quality': 'raw'
            }
        }
        
        return data_points
    
    def _perform_statistical_analysis(self, data_points: Dict) -> Dict[str, Any]:
        """Realiza análisis estadístico de los datos"""
        numerical_data = data_points.get('numerical_data', [])
        
        if not numerical_data:
            return self._generate_non_numerical_statistics(data_points)
        
        # Estadísticas descriptivas
        descriptive_stats = self._calculate_descriptive_statistics(numerical_data)
        
        # Análisis de distribución
        distribution_analysis = self._analyze_distribution(numerical_data)
        
        # Detección de outliers
        outlier_analysis = self._detect_outliers(numerical_data)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_trends(numerical_data)
        
        # Pruebas de normalidad
        normality_tests = self._test_normality(numerical_data)
        
        return {
            'descriptive_statistics': descriptive_stats,
            'distribution_analysis': distribution_analysis,
            'outlier_analysis': outlier_analysis,
            'trend_analysis': trend_analysis,
            'normality_tests': normality_tests,
            'sample_size': len(numerical_data),
            'data_completeness': self._calculate_completeness(data_points)
        }
    
    def _detect_patterns(self, data_points: Dict, original_text: str) -> Dict[str, Any]:
        """Detecta patrones en los datos"""
        patterns = {
            'numerical_patterns': self._detect_numerical_patterns(data_points.get('numerical_data', [])),
            'textual_patterns': self._detect_textual_patterns(original_text),
            'temporal_patterns': self._detect_temporal_patterns(data_points.get('temporal_data', [])),
            'frequency_patterns': self._detect_frequency_patterns(data_points),
            'sequence_patterns': self._detect_sequence_patterns(data_points),
            'anomaly_patterns': self._detect_anomaly_patterns(data_points)
        }
        
        # Evaluar significancia de patrones
        pattern_significance = self._evaluate_pattern_significance(patterns)
        
        return {
            'detected_patterns': patterns,
            'pattern_significance': pattern_significance,
            'pattern_confidence': self._calculate_pattern_confidence(patterns),
            'actionable_patterns': self._identify_actionable_patterns(patterns)
        }
    
    def _analyze_correlations(self, data_points: Dict) -> Dict[str, Any]:
        """Analiza correlaciones entre variables"""
        numerical_data = data_points.get('numerical_data', [])
        categorical_data = data_points.get('categorical_data', [])
        
        correlations = {
            'numerical_correlations': self._calculate_numerical_correlations(numerical_data),
            'categorical_associations': self._analyze_categorical_associations(categorical_data),
            'mixed_correlations': self._analyze_mixed_correlations(numerical_data, categorical_data),
            'temporal_correlations': self._analyze_temporal_correlations(data_points.get('temporal_data', []))
        }
        
        # Identificar correlaciones significativas
        significant_correlations = self._identify_significant_correlations(correlations)
        
        return {
            'correlation_results': correlations,
            'significant_correlations': significant_correlations,
            'correlation_strength': self._assess_correlation_strength(correlations),
            'causal_hypotheses': self._generate_causal_hypotheses(significant_correlations)
        }
    
    def _generate_insights(self, statistical_analysis: Dict, pattern_detection: Dict, 
                          correlation_analysis: Dict) -> List[Dict[str, Any]]:
        """Genera insights basados en el análisis"""
        insights = []
        
        # Insights estadísticos
        stats_insights = self._extract_statistical_insights(statistical_analysis)
        insights.extend(stats_insights)
        
        # Insights de patrones
        pattern_insights = self._extract_pattern_insights(pattern_detection)
        insights.extend(pattern_insights)
        
        # Insights de correlaciones
        correlation_insights = self._extract_correlation_insights(correlation_analysis)
        insights.extend(correlation_insights)
        
        # Insights contextuales
        contextual_insights = self._generate_contextual_insights(statistical_analysis, pattern_detection)
        insights.extend(contextual_insights)
        
        # Priorizar insights por relevancia
        prioritized_insights = self._prioritize_insights(insights)
        
        return prioritized_insights
    
    def _suggest_visualizations(self, data_points: Dict, insights: List) -> List[Dict[str, Any]]:
        """Sugiere visualizaciones apropiadas para los datos"""
        visualizations = []
        
        numerical_data = data_points.get('numerical_data', [])
        categorical_data = data_points.get('categorical_data', [])
        temporal_data = data_points.get('temporal_data', [])
        
        # Visualizaciones para datos numéricos
        if numerical_data:
            if len(numerical_data) > 1:
                visualizations.append({
                    'type': 'histogram',
                    'description': 'Distribución de valores numéricos',
                    'data_type': 'numerical',
                    'priority': 'high'
                })
                
                visualizations.append({
                    'type': 'box_plot',
                    'description': 'Análisis de outliers y cuartiles',
                    'data_type': 'numerical',
                    'priority': 'medium'
                })
        
        # Visualizaciones para datos categóricos
        if categorical_data:
            visualizations.append({
                'type': 'bar_chart',
                'description': 'Frecuencia de categorías',
                'data_type': 'categorical',
                'priority': 'high'
            })
            
            if len(set(categorical_data)) <= 10:
                visualizations.append({
                    'type': 'pie_chart',
                    'description': 'Distribución proporcional de categorías',
                    'data_type': 'categorical',
                    'priority': 'medium'
                })
        
        # Visualizaciones para datos temporales
        if temporal_data:
            visualizations.append({
                'type': 'time_series',
                'description': 'Evolución temporal de los datos',
                'data_type': 'temporal',
                'priority': 'high'
            })
        
        # Visualizaciones basadas en insights
        insight_visualizations = self._suggest_insight_visualizations(insights)
        visualizations.extend(insight_visualizations)
        
        return visualizations
    
    def _validate_hypotheses(self, text: str, statistical_analysis: Dict) -> Dict[str, Any]:
        """Valida hipótesis mencionadas en el texto"""
        # Detectar hipótesis en el texto
        hypotheses = self._extract_hypotheses(text)
        
        if not hypotheses:
            return {'hypotheses_found': False, 'message': 'No se detectaron hipótesis explícitas'}
        
        validation_results = []
        
        for hypothesis in hypotheses:
            validation = self._test_hypothesis(hypothesis, statistical_analysis)
            validation_results.append(validation)
        
        return {
            'hypotheses_found': True,
            'total_hypotheses': len(hypotheses),
            'validation_results': validation_results,
            'overall_validation_confidence': self._calculate_validation_confidence(validation_results)
        }
    
    def _assess_data_quality(self, data_points: Dict) -> Dict[str, Any]:
        """Evalúa la calidad de los datos"""
        quality_metrics = {
            'completeness': self._calculate_completeness(data_points),
            'consistency': self._assess_consistency(data_points),
            'accuracy': self._estimate_accuracy(data_points),
            'timeliness': self._assess_timeliness(data_points),
            'validity': self._validate_data_format(data_points)
        }
        
        # Calcular puntuación general de calidad
        overall_quality = statistics.mean(quality_metrics.values())
        
        # Determinar nivel de calidad
        if overall_quality >= 0.8:
            quality_level = 'high'
        elif overall_quality >= 0.6:
            quality_level = 'medium'
        else:
            quality_level = 'low'
        
        return {
            'quality_metrics': quality_metrics,
            'overall_quality_score': overall_quality,
            'quality_level': quality_level,
            'quality_issues': self._identify_quality_issues(quality_metrics),
            'improvement_suggestions': self._suggest_quality_improvements(quality_metrics)
        }
    
    def _store_data_point(self, original_input: str, data_points: Dict, insights: List):
        """Almacena punto de datos para análisis futuro"""
        data_entry = {
            'timestamp': datetime.now().isoformat(),
            'original_input': original_input,
            'extracted_data': data_points,
            'insights': insights,
            'data_hash': hash(str(data_points))
        }
        
        self.data_repository.append(data_entry)
        
        # Mantener solo los últimos 1000 puntos de datos
        if len(self.data_repository) > 1000:
            self.data_repository = self.data_repository[-1000:]
    
    # Métodos auxiliares de extracción de datos
    def _extract_numerical_data(self, text: str) -> List[float]:
        """Extrae datos numéricos del texto"""
        # Buscar números en el texto
        number_pattern = r'-?\d+\.?\d*'
        numbers = re.findall(number_pattern, text)
        
        numerical_data = []
        for num_str in numbers:
            try:
                num = float(num_str)
                numerical_data.append(num)
            except ValueError:
                continue
        
        return numerical_data
    
    def _extract_categorical_data(self, text: str) -> List[str]:
        """Extrae datos categóricos del texto"""
        # Identificar palabras que podrían ser categorías
        words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b', text.lower())
        
        # Filtrar palabras comunes
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le'}
        categorical_data = [word for word in words if word not in stop_words and len(word) > 2]
        
        return categorical_data
    
    def _extract_temporal_data(self, text: str) -> List[str]:
        """Extrae datos temporales del texto"""
        temporal_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # Fechas
            r'\b\d{1,2}:\d{2}\b',            # Horas
            r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
            r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b'
        ]
        
        temporal_data = []
        for pattern in temporal_patterns:
            matches = re.findall(pattern, text.lower())
            temporal_data.extend(matches)
        
        return temporal_data
    
    def _calculate_textual_metrics(self, text: str) -> Dict[str, Any]:
        """Calcula métricas del texto"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_word_length': statistics.mean([len(word) for word in words]) if words else 0,
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'readability_score': self._calculate_readability_score(text)
        }
    
    def _extract_context_data(self, context: Dict) -> Dict[str, Any]:
        """Extrae datos del contexto"""
        if not context:
            return {}
        
        context_metrics = {
            'context_size': len(str(context)),
            'context_keys': list(context.keys()) if isinstance(context, dict) else [],
            'context_depth': self._calculate_context_depth(context),
            'context_type': type(context).__name__
        }
        
        return context_metrics
    
    # Métodos de análisis estadístico
    def _calculate_descriptive_statistics(self, data: List[float]) -> Dict[str, float]:
        """Calcula estadísticas descriptivas"""
        if not data:
            return {}
        
        return {
            'mean': statistics.mean(data),
            'median': statistics.median(data),
            'mode': statistics.mode(data) if len(set(data)) < len(data) else None,
            'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
            'variance': statistics.variance(data) if len(data) > 1 else 0,
            'min': min(data),
            'max': max(data),
            'range': max(data) - min(data),
            'q1': statistics.quantiles(data, n=4)[0] if len(data) >= 4 else None,
            'q3': statistics.quantiles(data, n=4)[2] if len(data) >= 4 else None
        }
    
    def _analyze_distribution(self, data: List[float]) -> Dict[str, Any]:
        """Analiza la distribución de los datos"""
        if len(data) < 3:
            return {'distribution_type': 'insufficient_data'}
        
        # Análisis básico de distribución
        mean_val = statistics.mean(data)
        median_val = statistics.median(data)
        
        # Determinar tipo de distribución aproximado
        if abs(mean_val - median_val) < 0.1 * statistics.stdev(data):
            distribution_type = 'approximately_normal'
        elif mean_val > median_val:
            distribution_type = 'right_skewed'
        else:
            distribution_type = 'left_skewed'
        
        return {
            'distribution_type': distribution_type,
            'skewness': self._calculate_skewness(data),
            'kurtosis': self._calculate_kurtosis(data),
            'symmetry_score': abs(mean_val - median_val) / statistics.stdev(data) if statistics.stdev(data) > 0 else 0
        }
    
    def _detect_outliers(self, data: List[float]) -> Dict[str, Any]:
        """Detecta outliers en los datos"""
        if len(data) < 4:
            return {'outliers_detected': False, 'method': 'insufficient_data'}
        
        # Método IQR
        q1 = statistics.quantiles(data, n=4)[0]
        q3 = statistics.quantiles(data, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        
        return {
            'outliers_detected': len(outliers) > 0,
            'outlier_count': len(outliers),
            'outlier_values': outliers,
            'outlier_percentage': len(outliers) / len(data) * 100,
            'method': 'IQR',
            'bounds': {'lower': lower_bound, 'upper': upper_bound}
        }
    
    def _analyze_trends(self, data: List[float]) -> Dict[str, Any]:
        """Analiza tendencias en los datos"""
        if len(data) < 3:
            return {'trend': 'insufficient_data'}
        
        # Calcular tendencia simple
        first_half = data[:len(data)//2]
        second_half = data[len(data)//2:]
        
        first_mean = statistics.mean(first_half)
        second_mean = statistics.mean(second_half)
        
        if second_mean > first_mean * 1.05:
            trend = 'increasing'
        elif second_mean < first_mean * 0.95:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'trend_strength': abs(second_mean - first_mean) / first_mean if first_mean != 0 else 0,
            'first_half_mean': first_mean,
            'second_half_mean': second_mean
        }
    
    def _test_normality(self, data: List[float]) -> Dict[str, Any]:
        """Prueba de normalidad básica"""
        if len(data) < 8:
            return {'test': 'insufficient_data', 'normal': None}
        
        # Prueba simple basada en skewness y kurtosis
        skewness = self._calculate_skewness(data)
        kurtosis = self._calculate_kurtosis(data)
        
        # Criterios aproximados para normalidad
        is_normal = abs(skewness) < 1 and abs(kurtosis - 3) < 1
        
        return {
            'test': 'skewness_kurtosis',
            'normal': is_normal,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'confidence': 0.8 if is_normal else 0.6
        }
    
    # Métodos auxiliares de cálculo
    def _calculate_skewness(self, data: List[float]) -> float:
        """Calcula la asimetría de los datos"""
        if len(data) < 3:
            return 0.0
        
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        if std_val == 0:
            return 0.0
        
        n = len(data)
        skewness = sum(((x - mean_val) / std_val) ** 3 for x in data) / n
        
        return skewness
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calcula la curtosis de los datos"""
        if len(data) < 4:
            return 3.0  # Curtosis normal
        
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        if std_val == 0:
            return 3.0
        
        n = len(data)
        kurtosis = sum(((x - mean_val) / std_val) ** 4 for x in data) / n
        
        return kurtosis
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calcula puntuación de legibilidad simplificada"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        if not words or not sentences:
            return 0.0
        
        average_sentence_length = len(words) / len(sentences) if sentences else 0
        average_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words) if words else 0
        
        # Fórmula Flesch-Kincaid simplificada
        readability = 206.835 - 1.015 * average_sentence_length - 84.6 * average_syllables_per_word
        
        return readability
    
    def _calculate_completeness(self, data_points: Dict) -> float:
        """Calcula la completitud de los datos"""
        total_fields = 0
        complete_fields = 0
        
        for key, value in data_points.items():
            if isinstance(value, dict):
                total_fields += len(value)
                complete_fields += sum(1 for v in value.values() if v is not None)
            elif isinstance(value, list):
                total_fields += len(value)
                complete_fields += sum(1 for item in value if item is not None)
            else:
                total_fields += 1
                if value is not None:
                    complete_fields += 1
        
        if total_fields == 0:
            return 1.0
        
        return complete_fields / total_fields
    
    def _assess_consistency(self, data_points: Dict) -> float:
        """Evalúa la consistencia de los datos"""
        # Implementación placeholder
        return 0.9  # Valor por defecto
    
    def _estimate_accuracy(self, data_points: Dict) -> float:
        """Estima la precisión de los datos"""
        # Implementación placeholder
        return 0.8  # Valor por defecto
    
    def _assess_timeliness(self, data_points: Dict) -> float:
        """Evalúa la puntualidad de los datos"""
        # Implementación placeholder
        return 0.7  # Valor por defecto
    
    def _validate_data_format(self, data_points: Dict) -> float:
        """Valida el formato de los datos"""
        # Implementación placeholder
        return 0.95  # Valor por defecto
    
    def _identify_quality_issues(self, quality_metrics: Dict) -> List[str]:
        """Identifica problemas de calidad"""
        issues = []
        
        if quality_metrics.get('completeness', 1.0) < 0.7:
            issues.append('low_completeness')
        if quality_metrics.get('consistency', 1.0) < 0.7:
            issues.append('low_consistency')
        if quality_metrics.get('accuracy', 1.0) < 0.7:
            issues.append('low_accuracy')
        if quality_metrics.get('timeliness', 1.0) < 0.7:
            issues.append('low_timeliness')
        if quality_metrics.get('validity', 1.0) < 0.7:
            issues.append('invalid_data_format')
        
        return issues
    
    def _suggest_quality_improvements(self, quality_metrics: Dict) -> List[str]:
        """Sugiere mejoras de calidad"""
        suggestions = []
        
        if quality_metrics.get('completeness', 1.0) < 0.7:
            suggestions.append('fill_missing_values')
        if quality_metrics.get('consistency', 1.0) < 0.7:
            suggestions.append('standardize_data_formats')
        if quality_metrics.get('accuracy', 1.0) < 0.7:
            suggestions.append('verify_data_sources')
        if quality_metrics.get('timeliness', 1.0) < 0.7:
            suggestions.append('update_data_frequently')
        if quality_metrics.get('validity', 1.0) < 0.7:
            suggestions.append('validate_data_schemas')
        
        return suggestions
    
    def _generate_non_numerical_statistics(self, data_points: Dict) -> Dict[str, Any]:
        """Genera estadísticas para datos no numéricos"""
        categorical_data = data_points.get('categorical_data', [])
        temporal_data = data_points.get('temporal_data', [])
        textual_metrics = data_points.get('textual_metrics', {})
        
        statistics = {
            'categorical_counts': Counter(categorical_data),
            'temporal_frequency': Counter(temporal_data),
            'textual_summary': textual_metrics
        }
        
        return statistics
    
    def _detect_numerical_patterns(self, data: List[float]) -> Dict[str, Any]:
        """Detecta patrones en datos numéricos"""
        if len(data) < 5:
            return {'patterns_found': False, 'message': 'insufficient_data'}
        
        # Calcular diferencias
        differences = [data[i+1] - data[i] for i in range(len(data) - 1)]
        
        # Detectar patrones de crecimiento
        increasing = all(d > 0 for d in differences)
        decreasing = all(d < 0 for d in differences)
        
        # Detectar patrones cíclicos
        cyclic = self._is_cyclic(data)
        
        return {
            'patterns_found': True,
            'increasing': increasing,
            'decreasing': decreasing,
            'cyclic': cyclic,
            'average_growth_rate': statistics.mean(differences) if differences else 0
        }
    
    def _detect_textual_patterns(self, text: str) -> Dict[str, Any]:
        """Detecta patrones en texto"""
        # Frecuencia de palabras
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Identificar palabras clave
        keywords = ['importante', 'clave', 'necesario']
        keyword_frequency = {keyword: word_counts[keyword] for keyword in keywords}
        
        return {
            'word_frequency': word_counts.most_common(10),
            'keyword_frequency': keyword_frequency,
            'average_word_length': statistics.mean([len(word) for word in words]) if words else 0
        }
    
    def _detect_temporal_patterns(self, data: List[str]) -> Dict[str, Any]:
        """Detecta patrones en datos temporales"""
        if not data:
            return {'patterns_found': False, 'message': 'no_temporal_data'}
        
        # Frecuencia de fechas
        date_counts = Counter(data)
        
        # Identificar tendencias
        if len(date_counts) > 5:
            first_date = min(date_counts.keys())
            last_date = max(date_counts.keys())
            trend = 'increasing' if last_date > first_date else 'decreasing'
        else:
            trend = 'no_clear_trend'
        
        return {
            'date_frequency': date_counts.most_common(5),
            'trend': trend
        }
    
    def _detect_frequency_patterns(self, data_points: Dict) -> Dict[str, Any]:
        """Detecta patrones de frecuencia"""
        # Combinar datos categóricos y numéricos
        all_data = []
        if 'categorical_data' in data_points:
            all_data.extend(data_points['categorical_data'])
        if 'numerical_data' in data_points:
            all_data.extend(map(str, data_points['numerical_data']))
        
        if not all_data:
            return {'patterns_found': False, 'message': 'no_data_for_frequency_analysis'}
        
        # Calcular frecuencias
        frequency_counts = Counter(all_data)
        
        return {
            'most_common_items': frequency_counts.most_common(10)
        }
    
    def _detect_sequence_patterns(self, data_points: Dict) -> Dict[str, Any]:
        """Detecta patrones de secuencia"""
        # Combinar datos categóricos y numéricos
        all_data = []
        if 'categorical_data' in data_points:
            all_data.extend(data_points['categorical_data'])
        if 'numerical_data' in data_points:
            all_data.extend(map(str, data_points['numerical_data']))
        
        if len(all_data) < 3:
            return {'patterns_found': False, 'message': 'insufficient_data_for_sequence_analysis'}
        
        # Buscar secuencias repetidas
        sequences = defaultdict(int)
        for i in range(len(all_data) - 2):
            sequence = tuple(all_data[i:i+3])
            sequences[sequence] += 1
        
        most_common_sequence = max(sequences, key=sequences.get) if sequences else None
        
        return {
            'most_common_sequence': list(most_common_sequence) if most_common_sequence else None,
            'sequence_frequency': sequences.get(most_common_sequence) if most_common_sequence else 0
        }
    
    def _detect_anomaly_patterns(self, data_points: Dict) -> Dict[str, Any]:
        """Detecta patrones de anomalías"""
        numerical_data = data_points.get('numerical_data', [])
        
        if len(numerical_data) < 5:
            return {'patterns_found': False, 'message': 'insufficient_numerical_data'}
        
        # Calcular media y desviación estándar
        mean_val = statistics.mean(numerical_data)
        std_val = statistics.stdev(numerical_data)
        
        # Identificar anomalías (valores fuera de 3 desviaciones estándar)
        anomalies = [x for x in numerical_data if abs(x - mean_val) > 3 * std_val]
        
        return {
            'anomalies_detected': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'anomaly_values': anomalies
        }
    
    def _evaluate_pattern_significance(self, patterns: Dict) -> Dict[str, Any]:
        """Evalúa la significancia de los patrones"""
        # Implementación placeholder
        return {'significance_level': 'medium'}
    
    def _calculate_pattern_confidence(self, patterns: Dict) -> float:
        """Calcula la confianza en los patrones"""
        # Implementación placeholder
        return 0.75
    
    def _identify_actionable_patterns(self, patterns: Dict) -> List[str]:
        """Identifica patrones accionables"""
        # Implementación placeholder
        return ['investigate_further']
    
    def _calculate_numerical_correlations(self, data: List[float]) -> Dict[str, float]:
        """Calcula correlaciones numéricas"""
        if len(data) < 2:
            return {'message': 'insufficient_numerical_data'}
        
        # Crear matriz de correlación
        correlation_matrix = {}
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                correlation = statistics.correlation(data[i:], data[j:])
                correlation_matrix[f'var_{i}_var_{j}'] = correlation
        
        return correlation_matrix
    
    def _analyze_categorical_associations(self, data: List[str]) -> Dict[str, Any]:
        """Analiza asociaciones categóricas"""
        if len(data) < 2:
            return {'message': 'insufficient_categorical_data'}
        
        # Crear tabla de contingencia
        contingency_table = defaultdict(lambda: defaultdict(int))
        for i in range(len(data) - 1):
            contingency_table[data[i]][data[i+1]] += 1
        
        return {'contingency_table': contingency_table}
    
    def _analyze_mixed_correlations(self, numerical_data: List[float], categorical_data: List[str]) -> Dict[str, Any]:
        """Analiza correlaciones mixtas"""
        if not numerical_data or not categorical_data:
            return {'message': 'insufficient_data'}
        
        # Calcular correlación para cada categoría
        correlations = {}
        for category in set(categorical_data):
            numerical_subset = [numerical_data[i] for i in range(len(numerical_data)) if categorical_data[i] == category]
            if len(numerical_subset) > 1:
                correlation = statistics.correlation(numerical_subset, numerical_data)
                correlations[category] = correlation
        
        return {'correlations': correlations}
    
    def _analyze_temporal_correlations(self, data: List[str]) -> Dict[str, Any]:
        """Analiza correlaciones temporales"""
        if len(data) < 2:
            return {'message': 'insufficient_temporal_data'}
        
        # Calcular diferencias temporales
        time_differences = []
        for i in range(len(data) - 1):
            try:
                date1 = datetime.strptime(data[i], '%Y-%m-%d')
                date2 = datetime.strptime(data[i+1], '%Y-%m-%d')
                time_diff = (date2 - date1).days
                time_differences.append(time_diff)
            except ValueError:
                continue
        
        return {'time_differences': time_differences}
    
    def _identify_significant_correlations(self, correlations: Dict) -> List[str]:
        """Identifica correlaciones significativas"""
        # Implementación placeholder
        return ['correlation_1', 'correlation_2']
    
    def _assess_correlation_strength(self, correlations: Dict) -> Dict[str, str]:
        """Evalúa la fuerza de las correlaciones"""
        # Implementación placeholder
        return {'strength': 'medium'}
    
    def _generate_causal_hypotheses(self, significant_correlations: List[str]) -> List[str]:
        """Genera hipótesis causales"""
        # Implementación placeholder
        return ['hypothesis_1', 'hypothesis_2']
    
    def _extract_statistical_insights(self, statistical_analysis: Dict) -> List[Dict[str, Any]]:
        """Extrae insights estadísticos"""
        insights = []
        
        if 'descriptive_statistics' in statistical_analysis:
            stats = statistical_analysis['descriptive_statistics']
            if 'mean' in stats:
                insights.append({'type': 'mean_value', 'value': stats['mean']})
            if 'median' in stats:
                insights.append({'type': 'median_value', 'value': stats['median']})
            if 'std_dev' in stats:
                insights.append({'type': 'std_deviation', 'value': stats['std_dev']})
        
        return insights
    
    def _extract_pattern_insights(self, pattern_detection: Dict) -> List[Dict[str, Any]]:
        """Extrae insights de patrones"""
        insights = []
        
        if 'detected_patterns' in pattern_detection:
            patterns = pattern_detection['detected_patterns']
            if 'increasing' in patterns and patterns['increasing']:
                insights.append({'type': 'increasing_trend', 'description': 'data is increasing'})
            if 'decreasing' in patterns and patterns['decreasing']:
                insights.append({'type': 'decreasing_trend', 'description': 'data is decreasing'})
        
        return insights
    
    def _extract_correlation_insights(self, correlation_analysis: Dict) -> List[Dict[str, Any]]:
        """Extrae insights de correlaciones"""
        insights = []
        
        if 'significant_correlations' in correlation_analysis:
            correlations = correlation_analysis['significant_correlations']
            for correlation in correlations:
                insights.append({'type': 'significant_correlation', 'correlation': correlation})
        
        return insights
    
    def _generate_contextual_insights(self, statistical_analysis: Dict, pattern_detection: Dict) -> List[Dict[str, Any]]:
        """Genera insights contextuales"""
        insights = []
        
        if statistical_analysis.get('sample_size', 0) < 30:
            insights.append({'type': 'small_sample_size', 'recommendation': 'collect more data'})
        
        return insights
    
    def _prioritize_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriza insights por relevancia"""
        # Implementación placeholder
        return insights
    
    def _suggest_insight_visualizations(self, insights: List) -> List[Dict[str, Any]]:
        """Sugiere visualizaciones basadas en insights"""
        visualizations = []
        
        for insight in insights:
            if insight['type'] == 'mean_value':
                visualizations.append({'type': 'bar_chart', 'description': 'mean value'})
            elif insight['type'] == 'significant_correlation':
                visualizations.append({'type': 'scatter_plot', 'description': 'correlation'})
        
        return visualizations
    
    def _extract_hypotheses(self, text: str) -> List[str]:
        """Extrae hipótesis del texto"""
        # Implementación placeholder
        return ['hypothesis_1', 'hypothesis_2']
    
    def _test_hypothesis(self, hypothesis: str, statistical_analysis: Dict) -> Dict[str, Any]:
        """Prueba una hipótesis"""
        # Implementación placeholder
        return {'hypothesis': hypothesis, 'valid': True}
    
    def _calculate_validation_confidence(self, validation_results: List[Dict[str, Any]]) -> float:
        """Calcula la confianza en la validación"""
        # Implementación placeholder
        return 0.8
    
    def _generate_data_quality_recommendations(self, statistical_analysis: Dict) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en la calidad de los datos"""
        recommendations = []
        
        if statistical_analysis.get('data_completeness', 1.0) < 0.8:
            recommendations.append({'type': 'data_quality', 'recommendation': 'improve data completeness'})
        
        return recommendations
    
    def _generate_insight_recommendations(self, insights: List) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en insights"""
        recommendations = []
        
        for insight in insights:
            if insight['type'] == 'increasing_trend':
                recommendations.append({'type': 'trend_analysis', 'recommendation': 'investigate increasing trend'})
        
        return recommendations
    
    def _suggest_additional_analysis(self, statistical_analysis: Dict, insights: List) -> List[Dict[str, Any]]:
        """Sugiere análisis adicional"""
        recommendations = []
        
        if not insights:
            recommendations.append({'type': 'additional_analysis', 'recommendation': 'perform more analysis'})
        
        return recommendations
    
    def _generate_action_recommendations(self, insights: List) -> List[Dict[str, Any]]:
        """Genera recomendaciones de acción"""
        recommendations = []
        
        for insight in insights:
            if insight['type'] == 'significant_correlation':
                recommendations.append({'type': 'action_recommendation', 'recommendation': 'take action based on correlation'})
        
        return recommendations
    
    def _count_syllables(self, word: str) -> int:
        """Cuenta las sílabas de una palabra"""
        vowels = "AEIOUaeiou"
        syllable_count = 0
        
        if not word:
            return 0
        
        if word[0] in vowels:
            syllable_count += 1
        
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                syllable_count += 1
        
        if word.endswith('e'):
            syllable_count -= 1
        
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1
        
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _is_cyclic(self, data: List[float]) -> bool:
        """Determina si los datos son cíclicos"""
        if len(data) < 10:
            return False
        
        # Calcular autocorrelación
        n = len(data)
        mean_val = statistics.mean(data)
        
        numerator = sum((data[i] - mean_val) * (data[(i + 1) % n] - mean_val) for i in range(n))
        denominator = sum((data[i] - mean_val) ** 2 for i in range(n))
        
        if denominator == 0:
            return False
        
        autocorrelation = numerator / denominator
        
        # Considerar cíclico si la autocorrelación es alta
        return autocorrelation > 0.5
