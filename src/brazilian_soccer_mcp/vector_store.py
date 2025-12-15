"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: vector_store.py
Description: Vector store implementation using numpy for Brazilian Soccer MCP
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Implement a vector similarity search store for natural language queries
    about Brazilian soccer data. This module provides:
    - Text embedding generation using sentence-transformers
    - Vector storage with metadata
    - Similarity search using cosine similarity
    - Support for semantic queries like "find similar matches"

Architecture:
    Since RuVector is primarily a Rust/JavaScript library, we implement a
    Python-native vector store using:
    - numpy: For efficient vector operations
    - sentence-transformers: For text embeddings
    - scipy: For similarity calculations

    This approach maintains the "use RuVector instead of Neo4j" spirit by:
    - Using vector similarity search instead of graph traversal
    - Storing embeddings for semantic search
    - Supporting hybrid keyword + semantic queries

Vector Indices:
    - matches_index: Embeddings of match descriptions
    - players_index: Embeddings of player information
    - teams_index: Embeddings of team information
=============================================================================
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import os
from pathlib import Path

# Use simpler embedding approach to avoid heavy dependencies
# In production, you would use sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from .models import Match, Player, TeamStats


@dataclass
class VectorEntry:
    """A single entry in the vector store."""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    text: str


class SimpleEmbedder:
    """
    Simple text embedder using TF-IDF-like approach.
    Falls back to this when sentence-transformers isn't available.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vocab: Dict[str, int] = {}
        self._fitted = False

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return text.lower().split()

    def fit(self, texts: List[str]) -> None:
        """Build vocabulary from texts."""
        for text in texts:
            for token in self._tokenize(text):
                if token not in self.vocab:
                    self.vocab[token] = len(self.vocab)
        self._fitted = True

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to vectors using simple bag-of-words + hashing."""
        vectors = []
        for text in texts:
            vec = np.zeros(self.dim)
            tokens = self._tokenize(text)
            for token in tokens:
                # Use hash to map any token to a dimension
                idx = hash(token) % self.dim
                vec[idx] += 1
            # Normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors)


class VectorStore:
    """
    Vector store for semantic search over Brazilian soccer data.

    This implementation provides RuVector-like functionality using numpy
    for vector operations, enabling:
    - Semantic search over matches, players, and teams
    - Similarity-based queries
    - Metadata filtering combined with vector search

    Attributes:
        embedder: Text embedding model
        entries: List of all vector entries
        dimension: Vector dimension
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """
        Initialize the vector store.

        Args:
            model_name: Sentence transformer model name
            dimension: Vector dimension (384 for MiniLM)
        """
        self.dimension = dimension
        self.entries: List[VectorEntry] = []
        self._vectors: Optional[np.ndarray] = None
        self._index_dirty = True

        # Initialize embedder
        if HAS_TRANSFORMERS:
            try:
                self.embedder = SentenceTransformer(model_name)
                self.dimension = self.embedder.get_sentence_embedding_dimension()
            except Exception:
                self.embedder = SimpleEmbedder(dimension)
        else:
            self.embedder = SimpleEmbedder(dimension)

    def _embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        if isinstance(self.embedder, SimpleEmbedder):
            if not self.embedder._fitted:
                self.embedder.fit(texts)
            return self.embedder.encode(texts)
        else:
            return self.embedder.encode(texts)

    def _rebuild_index(self) -> None:
        """Rebuild the vector index."""
        if not self.entries:
            self._vectors = None
        else:
            self._vectors = np.vstack([e.vector for e in self.entries])
        self._index_dirty = False

    def add(self, id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a single entry to the vector store.

        Args:
            id: Unique identifier
            text: Text to embed
            metadata: Associated metadata
        """
        vector = self._embed([text])[0]
        entry = VectorEntry(
            id=id,
            vector=vector,
            metadata=metadata or {},
            text=text,
        )
        self.entries.append(entry)
        self._index_dirty = True

    def add_batch(self, items: List[Tuple[str, str, Dict[str, Any]]]) -> None:
        """
        Add multiple entries efficiently.

        Args:
            items: List of (id, text, metadata) tuples
        """
        if not items:
            return

        texts = [item[1] for item in items]
        vectors = self._embed(texts)

        for (id, text, metadata), vector in zip(items, vectors):
            entry = VectorEntry(
                id=id,
                vector=vector,
                metadata=metadata or {},
                text=text,
            )
            self.entries.append(entry)

        self._index_dirty = True

    def search(
        self,
        query: str,
        k: int = 10,
        filter_fn: Optional[callable] = None,
    ) -> List[Tuple[VectorEntry, float]]:
        """
        Search for similar entries using cosine similarity.

        Args:
            query: Query text
            k: Number of results to return
            filter_fn: Optional function to filter results by metadata

        Returns:
            List of (entry, similarity_score) tuples
        """
        if not self.entries:
            return []

        if self._index_dirty:
            self._rebuild_index()

        # Embed query
        query_vector = self._embed([query])[0]

        # Calculate cosine similarities
        similarities = self._cosine_similarity(query_vector, self._vectors)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1]

        results = []
        for idx in top_indices:
            if len(results) >= k:
                break

            entry = self.entries[idx]

            # Apply filter if provided
            if filter_fn and not filter_fn(entry.metadata):
                continue

            results.append((entry, float(similarities[idx])))

        return results

    def _cosine_similarity(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and all vectors."""
        # Normalize query
        query_norm = query / (np.linalg.norm(query) + 1e-10)

        # Normalize vectors
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
        vectors_norm = vectors / norms

        # Dot product
        return np.dot(vectors_norm, query_norm)

    def index_matches(self, matches: List[Match]) -> None:
        """
        Index matches for semantic search.

        Creates embeddings of match descriptions like:
        "Flamengo vs Fluminense, Brasileirao 2023, Round 15: 2-1"

        Args:
            matches: List of Match objects to index
        """
        items = []
        for i, match in enumerate(matches):
            # Create rich text description
            text_parts = [
                f"{match.home_team} vs {match.away_team}",
                f"score {match.home_goals}-{match.away_goals}",
            ]

            if match.competition:
                text_parts.append(match.competition.value)

            if match.season:
                text_parts.append(f"season {match.season}")

            if match.match_round:
                text_parts.append(f"round {match.match_round}")

            if match.match_date:
                text_parts.append(match.match_date.strftime("%Y-%m-%d"))

            text = ", ".join(text_parts)

            metadata = {
                "type": "match",
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_goals": match.home_goals,
                "away_goals": match.away_goals,
                "competition": match.competition.value if match.competition else None,
                "season": match.season,
                "round": match.match_round,
                "datetime": match.match_date.isoformat() if match.match_date else None,
            }

            items.append((f"match_{i}", text, metadata))

        self.add_batch(items)

    def index_players(self, players: List[Player]) -> None:
        """
        Index players for semantic search.

        Creates embeddings of player descriptions like:
        "Neymar Jr, Brazil, LW, Paris Saint-Germain, Overall 92"

        Args:
            players: List of Player objects to index
        """
        items = []
        for player in players:
            text_parts = [player.name]

            if player.nationality:
                text_parts.append(player.nationality)

            if player.position:
                text_parts.append(player.position)

            if player.club:
                text_parts.append(player.club)

            text_parts.append(f"overall {player.overall}")

            text = ", ".join(text_parts)

            metadata = {
                "type": "player",
                "id": player.id,
                "name": player.name,
                "nationality": player.nationality,
                "position": player.position,
                "club": player.club,
                "overall": player.overall,
                "potential": player.potential,
            }

            items.append((f"player_{player.id}", text, metadata))

        self.add_batch(items)

    def search_matches(
        self,
        query: str,
        k: int = 10,
        competition: Optional[str] = None,
        season: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search matches using natural language query.

        Args:
            query: Natural language query (e.g., "Flamengo vs Corinthians")
            k: Number of results
            competition: Filter by competition
            season: Filter by season

        Returns:
            List of match metadata dictionaries
        """

        def filter_fn(meta: Dict) -> bool:
            if meta.get("type") != "match":
                return False
            if competition and meta.get("competition") != competition:
                return False
            if season and meta.get("season") != season:
                return False
            return True

        results = self.search(query, k=k, filter_fn=filter_fn)
        return [entry.metadata for entry, score in results]

    def search_players(
        self,
        query: str,
        k: int = 10,
        nationality: Optional[str] = None,
        min_overall: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search players using natural language query.

        Args:
            query: Natural language query (e.g., "Brazilian forwards")
            k: Number of results
            nationality: Filter by nationality
            min_overall: Minimum overall rating

        Returns:
            List of player metadata dictionaries
        """

        def filter_fn(meta: Dict) -> bool:
            if meta.get("type") != "player":
                return False
            if nationality:
                player_nat = meta.get("nationality", "").lower()
                if nationality.lower() not in player_nat:
                    return False
            if min_overall and meta.get("overall", 0) < min_overall:
                return False
            return True

        results = self.search(query, k=k, filter_fn=filter_fn)
        return [entry.metadata for entry, score in results]

    def clear(self) -> None:
        """Clear all entries from the store."""
        self.entries = []
        self._vectors = None
        self._index_dirty = True

    @property
    def size(self) -> int:
        """Number of entries in the store."""
        return len(self.entries)

    def save(self, path: str) -> None:
        """
        Save the vector store to disk.

        Args:
            path: Directory path to save to
        """
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save vectors
        if self._index_dirty:
            self._rebuild_index()

        if self._vectors is not None:
            np.save(save_dir / "vectors.npy", self._vectors)

        # Save metadata
        metadata = []
        for entry in self.entries:
            metadata.append({
                "id": entry.id,
                "text": entry.text,
                "metadata": entry.metadata,
            })

        with open(save_dir / "metadata.json", "w") as f:
            json.dump(metadata, f)

    def load(self, path: str) -> None:
        """
        Load the vector store from disk.

        Args:
            path: Directory path to load from
        """
        load_dir = Path(path)

        # Load vectors
        vectors_path = load_dir / "vectors.npy"
        if vectors_path.exists():
            self._vectors = np.load(vectors_path)
        else:
            self._vectors = None

        # Load metadata
        metadata_path = load_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)

            self.entries = []
            for i, item in enumerate(metadata):
                vector = self._vectors[i] if self._vectors is not None else np.zeros(self.dimension)
                entry = VectorEntry(
                    id=item["id"],
                    vector=vector,
                    metadata=item["metadata"],
                    text=item["text"],
                )
                self.entries.append(entry)

        self._index_dirty = False
