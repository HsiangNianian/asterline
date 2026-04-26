"""Public package exports for Asterline plugin authors and application code."""

from .agent import AgentError, AgentTrace, Guardrail, LLMClient, LLMConfig, ToolRegistry
from .adapter import Adapter
from .runtime import Runtime
from .config import ConfigValidationError
from .context import Context
from .di import Depends, depends
from .event import Event
from .message import Message
from .observability import AuditLogger, RuntimeMetrics
from .middleware import middleware
from .permissions import Permission, adapter_in, allow_all, channel_in, deny_all, group_in, permission, predicate as permission_predicate, superusers, user_in
from .plugin import Plugin, command, event_handler, message_handler
from .rules import (
    FieldCondition,
    FieldOp,
    Rule,
    RuleCase,
    RuleMatch,
    Ruleset,
    adapter_is,
    all_of as all_rules,
    allow as allow_rule,
    any_of as any_rules,
    channel_id_is,
    contains,
    deny as deny_rule,
    detail_type_is,
    endswith,
    event_type_is,
    field,
    fullmatch,
    group_message,
    guild_id_is,
    match_fields,
    none_of,
    platform_is,
    predicate as rule_predicate,
    private_message,
    raw_field,
    regex,
    rule,
    ruleset,
    startswith,
    state_field,
    text_equals,
    user_id_is,
    when_all,
    when_any,
    word_in,
)
from .session import SessionManager
from .state import JsonStateStore, NullStateStore, SqliteStateStore, StateStore

__all__ = [
    "AgentError",
    "AgentTrace",
    "Adapter",
    "AuditLogger",
    "Guardrail",
    "JsonStateStore",
    "LLMClient",
    "LLMConfig",
    "NullStateStore",
    "Permission",
    "Rule",
    "RuntimeMetrics",
    "SessionManager",
    "SqliteStateStore",
    "StateStore",
    "ToolRegistry",
    "Runtime",
    "ConfigValidationError",
    "Context",
    "Depends",
    "Event",
    "Message",
    "FieldCondition",
    "FieldOp",
    "adapter_in",
    "adapter_is",
    "allow_all",
    "allow_rule",
    "all_rules",
    "any_rules",
    "channel_in",
    "Plugin",
    "command",
    "channel_id_is",
    "contains",
    "deny_all",
    "deny_rule",
    "detail_type_is",
    "depends",
    "endswith",
    "event_handler",
    "event_type_is",
    "field",
    "fullmatch",
    "group_in",
    "group_message",
    "guild_id_is",
    "match_fields",
    "middleware",
    "message_handler",
    "none_of",
    "permission",
    "permission_predicate",
    "platform_is",
    "private_message",
    "raw_field",
    "regex",
    "rule",
    "rule_predicate",
    "RuleCase",
    "RuleMatch",
    "Ruleset",
    "ruleset",
    "startswith",
    "state_field",
    "superusers",
    "text_equals",
    "user_id_is",
    "user_in",
    "when_all",
    "when_any",
    "word_in",
]

on_command = command
on_message = message_handler
on_event = event_handler

__all__.extend(["on_command", "on_message", "on_event"])
