"""
Example usage of TrapNZDatabase
"""
import asyncio
from uuid import UUID
from database import TrapNZDatabase
from logging_config import setup_default_logging, get_logger

# Set up logging
setup_default_logging()
logger = get_logger(__name__)

async def main():
    # Initialize database
    db = TrapNZDatabase(db_path="trapnz.db")
    
    # Example line UUIDs (replace with actual UUIDs from your Trap.NZ project)
    line_uuids = [
        UUID("your-line-uuid-1"),
        UUID("your-line-uuid-2"),
        # Add more line UUIDs as needed
    ]
    
    logger.info("🪤 Trap.NZ Data Retrieval")
    logger.info("=" * 40)
    
    try:
        # Retrieve all data (will use cache if less than 1 hour old)
        result = await db.retrieve_lines_traps_and_records(line_uuids)
        
        # Force refresh from API (ignores cache)
        # result = await db.retrieve_lines_traps_and_records(line_uuids, force_refresh=True)
        
        logger.info("✅ Data retrieval completed!")
        logger.info(f"   Lines: {len(result['lines'])}")
        logger.info(f"   Traps: {len(result['traps'])}")
        logger.info(f"   Records: {len(result['records'])}")
        
        # Show some details
        if result['lines']:
            logger.info("📋 Lines retrieved:")
            for line in result['lines']:
                logger.info(f"   • {line.name} (UUID: {line.uuid})")
        
        if result['traps']:
            logger.info("🪤 Traps retrieved:")
            for trap in result['traps']:
                logger.info(f"   • {trap.name} - {trap.trap_type} (Battery: {trap.battery_voltage}V)")
        
        if result['records']:
            logger.info("📊 Latest records:")
            for record in result['records']:
                logger.info(f"   • {record.trap.name}: {record.event} - {record.status} ({record.date})")
        
        logger.info(f"💾 All data has been stored in SQLite database: {db.db_path}")
        
        # Example of using individual retrieval methods
        logger.info("\n📊 Individual Data Retrieval Examples:")
        
        # Get all lines from database
        all_lines = db.get_all_lines()
        logger.info(f"   Total lines in database: {len(all_lines)}")
        
        # Get all traps from database
        all_traps = db.get_all_traps()
        logger.info(f"   Total traps in database: {len(all_traps)}")
        
        # Get all trap records from database
        all_records = db.get_all_trap_records()
        logger.info(f"   Total trap records in database: {len(all_records)}")
        
        # Get multiple records for a specific trap
        if all_traps:
            sample_trap = all_traps[0]
            trap_records = db.get_trap_records_by_trap(sample_trap.uuid, limit=10)
            logger.info(f"   Records for trap {sample_trap.name}: {len(trap_records)}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
