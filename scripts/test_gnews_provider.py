"""Test the GNews provider for a specific patient."""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.services.care_circle.providers.gnews.provider import GnewsProvider


async def main():
    patient_id = 17

    async with async_session_local() as db:
        patient = await db.get(CareCirclePatientProfile, patient_id)
        if not patient:
            print(f"Patient {patient_id} not found!")
            return

        print(f"Testing GNews provider for patient {patient_id}:")
        print(f"  Name: {getattr(patient, 'display_name', 'N/A')}")
        print(f"  Preferred language: {getattr(patient, 'preferred_language', 'N/A')}")
        print(f"  Country: {getattr(patient, 'country', 'N/A')}")
        print()

        provider = GnewsProvider()
        result = await provider.execute(patient)

        print(f"Success: {result.get('success')}")
        print(f"Provider key: {result.get('provider_key')}")

        data = result.get("data", {})
        articles = data.get("articles", [])
        print(f"Articles returned: {len(articles)}")
        print()

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source_name', 'N/A')}")
            print(f"   Description: {article.get('description', 'N/A')[:100]}...")
            content = article.get('content', '')
            if content:
                print(f"   Content: {content[:200]}...")
            print()

        if result.get("token_usage"):
            print(f"Token usage: {result['token_usage']}")


if __name__ == "__main__":
    asyncio.run(main())
