from typing import Optional, Callable, Awaitable, Any, TypeAlias

import httpx

Json: TypeAlias = dict[str, Any] | list[dict[str, Any]]
Tool: TypeAlias = Callable[..., Awaitable[Json]]


def json_placeholder_tools() -> list[Tool]:
    base_uri = "https://jsonplaceholder.typicode.com/"

    async def _request(method: str, endpoint: str, **kwargs) -> Json:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, base_uri + endpoint, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_users(user_id: Optional[int] = None) -> Json:
        """
        ユーザーを取得する。

        Args:
            user_id (Optional[int]): 取得するユーザーのID。指定しない場合は全ユーザーを取得。
        """
        endpoint = f"users/{user_id}" if user_id else "users"
        return await _request("GET", endpoint)

    async def get_posts(post_id: Optional[int] = None, user_id: Optional[int] = None) -> Json:
        """
        投稿を取得する。

        Args:
            post_id (Optional[int]): 取得する投稿のID。指定しない場合は全投稿を取得。
            user_id (Optional[int]): 特定ユーザーの投稿を取得するためのユーザーID。
        """
        params = {}

        if user_id:
            params["userId"] = user_id

        if post_id:
            params["id"] = post_id

        return await _request("GET", "posts", params=params)

    return [get_users, get_posts]

