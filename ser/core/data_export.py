"""Data export module for exporting task results in various formats."""

from typing import Dict, Any, List, Optional
import json
import csv
from datetime import datetime
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from fpdf import FPDF
import os
import shutil

class ExportFormat(Enum):
    """Supported export formats."""
    CSV = 'csv'
    JSON = 'json'
    PDF = 'pdf'
    EXCEL = 'xlsx'

@dataclass
class ExportConfig:
    """Configuration for data export."""
    format: ExportFormat
    output_dir: Optional[Path] = None
    filename_prefix: str = 'export'
    include_metadata: bool = True
    compress_output: bool = False

class DataExporter:
    """Handles exporting data in various formats."""

    def __init__(self, output_dir: Path = None):
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir or Path.cwd() / 'exports'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.offline_queue: List[Dict[str, Any]] = []

    def export_task_results(self, task_data: Dict[str, Any], config: ExportConfig) -> Optional[Path]:
        """Export task results in the specified format."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{config.filename_prefix}_{timestamp}.{config.format.value}"
            output_path = self.output_dir / filename

            result = None
            if config.format == ExportFormat.JSON:
                result = self._export_json(task_data, output_path)
            elif config.format == ExportFormat.CSV:
                result = self._export_csv(task_data, output_path)
            elif config.format == ExportFormat.PDF:
                result = self._export_pdf(task_data, output_path)
            elif config.format == ExportFormat.EXCEL:
                result = self._export_excel(task_data, output_path)
            else:
                raise ValueError(f"Unsupported export format: {config.format}")

            if result and config.compress_output:
                return self._compress_output(result)

            return result

        except Exception as e:
            self.logger.error(f"Failed to export data: {str(e)}")
            self._queue_export(task_data, config)
            return None

    def _export_json(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Export data in JSON format."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Data exported to JSON: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {str(e)}")
            raise

    def _export_csv(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Export data in CSV format."""
        try:
            flattened_data = self._flatten_dict(data)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(flattened_data.keys())
                writer.writerow(flattened_data.values())
            
            self.logger.info(f"Data exported to CSV: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
            raise

    def _export_pdf(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Export data in PDF format."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "Task Results", ln=True, align='C')
            pdf.ln(10)

            # Add content
            pdf.set_font("Arial", size=12)
            flattened_data = self._flatten_dict(data)
            for key, value in flattened_data.items():
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(50, 10, f"{key}:", ln=False)
                pdf.set_font("Arial", size=12)
                pdf.cell(140, 10, str(value), ln=True)

            pdf.output(str(output_path))
            self.logger.info(f"Data exported to PDF: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to export PDF: {str(e)}")
            raise

    def _export_excel(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Export data in Excel format."""
        try:
            import pandas as pd
            flattened_data = self._flatten_dict(data)
            df = pd.DataFrame([flattened_data])
            df.to_excel(output_path, index=False)
            self.logger.info(f"Data exported to Excel: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {str(e)}")
            raise

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten a nested dictionary."""
        items: List = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _compress_output(self, file_path: Path) -> Path:
        """Compress the output file."""
        try:
            output_zip = file_path.with_suffix('.zip')
            shutil.make_archive(str(file_path.with_suffix('')), 'zip', file_path.parent, file_path.name)
            os.remove(file_path)
            return output_zip
        except Exception as e:
            self.logger.error(f"Failed to compress output: {str(e)}")
            return file_path

    def _queue_export(self, task_data: Dict[str, Any], config: ExportConfig) -> None:
        """Queue export task for offline processing."""
        self.offline_queue.append({
            'task_data': task_data,
            'config': config.__dict__,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info("Export task queued for offline processing")

    def process_offline_queue(self) -> None:
        """Process queued export tasks."""
        queued_tasks = self.offline_queue.copy()
        self.offline_queue.clear()

        for task in queued_tasks:
            try:
                config = ExportConfig(**task['config'])
                self.export_task_results(task['task_data'], config)
            except Exception as e:
                self.logger.error(f"Failed to process offline export: {str(e)}")
                self.offline_queue.append(task)

    def cleanup(self) -> None:
        """Cleanup temporary files and resources."""
        try:
            # Process any remaining offline tasks
            self.process_offline_queue()
            self.logger.info("Data exporter cleaned up")
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return [format.value for format in ExportFormat]

    def clean_old_exports(self, max_age_days: int = 7) -> None:
        """Clean up old export files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            for file_path in self.output_dir.glob('*.*'):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    self.logger.info(f"Deleted old export file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to clean old exports: {str(e)}")