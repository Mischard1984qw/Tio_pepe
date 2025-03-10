"""Data processing and analysis agent for the Tío Pepe system."""

from typing import Dict, Any, Union, List
import logging
import pandas as pd
import numpy as np

class DataAgent:
    """Specialized agent for data processing and analysis tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

    def process_task(self, task: Any) -> Dict[str, Any]:
        """Process a data task based on its type."""
        task_type = task.data.get('data_type')
        data = task.data.get('data')

        if not data:
            raise ValueError("No data provided for processing")

        if task_type == 'analysis':
            return self._analyze_data(data)
        elif task_type == 'transformation':
            return self._transform_data(data)
        elif task_type == 'statistics':
            return self._calculate_statistics(data)
        else:
            raise ValueError(f"Unsupported data task type: {task_type}")

    def _analyze_data(self, data: Union[pd.DataFrame, List, Dict]) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        try:
            if isinstance(data, (list, dict)):
                df = pd.DataFrame(data)
            else:
                df = data

            analysis = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'data_types': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_summary': df.describe().to_dict() if not df.empty else {},
                'correlations': df.corr().to_dict() if df.select_dtypes(include=[np.number]).columns.size > 1 else {}
            }
            return {'analysis_results': analysis}

        except Exception as e:
            self.logger.error(f"Data analysis error: {str(e)}")
            raise

    def _transform_data(self, data: Union[pd.DataFrame, List, Dict]) -> Dict[str, Any]:
        """Transform data according to specified operations."""
        try:
            if isinstance(data, (list, dict)):
                df = pd.DataFrame(data)
            else:
                df = data

            # Apply common data transformations
            transformed_data = {
                'normalized': self._normalize_numeric_columns(df),
                'encoded_categories': self._encode_categorical_columns(df),
                'filled_missing': self._handle_missing_values(df)
            }
            return {'transformed_data': transformed_data}

        except Exception as e:
            self.logger.error(f"Data transformation error: {str(e)}")
            raise

    def _calculate_statistics(self, data: Union[pd.DataFrame, List, Dict]) -> Dict[str, Any]:
        """Calculate detailed statistical metrics."""
        try:
            if isinstance(data, (list, dict)):
                df = pd.DataFrame(data)
            else:
                df = data

            numeric_cols = df.select_dtypes(include=[np.number]).columns
            stats = {
                'basic_stats': df[numeric_cols].agg(['mean', 'median', 'std', 'min', 'max']).to_dict(),
                'quartiles': df[numeric_cols].quantile([0.25, 0.5, 0.75]).to_dict(),
                'skewness': df[numeric_cols].skew().to_dict(),
                'kurtosis': df[numeric_cols].kurtosis().to_dict()
            }
            return {'statistical_metrics': stats}

        except Exception as e:
            self.logger.error(f"Statistical calculation error: {str(e)}")
            raise

    def _normalize_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Normalize numeric columns to a standard scale."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        normalized_data = {}
        for col in numeric_cols:
            normalized_data[col] = (df[col] - df[col].mean()) / df[col].std()
        return normalized_data

    def _encode_categorical_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Encode categorical columns using one-hot encoding."""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        encoded_data = {}
        for col in categorical_cols:
            encoded_data[col] = pd.get_dummies(df[col]).to_dict()
        return encoded_data

    def _handle_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Handle missing values using appropriate strategies."""
        filled_data = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # Fill numeric columns with mean
        for col in numeric_cols:
            filled_data[col] = df[col].fillna(df[col].mean())

        # Fill categorical columns with mode
        for col in categorical_cols:
            filled_data[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')

        return filled_data.to_dict()

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        self.logger.info("Data agent cleaned up")