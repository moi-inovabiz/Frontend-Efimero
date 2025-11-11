"""
Script para verificar las regiones en la base de datos
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, distinct, func

import sys
sys.path.insert(0, '..')

from app.models.persona_simulada import PersonaSimuladaDB

async def main():
    # Conectar a la base de datos
    engine = create_async_engine('sqlite+aiosqlite:///./personas.db')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Obtener regiones únicas
        result = await session.execute(
            select(distinct(PersonaSimuladaDB.region))
            .order_by(PersonaSimuladaDB.region)
        )
        regiones = [r[0] for r in result.all()]
        
        print("\n" + "="*60)
        print("📍 REGIONES EN LA BASE DE DATOS:")
        print("="*60)
        for region in regiones:
            # Contar personas por región
            count_result = await session.execute(
                select(func.count(PersonaSimuladaDB.id))
                .where(PersonaSimuladaDB.region == region)
            )
            count = count_result.scalar()
            print(f"  • {region}: {count} personas")
        
        print(f"\nTotal: {len(regiones)} regiones únicas")
        print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
