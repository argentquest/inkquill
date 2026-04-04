"""
Patient Session Assembly Service.
Takes a patient profile, queries their active providers, executes them securely,
and creates the daily patient content cards.
"""

import logging
import importlib
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.care_circle import (
    CareCirclePatientProfile,
    CareCirclePatientContentCard,
    CareCircleProviderCatalog,
    CareCircleProviderPatientConfig
)
from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)

def _to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return "".join(x.title() for x in components)

def get_provider_class(provider_key: str) -> type[BaseCareCircleProvider] | None:
    """Dynamically loads and returns the standardized provider class."""
    module_path = f"app.services.care_circle.providers.{provider_key}.provider"
    try:
        module = importlib.import_module(module_path)
        class_name = _to_camel_case(provider_key) + "Provider"
        provider_class = getattr(module, class_name, None)
        
        if provider_class and issubclass(provider_class, BaseCareCircleProvider):
            return provider_class
    except Exception as e:
        logger.error(f"Failed to load provider class {provider_key}: {e}")
    return None

async def assemble_daily_patient_session(db: AsyncSession, patient_id: int) -> bool:
    """
    Core executor orchestrating the day's patient assembly.
    1. Fetches patient.
    2. Identifies enabled, patient_visible providers.
    3. Runs them concurrently or sequentially.
    4. Overwrites the active CareCirclePatientContentCard rows.
    """
    patient = await db.get(CareCirclePatientProfile, patient_id)
    if not patient or patient.access_state == "archived":
        return False
        
    # Find all globally enabled, patient-safe catalog items
    catalog_query = select(CareCircleProviderCatalog).where(
        CareCircleProviderCatalog.enabled == True,
        CareCircleProviderCatalog.patient_visible == True
    )
    catalog_items = (await db.execute(catalog_query)).scalars().all()
    
    # Grab custom configs or disabled states from the family config mappings
    config_query = select(CareCircleProviderPatientConfig).where(
        CareCircleProviderPatientConfig.patient_id == patient_id
    )
    user_configs = (await db.execute(config_query)).scalars().all()
    config_map = {c.provider_key: c for c in user_configs}
    
    # Select which providers are running for this session
    # For Sprint 2, if no custom config exists, we default allow if they are marked patient_visible
    active_providers = []
    for item in catalog_items:
        conf = config_map.get(item.provider_key)
        if conf and not conf.is_enabled:
            continue # Family explicitly disabled it
            
        cls = get_provider_class(item.provider_key)
        if cls:
            # We enforce patient-safe flag at execution mount explicitly!
            if cls.is_safe_for_patient:
                # Mount the provider with any custom family dict
                cfg_dict = conf.custom_parameters if conf else {}
                instance = cls(patient_config=cfg_dict)
                active_providers.append((item.provider_key, item.display_order, instance))
            else:
                logger.warning(f"Skipping {item.provider_key} as it is structurally flagged unsafe for patients.")
    
    if not active_providers:
        logger.warning(f"No active safe providers found for patient {patient_id}.")
        return False
        
    # Execute the active providers
    # In production with LLMs, this should be asyncio.gather, but sequential is fine for stabilization
    generated_cards = []
    for p_key, order, provider_instance in active_providers:
        result = await provider_instance.execute(patient)
        
        # Construct the normalized rendering card details from the Provider payload
        # Standard payloads return {'text': '...', 'subheading': '...', 'type': '...'}
        data = result.get("data", {})
        title = data.get("subheading") or data.get("title") or "Daily Highlight"
        body = data.get("text") or data.get("message") or str(data)
        
        card = CareCirclePatientContentCard(
            patient_id=patient_id,
            provider_key=p_key,
            title=title,
            body=body,
            card_kind=p_key, # Use provider key as kind mapping
            display_order=order,
            is_active=True
        )
        generated_cards.append(card)
        
    if generated_cards:
        # Clear out yesterday's active cards
        await db.execute(
            delete(CareCirclePatientContentCard)
            .where(CareCirclePatientContentCard.patient_id == patient_id)
        )
        # Flush to prevent unique constraint cascades
        await db.flush()
        
        # Save new cards
        for card in generated_cards:
            db.add(card)
            
        await db.commit()
    
    return True
