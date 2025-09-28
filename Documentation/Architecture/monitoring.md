# Operational Procedures and Monitoring

## Table of Contents
- [Monitoring Architecture](#monitoring-architecture)
- [Logging Strategy](#logging-strategy)
- [Performance Monitoring](#performance-monitoring)
- [Alerting and Incident Response](#alerting-and-incident-response)
- [Operational Runbooks](#operational-runbooks)
- [Backup and Disaster Recovery](#backup-and-disaster-recovery)
- [Maintenance Procedures](#maintenance-procedures)

## Monitoring Architecture

The storytelling platform implements comprehensive monitoring across all system layers, providing real-time visibility into application performance, infrastructure health, and user experience.

### Monitoring Stack Overview

```mermaid
graph TB
    subgraph "Application Layer"
        APP[FastAPI Application<br/>- Custom metrics<br/>- Health endpoints<br/>- Performance counters<br/>- Error tracking]
        MIDDLEWARE[Monitoring Middleware<br/>- Request tracing<br/>- User activity<br/>- Performance metrics<br/>- Security events]
    end
    
    subgraph "Infrastructure Layer"
        AZURE_MONITOR[Azure Monitor<br/>- Infrastructure metrics<br/>- Resource utilization<br/>- Network performance<br/>- Service health]
        APP_INSIGHTS[Application Insights<br/>- Application performance<br/>- Dependency tracking<br/>- Exception monitoring<br/>- User analytics]
    end
    
    subgraph "Data Layer"
        LOG_ANALYTICS[Log Analytics<br/>- Centralized logging<br/>- Query and analysis<br/>- Custom dashboards<br/>- Alert rules]
        METRICS_DB[Metrics Database<br/>- Time-series data<br/>- Historical trends<br/>- Capacity planning<br/>- Performance analysis]
    end
    
    subgraph "Alerting Layer"
        ACTION_GROUPS[Action Groups<br/>- Email notifications<br/>- SMS alerts<br/>- Webhook integrations<br/>- Escalation policies]
        ALERT_RULES[Alert Rules<br/>- Threshold monitoring<br/>- Anomaly detection<br/>- Smart alerts<br/>- Suppression rules]
    end
    
    subgraph "Visualization Layer"
        DASHBOARDS[Azure Dashboards<br/>- Real-time metrics<br/>- Custom views<br/>- Executive summaries<br/>- Operational views]
        WORKBOOKS[Azure Workbooks<br/>- Interactive reports<br/>- Trend analysis<br/>- Troubleshooting guides<br/>- Performance reviews]
    end
    
    %% Data flow
    APP --> APP_INSIGHTS
    MIDDLEWARE --> LOG_ANALYTICS
    AZURE_MONITOR --> METRICS_DB
    APP_INSIGHTS --> LOG_ANALYTICS
    
    LOG_ANALYTICS --> ALERT_RULES
    METRICS_DB --> ALERT_RULES
    ALERT_RULES --> ACTION_GROUPS
    
    LOG_ANALYTICS --> DASHBOARDS
    METRICS_DB --> DASHBOARDS
    LOG_ANALYTICS --> WORKBOOKS
    
    %% Styling
    classDef application fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef infrastructure fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef alerting fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef visualization fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class APP,MIDDLEWARE application
    class AZURE_MONITOR,APP_INSIGHTS infrastructure
    class LOG_ANALYTICS,METRICS_DB data
    class ACTION_GROUPS,ALERT_RULES alerting
    class DASHBOARDS,WORKBOOKS visualization
```### K
ey Performance Indicators (KPIs)

#### Application Performance Metrics
- **Response Time**: API endpoint response times (P50, P95, P99)
- **Throughput**: Requests per second and concurrent users
- **Error Rate**: HTTP 4xx and 5xx error percentages
- **Availability**: Service uptime and health check success rates

#### Business Metrics
- **User Engagement**: Active users, session duration, feature usage
- **Content Creation**: Stories created, AI interactions, image generations
- **System Utilization**: AI token usage, storage consumption, database performance
- **Revenue Metrics**: Credit purchases, AI cost efficiency, user retention

## Logging Strategy

### Structured Logging Implementation

#### Application Logging Configuration
```python
# app/core/logging_config.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

def setup_logging(log_level_console: str = "INFO", log_level_file: str = "DEBUG"):
    """Configure structured logging for the application."""
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level_console.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with structured JSON
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(getattr(logging, log_level_file.upper()))
    file_handler.setFormatter(StructuredFormatter())
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

#### Contextual Logging
```python
# app/core/context.py
from contextvars import ContextVar
from typing import Optional

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='[no_request_id]')
user_identifier_var: ContextVar[str] = ContextVar('user_id', default='[anonymous]')

class ContextualLogger:
    """Logger that automatically includes context information."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        extra = self._get_context()
        extra.update(kwargs)
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error message with context and exception info."""
        extra = self._get_context()
        extra.update(kwargs)
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current request context."""
        return {
            'request_id': request_id_var.get(),
            'user_id': user_identifier_var.get()
        }
```

### Log Categories and Levels

#### Security Logs
```python
# Security event logging
security_logger = logging.getLogger("security")

def log_authentication_event(username: str, success: bool, ip_address: str):
    """Log authentication attempts for security monitoring."""
    security_logger.info(
        "Authentication attempt",
        extra={
            'event_type': 'authentication',
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

def log_authorization_failure(user_id: int, resource: str, action: str):
    """Log authorization failures for security analysis."""
    security_logger.warning(
        "Authorization denied",
        extra={
            'event_type': 'authorization_denied',
            'user_id': user_id,
            'resource': resource,
            'action': action
        }
    )
```

#### Business Event Logs
```python
# Business event tracking
business_logger = logging.getLogger("business")

def log_story_creation(user_id: int, story_id: int, world_id: int):
    """Track story creation for analytics."""
    business_logger.info(
        "Story created",
        extra={
            'event_type': 'story_creation',
            'user_id': user_id,
            'story_id': story_id,
            'world_id': world_id,
            'metrics': {
                'creation_time': datetime.utcnow().isoformat()
            }
        }
    )

def log_ai_usage(user_id: int, model_name: str, tokens: int, cost: float):
    """Track AI usage for cost analysis."""
    business_logger.info(
        "AI service used",
        extra={
            'event_type': 'ai_usage',
            'user_id': user_id,
            'model_name': model_name,
            'tokens_used': tokens,
            'cost_usd': cost
        }
    )
```

## Performance Monitoring

### Application Performance Monitoring (APM)

#### Custom Metrics Collection
```python
# app/core/metrics.py
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram, Gauge
import time

class ApplicationMetrics:
    """Custom application metrics collector."""
    
    def __init__(self):
        self.meter = metrics.get_meter(__name__)
        
        # Request metrics
        self.request_counter = self.meter.create_counter(
            name="http_requests_total",
            description="Total HTTP requests",
            unit="1"
        )
        
        self.request_duration = self.meter.create_histogram(
            name="http_request_duration_seconds",
            description="HTTP request duration",
            unit="s"
        )
        
        # Business metrics
        self.story_creation_counter = self.meter.create_counter(
            name="stories_created_total",
            description="Total stories created",
            unit="1"
        )
        
        self.ai_token_usage = self.meter.create_counter(
            name="ai_tokens_used_total",
            description="Total AI tokens consumed",
            unit="1"
        )
        
        # System metrics
        self.active_users_gauge = self.meter.create_gauge(
            name="active_users_current",
            description="Currently active users",
            unit="1"
        )
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        labels = {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code)
        }
        
        self.request_counter.add(1, labels)
        self.request_duration.record(duration, labels)
    
    def record_story_creation(self, user_id: int, world_id: int):
        """Record story creation metrics."""
        self.story_creation_counter.add(1, {
            "user_id": str(user_id),
            "world_id": str(world_id)
        })
    
    def record_ai_usage(self, model_name: str, tokens: int):
        """Record AI token usage."""
        self.ai_token_usage.add(tokens, {
            "model": model_name
        })

# Global metrics instance
app_metrics = ApplicationMetrics()
```

#### Performance Monitoring Middleware
```python
# Performance monitoring middleware
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic performance monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        app_metrics.record_request(
            method=request.method,
            endpoint=str(request.url.path),
            status_code=response.status_code,
            duration=duration
        )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
```

### Database Performance Monitoring

#### Query Performance Tracking
```python
# Database performance monitoring
class DatabaseMetrics:
    """Database performance metrics collector."""
    
    def __init__(self):
        self.meter = metrics.get_meter("database")
        
        self.query_counter = self.meter.create_counter(
            name="database_queries_total",
            description="Total database queries",
            unit="1"
        )
        
        self.query_duration = self.meter.create_histogram(
            name="database_query_duration_seconds",
            description="Database query duration",
            unit="s"
        )
        
        self.connection_pool_gauge = self.meter.create_gauge(
            name="database_connections_active",
            description="Active database connections",
            unit="1"
        )
    
    def record_query(self, operation: str, table: str, duration: float):
        """Record database query metrics."""
        self.query_counter.add(1, {
            "operation": operation,
            "table": table
        })
        
        self.query_duration.record(duration, {
            "operation": operation,
            "table": table
        })

# Database event listener for automatic monitoring
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    
    # Extract operation and table from SQL
    operation = statement.strip().split()[0].upper()
    
    db_metrics.record_query(
        operation=operation,
        table="unknown",  # Could be parsed from SQL
        duration=total
    )

db_metrics = DatabaseMetrics()
```

## Alerting and Incident Response

### Alert Configuration

#### Critical System Alerts
```json
{
  "alertRules": [
    {
      "name": "High Error Rate",
      "description": "Alert when error rate exceeds 5%",
      "severity": "Critical",
      "condition": {
        "query": "requests | where resultCode >= 400 | summarize errorRate = count() * 100.0 / toscalar(requests | count()) by bin(timestamp, 5m)",
        "threshold": 5.0,
        "operator": "GreaterThan",
        "timeAggregation": "Average",
        "evaluationFrequency": "PT1M",
        "windowSize": "PT5M"
      },
      "actions": [
        {
          "actionGroupId": "/subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.Insights/actionGroups/CriticalAlerts"
        }
      ]
    },
    {
      "name": "Database Connection Failure",
      "description": "Alert when database connections fail",
      "severity": "Critical",
      "condition": {
        "query": "exceptions | where type == 'DatabaseConnectionError'",
        "threshold": 1,
        "operator": "GreaterThanOrEqual"
      }
    },
    {
      "name": "High Response Time",
      "description": "Alert when P95 response time exceeds 2 seconds",
      "severity": "Warning",
      "condition": {
        "query": "requests | summarize percentile(duration, 95) by bin(timestamp, 5m)",
        "threshold": 2000,
        "operator": "GreaterThan"
      }
    }
  ]
}
```

#### Business Logic Alerts
```python
# Custom business logic alerts
class BusinessAlertManager:
    """Manages business-specific alerting logic."""
    
    async def check_ai_cost_anomalies(self):
        """Monitor for unusual AI cost spikes."""
        current_hour_cost = await self.get_current_hour_ai_cost()
        average_cost = await self.get_average_hourly_cost()
        
        if current_hour_cost > average_cost * 3:
            await self.send_alert(
                severity="Warning",
                title="AI Cost Spike Detected",
                message=f"Current hour cost: ${current_hour_cost:.2f}, Average: ${average_cost:.2f}"
            )
    
    async def check_user_activity_anomalies(self):
        """Monitor for unusual user activity patterns."""
        failed_logins = await self.get_recent_failed_logins()
        
        if failed_logins > 100:  # Threshold for potential attack
            await self.send_alert(
                severity="Critical",
                title="Potential Brute Force Attack",
                message=f"Detected {failed_logins} failed login attempts in the last hour"
            )
    
    async def send_alert(self, severity: str, title: str, message: str):
        """Send alert through configured channels."""
        alert_data = {
            "severity": severity,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "business_logic"
        }
        
        # Send to monitoring system
        logger.error(f"ALERT: {title}", extra=alert_data)
        
        # Send to external alerting service if configured
        if settings.ALERT_WEBHOOK_URL:
            await self.send_webhook_alert(alert_data)
```

### Incident Response Procedures

#### Automated Response Actions
```python
# Automated incident response
class IncidentResponseSystem:
    """Automated incident response and remediation."""
    
    async def handle_high_error_rate(self, error_rate: float):
        """Respond to high error rate incidents."""
        logger.critical(f"High error rate detected: {error_rate}%")
        
        # Enable additional logging
        await self.increase_log_level("DEBUG")
        
        # Scale up resources if possible
        await self.trigger_auto_scaling()
        
        # Notify on-call team
        await self.page_on_call_team("High error rate detected")
    
    async def handle_database_issues(self):
        """Respond to database connectivity issues."""
        logger.critical("Database connectivity issues detected")
        
        # Check connection pool status
        pool_status = await self.check_connection_pool()
        
        # Attempt connection pool reset
        if pool_status["unhealthy_connections"] > 5:
            await self.reset_connection_pool()
        
        # Enable database query logging
        await self.enable_query_logging()
        
        # Alert database team
        await self.alert_database_team()
    
    async def handle_security_incident(self, incident_type: str, details: dict):
        """Respond to security incidents."""
        logger.critical(f"Security incident: {incident_type}", extra=details)
        
        # Immediate response actions
        if incident_type == "brute_force_attack":
            await self.block_suspicious_ips(details.get("source_ips", []))
        
        elif incident_type == "privilege_escalation":
            await self.lock_affected_accounts(details.get("user_ids", []))
        
        # Alert security team
        await self.alert_security_team(incident_type, details)
        
        # Create incident ticket
        await self.create_incident_ticket(incident_type, details)
```

## Operational Runbooks

### Common Operational Procedures

#### Application Deployment Runbook
```markdown
# Application Deployment Runbook

## Pre-Deployment Checklist
- [ ] Verify all tests pass in CI/CD pipeline
- [ ] Review deployment diff and changes
- [ ] Confirm database migrations are ready
- [ ] Check resource capacity and scaling limits
- [ ] Verify backup systems are operational
- [ ] Notify stakeholders of deployment window

## Deployment Steps
1. **Enable Maintenance Mode** (if required)
   ```bash
   az webapp config appsettings set --name $APP_NAME --resource-group $RG --settings MAINTENANCE_MODE=true
   ```

2. **Deploy Application Code**
   ```bash
   az webapp deployment source config-zip --name $APP_NAME --resource-group $RG --src deployment.zip
   ```

3. **Run Database Migrations**
   ```bash
   az webapp ssh --name $APP_NAME --resource-group $RG --command "cd /home/site/wwwroot && alembic upgrade head"
   ```

4. **Verify Deployment**
   ```bash
   curl -f https://$APP_NAME.azurewebsites.net/health
   ```

5. **Disable Maintenance Mode**
   ```bash
   az webapp config appsettings delete --name $APP_NAME --resource-group $RG --setting-names MAINTENANCE_MODE
   ```

## Post-Deployment Verification
- [ ] Health checks pass
- [ ] Key user journeys work correctly
- [ ] Error rates remain normal
- [ ] Performance metrics are stable
- [ ] Database queries execute successfully

## Rollback Procedure
If issues are detected:
1. **Immediate Rollback**
   ```bash
   az webapp deployment slot swap --name $APP_NAME --resource-group $RG --slot production --target-slot staging
   ```

2. **Database Rollback** (if needed)
   ```bash
   alembic downgrade -1
   ```

3. **Verify Rollback**
   ```bash
   curl -f https://$APP_NAME.azurewebsites.net/health
   ```
```

#### Database Maintenance Runbook
```markdown
# Database Maintenance Runbook

## Regular Maintenance Tasks

### Weekly Tasks
- [ ] Review slow query log
- [ ] Check database size and growth trends
- [ ] Verify backup integrity
- [ ] Review index usage statistics
- [ ] Check for unused indexes

### Monthly Tasks
- [ ] Update database statistics
- [ ] Review and optimize query performance
- [ ] Check for table bloat
- [ ] Review connection pool settings
- [ ] Analyze storage usage patterns

## Performance Optimization

### Identify Slow Queries
```sql
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Check Index Usage
```sql
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

### Monitor Connection Pool
```sql
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;
```

## Backup and Recovery

### Manual Backup
```bash
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Point-in-Time Recovery
```bash
# Restore to specific timestamp
az postgres flexible-server restore --name $NEW_SERVER --resource-group $RG --source-server $SOURCE_SERVER --restore-time "2025-07-14T10:00:00Z"
```
```

## Backup and Disaster Recovery

### Backup Strategy

#### Automated Backup Configuration
```python
# Backup management service
class BackupManager:
    """Manages automated backup operations."""
    
    def __init__(self):
        self.blob_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
    
    async def create_database_backup(self):
        """Create automated database backup."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"db_backup_{timestamp}.sql"
        
        # Create database dump
        dump_command = [
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "--no-password"
        ]
        
        # Execute backup
        result = await asyncio.create_subprocess_exec(
            *dump_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PGPASSWORD": settings.POSTGRES_PASSWORD}
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode == 0:
            # Upload to blob storage
            await self.upload_backup_to_storage(backup_name, stdout)
            logger.info(f"Database backup created: {backup_name}")
        else:
            logger.error(f"Database backup failed: {stderr.decode()}")
    
    async def create_application_backup(self):
        """Create application code and configuration backup."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Backup configuration
        config_backup = {
            "timestamp": timestamp,
            "environment_variables": dict(os.environ),
            "application_settings": await self.get_app_settings(),
            "database_schema_version": await self.get_schema_version()
        }
        
        backup_name = f"app_config_{timestamp}.json"
        await self.upload_backup_to_storage(
            backup_name, 
            json.dumps(config_backup, indent=2).encode()
        )
    
    async def verify_backup_integrity(self, backup_name: str):
        """Verify backup file integrity."""
        try:
            # Download backup
            backup_data = await self.download_backup_from_storage(backup_name)
            
            # Verify SQL backup
            if backup_name.endswith('.sql'):
                return await self.verify_sql_backup(backup_data)
            
            # Verify JSON backup
            elif backup_name.endswith('.json'):
                json.loads(backup_data.decode())
                return True
                
        except Exception as e:
            logger.error(f"Backup verification failed for {backup_name}: {e}")
            return False
```

#### Disaster Recovery Plan
```python
# Disaster recovery procedures
class DisasterRecoveryManager:
    """Manages disaster recovery operations."""
    
    async def initiate_disaster_recovery(self, recovery_point: datetime):
        """Initiate disaster recovery to specified point in time."""
        logger.critical("Disaster recovery initiated")
        
        # Step 1: Assess damage and determine recovery strategy
        damage_assessment = await self.assess_system_damage()
        
        # Step 2: Restore database
        if damage_assessment["database_affected"]:
            await self.restore_database(recovery_point)
        
        # Step 3: Restore application
        if damage_assessment["application_affected"]:
            await self.restore_application(recovery_point)
        
        # Step 4: Verify system integrity
        await self.verify_system_integrity()
        
        # Step 5: Resume normal operations
        await self.resume_normal_operations()
    
    async def restore_database(self, recovery_point: datetime):
        """Restore database to specified point in time."""
        logger.info(f"Restoring database to {recovery_point}")
        
        # Create new database instance from backup
        restore_command = [
            "az", "postgres", "flexible-server", "restore",
            "--name", f"{settings.POSTGRES_SERVER}-recovery",
            "--resource-group", settings.RESOURCE_GROUP,
            "--source-server", settings.POSTGRES_SERVER,
            "--restore-time", recovery_point.isoformat()
        ]
        
        result = await asyncio.create_subprocess_exec(*restore_command)
        await result.wait()
        
        if result.returncode == 0:
            logger.info("Database restore completed successfully")
        else:
            logger.error("Database restore failed")
            raise Exception("Database restore failed")
    
    async def test_disaster_recovery(self):
        """Test disaster recovery procedures without affecting production."""
        logger.info("Starting disaster recovery test")
        
        # Create test environment
        test_env = await self.create_test_environment()
        
        try:
            # Test database restore
            await self.test_database_restore(test_env)
            
            # Test application restore
            await self.test_application_restore(test_env)
            
            # Test system functionality
            await self.test_system_functionality(test_env)
            
            logger.info("Disaster recovery test completed successfully")
            
        finally:
            # Clean up test environment
            await self.cleanup_test_environment(test_env)
```

## Maintenance Procedures

### Scheduled Maintenance

#### System Maintenance Windows
```python
# Maintenance window management
class MaintenanceManager:
    """Manages scheduled maintenance operations."""
    
    async def enter_maintenance_mode(self):
        """Enable maintenance mode for the application."""
        logger.info("Entering maintenance mode")
        
        # Set maintenance flag
        await self.set_app_setting("MAINTENANCE_MODE", "true")
        
        # Update load balancer health check
        await self.update_health_check_response(healthy=False)
        
        # Wait for active requests to complete
        await asyncio.sleep(30)
        
        # Verify no active user sessions
        active_sessions = await self.get_active_session_count()
        if active_sessions > 0:
            logger.warning(f"Still {active_sessions} active sessions during maintenance")
    
    async def exit_maintenance_mode(self):
        """Disable maintenance mode and resume normal operations."""
        logger.info("Exiting maintenance mode")
        
        # Remove maintenance flag
        await self.remove_app_setting("MAINTENANCE_MODE")
        
        # Restore health check
        await self.update_health_check_response(healthy=True)
        
        # Verify system health
        health_status = await self.check_system_health()
        if not health_status["healthy"]:
            logger.error("System health check failed after maintenance")
            raise Exception("System unhealthy after maintenance")
    
    async def perform_routine_maintenance(self):
        """Execute routine maintenance tasks."""
        maintenance_tasks = [
            self.cleanup_old_logs,
            self.optimize_database_indexes,
            self.cleanup_temporary_files,
            self.update_ai_model_cache,
            self.verify_backup_integrity,
            self.check_security_updates
        ]
        
        for task in maintenance_tasks:
            try:
                await task()
                logger.info(f"Maintenance task completed: {task.__name__}")
            except Exception as e:
                logger.error(f"Maintenance task failed: {task.__name__}: {e}")
```

#### Database Maintenance
```python
# Database maintenance procedures
class DatabaseMaintenanceManager:
    """Manages database maintenance operations."""
    
    async def optimize_database_performance(self):
        """Perform database optimization tasks."""
        async with async_session_local() as db:
            # Update table statistics
            await db.execute(text("ANALYZE;"))
            
            # Vacuum tables to reclaim space
            await db.execute(text("VACUUM ANALYZE;"))
            
            # Reindex tables if needed
            await self.reindex_fragmented_tables(db)
            
            # Clean up old data
            await self.cleanup_old_audit_logs(db)
            
            await db.commit()
    
    async def cleanup_old_audit_logs(self, db: AsyncSession):
        """Remove old audit logs to manage database size."""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Clean up old user activities
        result = await db.execute(
            text("DELETE FROM user_activities WHERE created_at < :cutoff"),
            {"cutoff": cutoff_date}
        )
        
        logger.info(f"Cleaned up {result.rowcount} old user activity records")
        
        # Clean up old AI call logs (keep for billing purposes)
        billing_cutoff = datetime.utcnow() - timedelta(days=365)
        result = await db.execute(
            text("DELETE FROM ai_call_logs WHERE created_at < :cutoff"),
            {"cutoff": billing_cutoff}
        )
        
        logger.info(f"Cleaned up {result.rowcount} old AI call log records")
```

---
**Document Information:**
- Last Updated: 2025-07-14
- Version: 1.0.0
- Author: Architecture Team
- Reviewers: Operations Team, SRE Team