"""
Example of using TEST_MODE for development and testing
"""
import asyncio
import os
from uuid import UUID
from .database import TrapNZDatabase
from .test_config import setup_test_environment, create_test_line_data, create_test_trap_data, create_test_record_data
from .logging_config import setup_default_logging, get_logger

async def test_mode_example():
    """Example of using TEST_MODE for testing cache logic"""
    
    # Set up test environment
    setup_test_environment()
    
    # Set up logging
    setup_default_logging()
    logger = get_logger(__name__)
    
    logger.info("🧪 Starting TEST_MODE example")
    
    # Initialize database with test mode
    db = TrapNZDatabase(db_path="test_trapnz.db")
    
    # Add custom test data
    logger.info("📝 Adding custom test data...")
    
    # Add a new test line
    test_line_data = create_test_line_data()
    db.api_facade.add_test_line("test-line-2", test_line_data)
    
    # Add a new test trap
    test_trap_data = create_test_trap_data()
    db.api_facade.add_test_trap("test-line-2", test_trap_data)
    
    # Add a new test record
    test_record_data = create_test_record_data()
    db.api_facade.add_test_record("test-trap-2", test_record_data)
    
    # Test the cache logic with test data
    logger.info("🔄 Testing cache logic...")
    
    # First call - should fetch from "API" (test data)
    logger.info("📡 First call - fetching from test data...")
    result1 = await db.retrieve_lines_traps_and_records([
        UUID("test-line-1"),
        UUID("test-line-2")
    ])
    
    logger.info(f"   Retrieved {len(result1['lines'])} lines")
    logger.info(f"   Retrieved {len(result1['traps'])} traps")
    logger.info(f"   Retrieved {len(result1['records'])} records")
    
    # Second call within 1 hour - should use cache
    logger.info("💾 Second call - should use cache...")
    result2 = await db.retrieve_lines_traps_and_records([
        UUID("test-line-1"),
        UUID("test-line-2")
    ])
    
    logger.info(f"   Retrieved {len(result2['lines'])} lines")
    logger.info(f"   Retrieved {len(result2['traps'])} traps")
    logger.info(f"   Retrieved {len(result2['records'])} records")
    
    # Force refresh - should fetch from "API" again
    logger.info("🔄 Force refresh - fetching from test data again...")
    result3 = await db.retrieve_lines_traps_and_records([
        UUID("test-line-1"),
        UUID("test-line-2")
    ], force_refresh=True)
    
    logger.info(f"   Retrieved {len(result3['lines'])} lines")
    logger.info(f"   Retrieved {len(result3['traps'])} traps")
    logger.info(f"   Retrieved {len(result3['records'])} records")
    
    # Test individual retrieval methods
    logger.info("📊 Testing individual retrieval methods...")
    
    all_lines = db.get_all_lines()
    logger.info(f"   Total lines in database: {len(all_lines)}")
    
    all_traps = db.get_all_traps()
    logger.info(f"   Total traps in database: {len(all_traps)}")
    
    all_records = db.get_all_trap_records()
    logger.info(f"   Total trap records in database: {len(all_records)}")
    
    # Test getting multiple records for a specific trap
    if all_traps:
        sample_trap = all_traps[0]
        trap_records = db.get_trap_records_by_trap(sample_trap.uuid, limit=10)
        logger.info(f"   Records for trap {sample_trap.name}: {len(trap_records)}")
    
    # Clear test data
    logger.info("🧹 Clearing test data...")
    db.api_facade.clear_test_data()
    
    logger.info("✅ TEST_MODE example completed!")

def test_mode_sync_example():
    """Synchronous version for testing without async"""
    
    # Set up test environment
    setup_test_environment()
    
    # Set up logging
    setup_default_logging()
    logger = get_logger(__name__)
    
    logger.info("🧪 Starting synchronous TEST_MODE example")
    
    # Initialize database with test mode
    db = TrapNZDatabase(db_path="test_trapnz_sync.db")
    
    # Test individual retrieval methods (these don't require async)
    logger.info("📊 Testing individual retrieval methods...")
    
    # Add some test data first
    test_line_data = create_test_line_data()
    db.api_facade.add_test_line("test-line-2", test_line_data)
    
    test_trap_data = create_test_trap_data()
    db.api_facade.add_test_trap("test-line-2", test_trap_data)
    
    test_record_data = create_test_record_data()
    db.api_facade.add_test_record("test-trap-2", test_record_data)
    
    # Test database-only methods
    all_lines = db.get_all_lines()
    logger.info(f"   Total lines in database: {len(all_lines)}")
    
    all_traps = db.get_all_traps()
    logger.info(f"   Total traps in database: {len(all_traps)}")
    
    all_records = db.get_all_trap_records()
    logger.info(f"   Total trap records in database: {len(all_records)}")
    
    # Clear test data
    db.api_facade.clear_test_data()
    
    logger.info("✅ Synchronous TEST_MODE example completed!")

if __name__ == "__main__":
    # Run the async example
    asyncio.run(test_mode_example())
    
    # Run the sync example
    test_mode_sync_example()
