import requests
from requests import Response
from typing import Optional, Dict, Any, List, Union

# --- HELPER FUNCTIONS ---


def _fetch_work_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Performs the initial search in Open Library by title.

    Args:
        title (str): The book title to search for.

    Returns:
        Optional[Dict[str, Any]]: The first document found ('docs'[0]) or None.
    """
    search_url: str = "https://openlibrary.org/search.json"
    try:
        # We set a timeout to prevent the app from hanging if the API is down
        response: Response = requests.get(
            search_url, params={"title": title}, timeout=5
        )

        if response.status_code == 200:
            data: Dict[str, Any] = response.json()
            if data.get("numFound", 0) > 0:
                return data["docs"][0]
    except Exception:
        # Silently fail on connection errors to avoid crashing the view
        return None
    return None


def _fetch_edition_data(edition_key: str) -> Optional[Dict[str, Any]]:
    """
    Fetches specific details for an edition using its OLID key.

    Args:
        edition_key (str): The Open Library ID (e.g., 'OL123M').

    Returns:
        Optional[Dict[str, Any]]: The JSON response or None.
    """
    edition_url: str = f"https://openlibrary.org/books/{edition_key}.json"
    try:
        response: Response = requests.get(edition_url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None


def _resolve_publisher(work_doc: Dict[str, Any]) -> str:
    """
    Determines the best available publisher name using a two-step strategy.

    Strategy 1: Try to fetch the specific edition data (more accurate).
    Strategy 2: Fallback to the general work data list.

    Args:
        work_doc (Dict[str, Any]): The initial data dictionary from the search.

    Returns:
        str: The publisher name or "No especificada".
    """
    publisher_clean: str = "No especificada"

    # Strategy 1: Search by specific Edition Key (OLID)
    # This provides a single, accurate publisher for the cover image shown.
    edition_key: Optional[str] = work_doc.get("cover_edition_key")

    if edition_key:
        edition_data = _fetch_edition_data(edition_key)
        if edition_data:
            publishers: List[str] = edition_data.get("publishers", [])
            if publishers:
                return publishers[0]

    # Strategy 2: Fallback to the general 'Work' document
    # If the API call above failed or had no data, use the generic list.
    if publisher_clean == "No especificada":
        publisher_list_backup: List[str] = work_doc.get("publisher", [])
        if publisher_list_backup:
            publisher_clean = publisher_list_backup[0]

    return publisher_clean


def _format_rating(rating: Optional[float]) -> Union[float, str]:
    """
    Formats the rating to 1 decimal place or returns a default message.
    """
    if rating:
        return round(float(rating), 1)
    return "Sin calificación"


# --- MAIN ORCHESTRATOR ---


def get_book_data_from_api(title: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves and processes book metadata from the Open Library API.

    This function acts as an orchestrator, calling helper functions to:
    1. Search for the book.
    2. Resolve the best possible publisher data (handling multiple API calls).
    3. Format ratings and extract metadata.

    Args:
        title (str): The title of the book to search for.

    Returns:
        Optional[Dict[str, Any]]: A dictionary with keys:
            - 'ratings_average'
            - 'first_publish_year'
            - 'publisher'
            - 'cover_id'
        Returns None if the book is not found or API fails.
    """
    # 1. Find the book
    work_doc = _fetch_work_by_title(title)

    if not work_doc:
        return None

    # 2. Process individual data fields
    rating_val = work_doc.get("ratings_average", None)
    rating_clean = _format_rating(rating_val)

    # This step might trigger a second API call internally
    publisher_clean = _resolve_publisher(work_doc)

    first_year: Union[int, str] = work_doc.get("first_publish_year", "Desconocido")
    cover_id: Optional[int] = work_doc.get("cover_i")

    # 3. Return clean dictionary
    return {
        "ratings_average": rating_clean,
        "first_publish_year": first_year,
        "publisher": publisher_clean,
        "cover_id": cover_id,
    }
