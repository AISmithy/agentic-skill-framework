"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from agentic.core.config import get_settings
from agentic.layer1_experience.middleware.auth_middleware import AuthMiddleware
from agentic.layer1_experience.middleware.tracing_middleware import TracingMiddleware
from agentic.layer1_experience.routes import agents, executions, health, skills
from agentic.layer2_orchestration.context_manager import ContextManager
from agentic.layer2_orchestration.skill_router import SkillRouter
from agentic.layer2_orchestration.workflow_engine import WorkflowEngine
from agentic.layer3_skill_library.metadata_catalog import MetadataCatalog
from agentic.layer3_skill_library.registry import get_registry
from agentic.layer4_runtime.executor import SkillExecutor
from agentic.layer4_runtime.resilience.circuit_breaker import CircuitBreakerRegistry
from agentic.layer5_memory.artifact_store import ArtifactStore
from agentic.layer6_governance.approval_workflow import ApprovalWorkflow
from agentic.layer6_governance.audit_log import AuditLog
from agentic.layer6_governance.authz import AuthorizationEngine
from agentic.layer6_governance.policy_engine import PolicyEngine
from agentic.layer6_governance.safety_filters import SafetyFilter
from agentic.layer7_observability.evaluator import ExecutionEvaluator
from agentic.layer7_observability.logger import configure_logging, get_logger
from agentic.layer7_observability.metrics import get_metrics

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize all framework services on startup."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("framework_starting", version=settings.app_version)

    # Initialize DB-backed services
    catalog = MetadataCatalog(db_path=settings.db_path)
    await catalog.initialize()

    audit = AuditLog(db_path=settings.db_path)
    await audit.initialize()

    # Hydrate in-process registry from catalog
    registry = get_registry()
    skills_from_db = await catalog.load_all()
    for skill in skills_from_db:
        try:
            registry.register(skill, overwrite=True)
        except Exception:
            pass
    logger.info("registry_hydrated", skill_count=len(registry))

    # Build executor
    circuit_registry = CircuitBreakerRegistry(
        failure_threshold=settings.circuit_breaker_failure_threshold,
        recovery_timeout_s=settings.circuit_breaker_recovery_timeout_s,
    )
    executor = SkillExecutor(
        registry=registry,
        skill_instances=app.state.skill_instances,
        policy_engine=PolicyEngine(),
        authz=AuthorizationEngine(),
        safety_filter=SafetyFilter(),
        approval_workflow=ApprovalWorkflow(),
        audit_log=audit,
        evaluator=ExecutionEvaluator(),
        circuit_registry=circuit_registry,
        environment=settings.environment,
    )
    app.state.executor = executor

    # Build workflow engine
    router = SkillRouter(registry)
    workflow_engine = WorkflowEngine(
        router=router,
        executor=executor,
        context_manager=ContextManager(),
        artifact_store=ArtifactStore(),
    )
    app.state.workflow_engine = workflow_engine
    app.state.catalog = catalog
    app.state.audit = audit

    logger.info("framework_ready")
    yield

    logger.info("framework_shutting_down")


def create_app(skill_instances: dict | None = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        skill_instances: Map of skill_id → BaseSkill instance.
                         Skills must be registered here to be executable.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # Store skill instances on app state before lifespan runs
    app.state.skill_instances = skill_instances or {}

    # Middleware (order matters: outermost runs first)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(TracingMiddleware)

    # Routes
    app.include_router(health.router)
    app.include_router(skills.router)
    app.include_router(executions.router)
    app.include_router(agents.router)

    @app.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
    async def prometheus_metrics():
        return get_metrics().to_prometheus_text()

    @app.get("/", include_in_schema=False)
    async def root():
        return {"framework": settings.app_name, "version": settings.app_version}

    return app
