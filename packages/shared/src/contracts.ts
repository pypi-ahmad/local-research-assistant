export interface SourceRef {
  document_id: string;
  chunk_id: string;
  source_name: string;
  page_number?: number;
}

export interface Citation extends SourceRef {
  quote: string;
}

export interface ChunkHit extends SourceRef {
  score: number;
  semantic_score: number;
  lexical_score: number;
  text: string;
}

export interface RagAnswer {
  answer: string;
  citations: Citation[];
}

export interface GraphNode {
  id: string;
  label: string;
  kind: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
}
