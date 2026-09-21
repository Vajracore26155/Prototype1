"""
Prometheus Metrics Exporter
Phase 9: Monitoring and observability
"""
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST
)
from fastapi import Response
from typing import Dict
import psutil
import time


# ============================================================
# Application Metrics
# ============================================================

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

# Audit metrics
audits_total = Counter(
    'audits_total',
    'Total security audits performed',
    ['status', 'framework']
)

audit_duration_seconds = Histogram(
    'audit_duration_seconds',
    'Audit execution duration in seconds',
    ['framework']
)

audit_compliance_score = Histogram(
    'audit_compliance_score',
    'Compliance score distribution',
    ['framework']
)

# Finding metrics
findings_total = Counter(
    'findings_total',
    'Total security findings',
    ['severity', 'category']
)

findings_by_severity = Gauge(
    'findings_by_severity',
    'Current open findings by severity',
    ['severity']
)

# Configuration metrics
configurations_uploaded = Counter(
    'configurations_uploaded_total',
    'Total configurations uploaded',
    ['vendor', 'status']
)

configuration_parsing_duration_seconds = Histogram(
    'configuration_parsing_duration_seconds',
    'Configuration parsing duration',
    ['vendor']
)

# Device metrics
devices_total = Gauge(
    'devices_total',
    'Total devices registered',
    ['vendor', 'status']
)

device_drift_score = Histogram(
    'device_drift_score',
    'Configuration drift score distribution',
    ['device_id']
)

# AI/ML metrics
ai_predictions_total = Counter(
    'ai_predictions_total',
    'Total AI predictions made',
    ['model_type', 'confidence_level']
)

ai_prediction_confidence = Histogram(
    'ai_prediction_confidence',
    'AI prediction confidence scores',
    ['model_type']
)

ai_feedback_total = Counter(
    'ai_feedback_total',
    'Total user feedback on AI predictions',
    ['feedback_type']
)

# Webhook metrics
webhooks_delivered = Counter(
    'webhooks_delivered_total',
    'Total webhooks delivered',
    ['event_type', 'status']
)

webhook_delivery_duration_seconds = Histogram(
    'webhook_delivery_duration_seconds',
    'Webhook delivery duration',
    ['event_type']
)

# Report metrics
reports_generated = Counter(
    'reports_generated_total',
    'Total reports generated',
    ['report_type', 'format']
)

report_generation_duration_seconds = Histogram(
    'report_generation_duration_seconds',
    'Report generation duration',
    ['report_type']
)

# ============================================================
# System Metrics
# ============================================================

# System resources
system_cpu_percent = Gauge(
    'system_cpu_percent',
    'System CPU usage percentage'
)

system_memory_percent = Gauge(
    'system_memory_percent',
    'System memory usage percentage'
)

system_disk_percent = Gauge(
    'system_disk_percent',
    'System disk usage percentage',
    ['mount_point']
)

# Database metrics
database_connections_total = Gauge(
    'database_connections_total',
    'Total database connections'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Application info
app_info = Info(
    'app',
    'Application information'
)

app_info.info({
    'version': '1.0.0',
    'name': 'VAJRA-CORE',
    'environment': 'production'
})


# ============================================================
# Metrics Collection
# ============================================================

class MetricsCollector:
    """
    Collect and update system metrics
    """
    
    @staticmethod
    def collect_system_metrics():
        """Collect system resource metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_percent.set(cpu_percent)
            
            # Memory
            memory = psutil.virtual_memory()
            system_memory_percent.set(memory.percent)
            
            # Disk
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_disk_percent.labels(
                        mount_point=partition.mountpoint
                    ).set(usage.percent)
                except:
                    pass
        
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
    
    @staticmethod
    def record_http_request(
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Record HTTP request metrics"""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if request_size:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
        
        if response_size:
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
    
    @staticmethod
    def record_audit(
        framework: str,
        status: str,
        duration: float,
        compliance_score: float
    ):
        """Record audit metrics"""
        audits_total.labels(
            status=status,
            framework=framework
        ).inc()
        
        audit_duration_seconds.labels(
            framework=framework
        ).observe(duration)
        
        if compliance_score:
            audit_compliance_score.labels(
                framework=framework
            ).observe(compliance_score)
    
    @staticmethod
    def record_finding(severity: str, category: str):
        """Record finding metrics"""
        findings_total.labels(
            severity=severity,
            category=category
        ).inc()
    
    @staticmethod
    def update_findings_gauge(severity_counts: Dict[str, int]):
        """Update current findings gauge"""
        for severity, count in severity_counts.items():
            findings_by_severity.labels(severity=severity).set(count)
    
    @staticmethod
    def record_ai_prediction(
        model_type: str,
        confidence: float,
        confidence_level: str
    ):
        """Record AI prediction metrics"""
        ai_predictions_total.labels(
            model_type=model_type,
            confidence_level=confidence_level
        ).inc()
        
        ai_prediction_confidence.labels(
            model_type=model_type
        ).observe(confidence)


def metrics_endpoint():
    """
    Prometheus metrics endpoint
    
    Returns metrics in Prometheus format
    """
    # Collect current system metrics
    MetricsCollector.collect_system_metrics()
    
    # Generate metrics
    metrics = generate_latest()
    
    return Response(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST
    )
