# sensor.py
import logging
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, UnitOfTime, UnitOfVolumetricFlux
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import ATTR_ATTRIBUTION, DOMAIN, SENSORS
from .coordinator import BuienalarmDataUpdateCoordinator
from .entity import BuienalarmEntity, BuienalarmSensorEntity
from .sensor_types import SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


old_SENSOR_DESCRIPTIONS: Final[list[SensorEntityDescription]] = [
    SensorEntityDescription(
        key="nowcastmessage",
        name="Buienalarm",
        icon="mdi:weather-pouring",
    ),
    SensorEntityDescription(
        key="mycastmessage",
        name="My Buienalarm",
        icon="mdi:weather-pouring",
    ),
    SensorEntityDescription(
        key="precipitationrate_now_description",
        name="Neerslag omschrijving",
        icon="mdi:weather-rainy",
    ),
    SensorEntityDescription(
        key="precipitationtype_now",
        name="Soort neerslag",
        icon="mdi:weather-pouring",
    ),
    SensorEntityDescription(
        key="next_precipitation",
        name="Next precipitation",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
    SensorEntityDescription(
        key="precipitation_duration",
        name="Duur neerslag",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
    SensorEntityDescription(
        key="precipitationrate_now",
        name="Neerslag",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="precipitationrate_hour",
        name="Neerslag komend uur",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="precipitationrate_total",
        name="Neerslag verwacht",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Buienalarm sensors from config entry."""
    _LOGGER.debug("[SENSOR SETUP] Setting up Buienalarm sensors for %s", config_entry.unique_id)
    _LOGGER.debug("[SENSOR SETUP] async_setup_entry called for %s", config_entry.entry_id)

    coordinator: BuienalarmDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug(
        "[SENSOR SETUP] Reusing existing coordinator from hass.data (last_update_success=%s)",
        coordinator.last_update_success,
    )

    # old_sensors
    sensors1: list[SensorEntity] = [
        BuienalarmSensor(coordinator, config_entry, **sensor_data)
        for sensor_data in SENSORS
    ]

    sensors2 = [
        BuienalarmSensorEntity(coordinator, config_entry, description,
                               location_id=config_entry.data.get("location_id", "unknown"),
                               location_name=config_entry.data.get("location_name", "unknown"))
        for description in SENSOR_DESCRIPTIONS
    ]

    sensors3: list[SensorEntity] = [
        BuienalarmSensorEntity(coordinator, config_entry, description,
                               location_id=config_entry.data.get("location_id", "unknown"),
                               location_name=config_entry.data.get("location_name", "unknown"))
        for description in SENSOR_DESCRIPTIONS
    ]

    sensors4 = [
        BuienalarmSensor(coordinator, config_entry, description.name, description.native_unit_of_measurement,
                         description.icon, description.device_class, description.state_class, description.key)
        for description in SENSOR_DESCRIPTIONS
    ]

    sensors5: list[SensorEntity] = [
        BuienalarmTestSensor(coordinator, config_entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    _LOGGER.debug("[SENSOR SETUP] Adding %d sensors", len(sensors1))
    async_add_entities(sensors1, update_before_add=False)  # sensors van de oude setup *werkt*
    # async_add_entities(sensors2, update_before_add=True)  # sensors van SENSOR_DESCRIPTIONS *raw Nowcast Message*
    # async_add_entities(sensors3, update_before_add=True)  # sensors van SENSOR_DESCRIPTIONS met SensorEntity
    # async_add_entities(sensors4, update_before_add=True)  # sensors van SENSOR_DESCRIPTIONS met BuienalarmSensor
    # async_add_entities(sensors5, update_before_add=True)  # sensors van SENSOR_DESCRIPTIONS met BuienalarmTestSensor
    _LOGGER.debug("[SENSOR SETUP] %d sensors added", len(sensors1))


    return True


# class BuienalarmTestSensor(CoordinatorEntity[BuienalarmDataUpdateCoordinator], SensorEntity):
class BuienalarmTestSensor(BuienalarmEntity, SensorEntity):
    def __init__(
        self,
        coordinator: BuienalarmDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
    ):
        # super().__init__(coordinator)
        super().__init__(coordinator, config_entry, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"

    # @property
    # def strict_native_value(self) -> int | float | str | datetime | None:
    #     """Return the value for the sensor."""
    #     return self.coordinator.data.get(self.entity_description.key)

    @property
    def native_value(self) -> object:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            _LOGGER.debug("[TEST SENSOR] No data available for %s", self.entity_description.key)
            return None
        # return self.coordinator.data.get(self.entity_description.key)
        value = self.get_data(self.entity_description.key)
        return value


class BuienalarmSensor(BuienalarmEntity, SensorEntity):
    _LOGGER.debug("[SENSOR SETUP] BuienalarmSensor created")

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: BuienalarmDataUpdateCoordinator,
        config_entry: ConfigEntry,
        name: str,
        unit_of_measurement: str,
        icon: str,
        device_class: str,
        state_class: str,
        key: str,
    ) -> None:
        _LOGGER.debug("[SENSOR ENTITY] __init__ for %s", name)
        super().__init__(coordinator, config_entry, key)
        self.entry_name = config_entry.data.get(CONF_NAME, "no_name")
        self.entry_place = config_entry.data.get("place", None)
        self._name = name
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._device_class = device_class
        self._state_class = state_class
        self._key = key
        _LOGGER.debug("[SENSOR ENTITY] Initialized sensor: %s", self.name)

    @property
    def available(self) -> bool:
        """Geeft aan of de sensor data heeft opgehaald."""
        if not self.coordinator.last_update_success:
            return False
        if not self.coordinator.data:
            return False
        if not isinstance(self.coordinator.data, dict):
            _LOGGER.debug(
                "[SENSOR ENTITY] Coordinator data is not a dict: %s",
                type(self.coordinator.data).__name__,
            )
            return False
        # if self.coordinator.data.get(self._key, None) is None:
        #     return False
        return True

    @property
    def new_available(self) -> bool:
        """Geeft aan of de sensor data heeft opgehaald."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get(self._key) is not None
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.name.lower().replace(' ', '_')}"

    @property
    def name(self) -> str:
        """Return the sensor name."""
        if self.entry_place:
            return f"{self._name} {self.entry_place}"
        return self._name

    # StateType = str | int | float | None
    @property
    def native_value(self) -> StateType:
        """Return the current value of the sensor."""
        # extra check to ensure data is available
        if not self.coordinator.last_update_success or self.coordinator.data is None:
            _LOGGER.debug("[SENSOR ENTITY] No data available for key: %s", self._key)
            return None  # STATE_UNAVAILABLE  # STATE_UNKNOWN  # of None
        value = self.get_data(self._key)
        _LOGGER.debug("[SENSOR ENTITY] native_value for %s: %s", self._key, value)

        # Validate the value to match allowed StateType
        if isinstance(value, (str, int, float)) or value is None:
            return value

        _LOGGER.warning(
            "[SENSOR ENTITY] Unexpected value type for key '%s': %s (%s)",
            self._key,
            value,
            type(value).__name__,
        )
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def state_class(self) -> str | None:
        """Return the state class of this entity, if any."""
        return self._state_class

    @property
    def device_class(self) -> str | None:
        """Return the device class of this entity, if any."""
        return self._device_class

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        """
        Return the additional state attributes for Home Assistant.

        This property replaces the deprecated `device_state_attributes`.
        It includes metadata such as the last update time and any extra
        contextual data relevant to the entity.
        """
        try:
            attributes: dict[str, object] = {}
            # attributes["api_last_updated"] = self._api_last_updated.isoformat() if self._api_last_updated else None
            # Add API timestamp from coordinator
            if getattr(self.coordinator, "api_last_updated", None):
                attributes["api_last_updated"] = self.coordinator.api_last_updated.isoformat()

            # Only include precipitation_data for one specific sensor
            if self._key == "precipitationrate_total":
                attributes["precipitation_data"] = getattr(self, "data_points_as_list", [])

            attributes["attribution"] = ATTR_ATTRIBUTION
            return attributes
        except Exception as exc:
            _LOGGER.error("Failed to build extra_state_attributes: %s", exc)
            return {}
