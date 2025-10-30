import asyncio
import asyncpg
import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', '20'))
        self.min_connections = int(os.getenv('DB_MIN_CONNECTIONS', '5'))
        
    async def initialize(self):
        """Initialize the connection pool"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                print("No DATABASE_URL found, skipping pool initialization")
                return
                
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=self.min_connections,
                max_size=self.max_connections,
                command_timeout=60,
                server_settings={
                    'jit': 'off'  # Disable JIT for faster connection times
                }
            )
            print(f"Database pool initialized with {self.min_connections}-{self.max_connections} connections")
        except Exception as e:
            print(f"Failed to initialize database pool: {e}")
    
    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            print("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            raise Exception("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE command"""
        async with self.get_connection() as conn:
            return await conn.execute(command, *args)
    
    async def execute_batch(self, command: str, args_list: List[tuple]) -> None:
        """Execute a batch of commands"""
        async with self.get_connection() as conn:
            await conn.executemany(command, args_list)

# Global pool instance
db_pool = DatabasePool()