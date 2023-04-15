"""Config flow for gamma_light integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    wrapped_entity_config_entry_title,
)

from .const import DOMAIN, GAMMA, MAX_BRIGHTNESS, MIN_BRIGHTNESS


def applicable_light_entity_selector(
    hass: HomeAssistant,
) -> vol.Schema:
    """Return an entity selector which allows selection of valid dimmable lights."""

    # Excludes our own entities and lights that have already been wrapped
    entity_registry = er.async_get(hass)
    exclude_entities = [
        entry.entity_id
        for entry in entity_registry.entities.values()
        if entry.domain == Platform.LIGHT
        and (
            entry.platform == DOMAIN
            or entry.hidden_by == er.RegistryEntryHider.INTEGRATION
        )
    ]

    entity_selector_config = selector.EntitySelectorConfig(
        domain=Platform.LIGHT, exclude_entities=exclude_entities
    )

    return selector.EntitySelector(entity_selector_config)


async def generate_config_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Generate config schema."""
    return vol.Schema(
        {
            vol.Required(CONF_ENTITY_ID): applicable_light_entity_selector(
                handler.parent_handler.hass,
            ),
            vol.Required(MIN_BRIGHTNESS, default=0): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=99,
                    step=1,
                    unit_of_measurement="percent",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(MAX_BRIGHTNESS, default=100): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100,
                    step=1,
                    unit_of_measurement="percent",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(GAMMA, default=1): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1,
                    max=5.0,
                    step=0.1,
                    unit_of_measurement="Gamma",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
        }
    )


async def generate_options_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Generate options schema."""
    return vol.Schema(
        {
            vol.Required(MIN_BRIGHTNESS, default=0): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=99,
                    step=1,
                    unit_of_measurement="percent",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(MAX_BRIGHTNESS, default=100): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100,
                    step=1,
                    unit_of_measurement="percent",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(GAMMA, default=1): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.3,
                    max=3.0,
                    step=0.1,
                    unit_of_measurement="Gamma",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
        }
    )


CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(generate_config_schema)
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(generate_options_schema)
}


class GammaLightConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config flow for gamma_light."""

    VERSION = 2
    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title and hide the wrapped entity if registered."""
        # Hide the wrapped entry if registered
        registry = er.async_get(self.hass)
        entity_entry = registry.async_get(options[CONF_ENTITY_ID])
        if entity_entry is not None and not entity_entry.hidden:
            registry.async_update_entity(
                options[CONF_ENTITY_ID], hidden_by=er.RegistryEntryHider.INTEGRATION
            )

        return wrapped_entity_config_entry_title(self.hass, options[CONF_ENTITY_ID])
