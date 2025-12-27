import asyncio
import sys
from app.database import async_session_maker
from app.models import Problem
from sqlalchemy import select, delete


async def seed_problems(clear_existing: bool = False):
    async with async_session_maker() as session:
        if clear_existing:
            await session.execute(delete(Problem))
            await session.commit()
            print("Cleared existing problems")

        # Check if problems already exist
        result = await session.execute(select(Problem))
        existing = result.scalar_one_or_none()
        if existing and not clear_existing:
            print("Problems already seeded. Use --clear to reseed.")
            return

        problem = Problem(
            title="Clone Even Numbers",
            description="""
Given an array of integers, clone all even numbers in-place. The array has enough space at the end to accommodate the cloned numbers.

For example:
- `[2, -1]` should become `[2, 2]` (clone the even number 2)
- `[1, 2, 3, 4, 5, 6, -1, -1, -1]` should become `[1, 2, 2, 3, 4, 4, 5, 6, 6]`

The `-1` values represent empty spaces that should be filled with cloned even numbers.

Write a function `clone_even_numbers(arr)` that modifies the array in-place and returns it.
            """.strip(),
            category="arrays-and-strings",
            function_name="clone_even_numbers",
            starter_code="""def clone_even_numbers(arr):
    # Your code here
    pass
""",
            test_code="""from arrays_and_strings.clone_even_numbers import clone_even_numbers


def test_empty_array():
    assert clone_even_numbers([]) == []


def test_single_odd_number():
    assert clone_even_numbers([1]) == [1]


def test_single_even_number():
    assert clone_even_numbers([2, -1]) == [2, 2]


def test_all_odd_numbers():
    assert clone_even_numbers([1, 3, 5]) == [1, 3, 5]


def test_all_even_numbers():
    assert clone_even_numbers([2, 4, 6, -1, -1, -1]) == [2, 2, 4, 4, 6, 6]


def test_mixed_numbers():
    assert clone_even_numbers([1, 2, 3, 4, 5, 6, -1, -1, -1]) == [1, 2, 2, 3, 4, 4, 5, 6, 6]
""",
        )

        session.add(problem)
        await session.commit()
        print(f"Seeded problem: {problem.title}")


if __name__ == "__main__":
    clear = "--clear" in sys.argv or "-c" in sys.argv
    asyncio.run(seed_problems(clear_existing=clear))
