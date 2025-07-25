#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/utils/async_utils.py
"""Async utility functions."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

from loguru import logger

from ..types import ProgressCallback

T = TypeVar("T")


async def run_async(
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """Run a sync function in an async context.
    
    Args:
        func: Function to run
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def gather_with_progress(
    tasks: list[Awaitable[T]],
    progress_callback: ProgressCallback | None = None,
    description: str = "Processing",
) -> list[T]:
    """Gather tasks with progress reporting.
    
    Args:
        tasks: List of async tasks
        progress_callback: Optional progress callback
        description: Progress description
        
    Returns:
        List of task results
    """
    total = len(tasks)
    completed = 0
    results = []
    
    async def track_task(task: Awaitable[T]) -> T:
        nonlocal completed
        try:
            result = await task
            completed += 1
            
            if progress_callback:
                progress = completed / total
                message = f"{description}: {completed}/{total}"
                progress_callback(progress, message)
                
            return result
        except Exception as e:
            logger.error(f"Task failed: {e}")
            raise
    
    # Create tracked tasks
    tracked_tasks = [track_task(task) for task in tasks]
    
    # Gather results
    return await asyncio.gather(*tracked_tasks)


async def run_with_timeout(
    coro: Awaitable[T],
    timeout_seconds: float,
    timeout_message: str = "Operation timed out",
) -> T:
    """Run a coroutine with timeout.
    
    Args:
        coro: Coroutine to run
        timeout_seconds: Timeout in seconds
        timeout_message: Message for timeout error
        
    Returns:
        Coroutine result
        
    Raises:
        TimeoutError: If operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(timeout_message) from None


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> T:
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Positional arguments
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry
        **kwargs: Keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Exception: Last exception if all attempts fail
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                    f"Retrying in {current_delay:.1f}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(f"All {max_attempts} attempts failed")
    
    raise last_exception


class AsyncContextManager:
    """Base class for async context managers."""
    
    async def __aenter__(self) -> AsyncContextManager:
        """Enter the context."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context."""
        pass


class AsyncPool:
    """Async task pool with concurrency limit."""
    
    def __init__(self, max_concurrent: int = 4) -> None:
        """Initialize pool.
        
        Args:
            max_concurrent: Maximum concurrent tasks
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks: list[asyncio.Task[Any]] = []
    
    async def submit(self, coro: Awaitable[T]) -> asyncio.Task[T]:
        """Submit a task to the pool.
        
        Args:
            coro: Coroutine to run
            
        Returns:
            Task object
        """
        async def run_with_semaphore() -> T:
            async with self.semaphore:
                return await coro
        
        task = asyncio.create_task(run_with_semaphore())
        self.tasks.append(task)
        return task
    
    async def gather(self) -> list[Any]:
        """Wait for all tasks to complete.
        
        Returns:
            List of task results
        """
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        return results
    
    async def shutdown(self) -> None:
        """Cancel all pending tasks."""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()