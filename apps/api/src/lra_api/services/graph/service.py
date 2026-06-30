"""Knowledge graph extraction and query service."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from neo4j import GraphDatabase

from lra_api.core.config import get_settings


@dataclass
class EntityRelation:
    """Extracted relation triple."""

    source: str
    relation: str
    target: str


class GraphService:
    """Neo4j-backed graph operations."""

    def __init__(self) -> None:
        settings = get_settings()
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def extract_relations(self, text: str) -> list[EntityRelation]:
        """Extract best-effort entity relations from text using lightweight heuristics."""
        entities = re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", text)
        top_entities = [entity for entity, _ in Counter(entities).most_common(20)]
        relations: list[EntityRelation] = []

        for idx in range(len(top_entities) - 1):
            relations.append(
                EntityRelation(
                    source=top_entities[idx],
                    relation="RELATED_TO",
                    target=top_entities[idx + 1],
                )
            )
        return relations

    def upsert_document_graph(self, document_id: str, text: str) -> int:
        """Upsert extracted entities and relations into graph."""
        triples = self.extract_relations(text)

        with self.driver.session() as session:
            for triple in triples:
                session.run(
                    """
                    MERGE (a:Entity {name: $source})
                    MERGE (b:Entity {name: $target})
                    MERGE (a)-[r:RELATED_TO {document_id: $document_id}]->(b)
                    SET r.relation = $relation
                    """,
                    source=triple.source,
                    target=triple.target,
                    relation=triple.relation,
                    document_id=document_id,
                )

        return len(triples)

    def query(self, query_text: str, limit: int) -> dict[str, list[dict[str, str]]]:
        """Query subgraph by partial entity match."""
        with self.driver.session() as session:
            records = session.run(
                """
                MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
                WHERE toLower(a.name) CONTAINS toLower($query_text)
                   OR toLower(b.name) CONTAINS toLower($query_text)
                RETURN a.name AS source, b.name AS target, r.relation AS relation
                LIMIT $limit
                """,
                query_text=query_text,
                limit=limit,
            )
            edges = [
                {"source": record["source"], "target": record["target"], "relation": record["relation"]}
                for record in records
            ]

        node_set = {edge["source"] for edge in edges} | {edge["target"] for edge in edges}
        nodes = [{"id": node, "label": node, "kind": "entity"} for node in sorted(node_set)]
        return {"nodes": nodes, "edges": edges}

    def close(self) -> None:
        """Close Neo4j driver."""
        self.driver.close()
