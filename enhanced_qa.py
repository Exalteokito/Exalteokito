import json
import os
from typing import List, Dict, Optional, Tuple
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.readers import ExtractiveReader
from haystack import Pipeline, Document
from web_search import WebSearchQA

class EnhancedQAPipeline:
    def __init__(self, serpapi_key: Optional[str] = None):
        self.web_search = WebSearchQA(serpapi_key)
        self.static_pipeline = None
        self.web_enabled = bool(serpapi_key or os.getenv('SERPAPI_KEY'))

        # Initialize static knowledge base pipeline
        self._load_static_pipeline()

    def _load_static_pipeline(self):
        """Load the static knowledge base pipeline."""
        try:
            with open("models/documents.json", "r", encoding="utf-8") as f:
                doc_dicts = json.load(f)
            docs = [Document.from_dict(d) for d in doc_dicts]

            document_store = InMemoryDocumentStore()
            document_store.write_documents(docs)

            retriever = InMemoryBM25Retriever(document_store=document_store)
            reader = ExtractiveReader(model="deepset/roberta-base-squad2")

            pipe = Pipeline()
            pipe.add_component("retriever", retriever)
            pipe.add_component("reader", reader)
            pipe.connect("retriever", "reader")

            self.static_pipeline = pipe
            print(f"Loaded static knowledge base with {len(docs)} documents")

        except Exception as e:
            print(f"Error loading static pipeline: {e}")
            self.static_pipeline = None

    def _is_real_time_query(self, query: str) -> bool:
        """Determine if a query needs real-time information."""
        real_time_keywords = [
            'latest', 'recent', 'current', 'today', 'now', 'update', 'news',
            'score', 'game', 'match', 'season', 'trade', 'injury', 'status',
            'performance', 'stats', 'record', 'standing', 'rank', 'schedule'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in real_time_keywords)

    def _combine_answers(self, static_answers: List, web_answers: List) -> List[Dict]:
        """Combine and rank answers from static and web sources."""
        combined = []

        # Add static answers with source attribution
        for ans in static_answers:
            if ans.score >= 0.5:  # Only include reasonably confident answers
                combined.append({
                    "answer": ans.data,
                    "score": ans.score * 0.9,  # Slight penalty for older data
                    "source": "knowledge_base",
                    "meta": ans.document.meta if ans.document else {},
                    "context": ans.document.content[:250] + "..." if ans.document else ""
                })

        # Add web answers with higher priority for real-time queries
        for ans in web_answers:
            if ans.score >= 0.4:  # Lower threshold for web results
                combined.append({
                    "answer": ans.data,
                    "score": ans.score,  # No penalty for current data
                    "source": "web_search",
                    "meta": ans.document.meta if ans.document else {},
                    "context": ans.document.content[:250] + "..." if ans.document else ""
                })

        # Sort by score (highest first)
        combined.sort(key=lambda x: x['score'], reverse=True)

        return combined[:5]  # Return top 5 answers

    def ask_question(self, question: str, use_web: bool = None) -> Dict:
        """
        Answer a question using hybrid approach (static KB + web search).

        Args:
            question: The question to answer
            use_web: Force web search on/off. If None, auto-determine based on query.
        """
        if use_web is None:
            use_web = self._is_real_time_query(question) and self.web_enabled

        static_answers = []
        web_answers = []

        # Get answers from static knowledge base
        if self.static_pipeline:
            try:
                result = self.static_pipeline.run({
                    "retriever": {"query": question, "top_k": 10},
                    "reader": {"query": question, "top_k": 3}
                })
                static_answers = result.get("reader", {}).get("answers", [])
            except Exception as e:
                print(f"Static pipeline error: {e}")

        # Get answers from web search if enabled
        if use_web and self.web_enabled:
            try:
                # Search web and create documents
                web_docs = self.web_search.search_and_create_docs(question, num_results=5)

                if web_docs:
                    # Create temporary pipeline for web documents
                    web_store = InMemoryDocumentStore()
                    web_store.write_documents(web_docs)

                    web_retriever = InMemoryBM25Retriever(document_store=web_store)
                    web_reader = ExtractiveReader(model="deepset/roberta-base-squad2")

                    web_pipe = Pipeline()
                    web_pipe.add_component("retriever", web_retriever)
                    web_pipe.add_component("reader", web_reader)
                    web_pipe.connect("retriever", "reader")

                    # Get web answers
                    web_result = web_pipe.run({
                        "retriever": {"query": question, "top_k": 10},
                        "reader": {"query": question, "top_k": 3}
                    })
                    web_answers = web_result.get("reader", {}).get("answers", [])

            except Exception as e:
                print(f"Web search error: {e}")

        # Combine and format results
        if not static_answers and not web_answers:
            return {
                "answer": "Sorry, I couldn't find any answer related to that topic in my knowledge base or web search.",
                "score": 0,
                "source": "none",
                "meta": {},
                "context": "",
                "all_answers": []
            }

        combined_answers = self._combine_answers(static_answers, web_answers)

        if not combined_answers:
            return {
                "answer": "Sorry, I couldn't find any answer related to that topic in my knowledge base or web search.",
                "score": 0,
                "source": "none",
                "meta": {},
                "context": "",
                "all_answers": []
            }

        best_answer = combined_answers[0]

        return {
            "answer": best_answer["answer"],
            "score": best_answer["score"],
            "source": best_answer["source"],
            "meta": best_answer["meta"],
            "context": best_answer["context"],
            "all_answers": combined_answers
        }

# Test function
if __name__ == "__main__":
    # Test the enhanced pipeline
    qa = EnhancedQAPipeline()

    # Test static query
    print("Testing static knowledge base query:")
    result = qa.ask_question("What happened between LeBron James and Stephen A. Smith?", use_web=False)
    print(f"Answer: {result['answer']}")
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.2f}")
    print()

    # Test web search query (will show warning if no API key)
    print("Testing web search query:")
    result = qa.ask_question("What is the latest news about LeBron James?", use_web=True)
    print(f"Answer: {result['answer']}")
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.2f}")