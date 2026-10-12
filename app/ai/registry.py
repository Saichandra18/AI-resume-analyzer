from __future__ import annotations

import inspect

from typing import Callable, Type

from .providers import LLMProvider


class LLMProviderRegistry:
    """
    Dynamic registry for LLM provider implementations.

    Providers can be registered directly as provider classes or
    through custom factory callables when a provider requires
    specialized construction logic.
    """

    def __init__(self):
        self._providers: dict[str, Type[LLMProvider]] = {}
        self._factories: dict[str, Callable[..., LLMProvider]] = {}

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise ValueError("Provider name must be a string.")

        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("Provider name must not be empty.")

        return normalized

    @staticmethod
    def _validate_provider_class(
        provider_class: Type[LLMProvider],
    ) -> None:
        if not isinstance(provider_class, type):
            raise TypeError(
                "Provider must implement LLMProvider."
            )

        if not issubclass(provider_class, LLMProvider):
            raise TypeError(
                "Provider must implement LLMProvider."
            )

    def register(
        self,
        name: str,
        provider_class: Type[LLMProvider],
    ) -> None:
        normalized_name = self._normalize_name(name)

        self._validate_provider_class(provider_class)

        if normalized_name in self._providers:
            raise ValueError(
                f"Provider already registered: {normalized_name}"
            )

        self._providers[normalized_name] = provider_class

    def register_factory(
        self,
        name: str,
        provider_class: Type[LLMProvider],
        factory: Callable[..., LLMProvider],
    ) -> None:
        """
        Register a provider with a custom construction callable.

        The provider class remains available through get(), while
        create() uses the supplied factory.
        """

        normalized_name = self._normalize_name(name)

        self._validate_provider_class(provider_class)

        if not callable(factory):
            raise TypeError(
                "Provider factory must be callable."
            )

        if (
            normalized_name in self._providers
            or normalized_name in self._factories
        ):
            raise ValueError(
                f"Provider already registered: {normalized_name}"
            )

        self._providers[normalized_name] = provider_class
        self._factories[normalized_name] = factory

    def get(self, name: str):
        normalized_name = self._normalize_name(name)
        return self._providers.get(normalized_name)

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def create(self, name: str, **kwargs) -> LLMProvider:
        normalized_name = self._normalize_name(name)

        provider_class = self._providers.get(normalized_name)

        if provider_class is None:
            raise ValueError(f"Unknown LLM provider: {name}")

        factory = self._factories.get(normalized_name)

        if factory is not None:
            provider = factory(**kwargs)
        else:
            # Pass only supported keyword arguments to custom classes
            # unless their constructor accepts arbitrary keyword arguments.
            signature = inspect.signature(provider_class)
            parameters = signature.parameters.values()

            accepts_kwargs = any(
                parameter.kind is inspect.Parameter.VAR_KEYWORD
                for parameter in parameters
            )

            if not accepts_kwargs:
                accepted_names = set(signature.parameters)

                kwargs = {
                    key: value
                    for key, value in kwargs.items()
                    if key in accepted_names
                }

            provider = provider_class(**kwargs)

        if not isinstance(provider, LLMProvider):
            raise TypeError(
                "Provider factory must return an LLMProvider."
            )

        return provider
