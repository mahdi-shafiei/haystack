# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
from typing import Any, Dict, Iterator, Optional

from haystack.lazy_imports import LazyImport
from haystack.tracing import Span, Tracer
from haystack.tracing import utils as tracing_utils

with LazyImport("Run 'pip install ddtrace'") as ddtrace_import:
    import ddtrace
    from ddtrace.trace import Span as ddSpan
    from ddtrace.trace import Tracer as ddTracer

_COMPONENT_NAME_KEY = "haystack.component.name"
_COMPONENT_TYPE_KEY = "haystack.component.type"
_COMPONENT_RUN_OPERATION_NAME = "haystack.component.run"


class DatadogSpan(Span):
    def __init__(self, span: "ddSpan") -> None:
        self._span = span

    def set_tag(self, key: str, value: Any) -> None:
        """
        Set a single tag on the span.

        :param key: the name of the tag.
        :param value: the value of the tag.
        """
        coerced_value = tracing_utils.coerce_tag_value(value)
        self._span.set_tag(key, coerced_value)

    def raw_span(self) -> Any:
        """
        Provides access to the underlying span object of the tracer.

        :return: The underlying span object.
        """
        return self._span

    def get_correlation_data_for_logs(self) -> Dict[str, Any]:
        """Return a dictionary with correlation data for logs."""
        raw_span = self.raw_span()
        if not raw_span:
            return {}

        # https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/#no-standard-library-logging
        trace_id, span_id = (str((1 << 64) - 1 & raw_span.trace_id), raw_span.span_id)

        return {
            "dd.trace_id": trace_id,
            "dd.span_id": span_id,
            "dd.service": ddtrace.config.service or "",
            "dd.env": ddtrace.config.env or "",
            "dd.version": ddtrace.config.version or "",
        }


class DatadogTracer(Tracer):
    def __init__(self, tracer: "ddTracer") -> None:
        ddtrace_import.check()
        self._tracer = tracer

    @staticmethod
    def _get_span_resource_name(operation_name: str, tags: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Get the resource name for the Datadog span.
        """
        if operation_name == _COMPONENT_RUN_OPERATION_NAME and tags:
            component_type = tags.get(_COMPONENT_TYPE_KEY, "")
            component_name = tags.get(_COMPONENT_NAME_KEY, "")

            return f"{component_type}: {component_name}"

        return None

    @contextlib.contextmanager
    def trace(
        self, operation_name: str, tags: Optional[Dict[str, Any]] = None, parent_span: Optional[Span] = None
    ) -> Iterator[Span]:
        """Activate and return a new span that inherits from the current active span."""
        resource_name = self._get_span_resource_name(operation_name, tags)

        with self._tracer.trace(name=operation_name, resource=resource_name) as span:
            custom_span = DatadogSpan(span)
            if tags:
                custom_span.set_tags(tags)

            yield custom_span

    def current_span(self) -> Optional[Span]:
        """Return the current active span"""
        current_span = self._tracer.current_span()
        if current_span is None:
            return None

        return DatadogSpan(current_span)
