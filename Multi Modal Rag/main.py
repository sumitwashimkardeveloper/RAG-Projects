import os
import sys
import json
from pathlib import Path
from typing import List

from indexer import MultiModalIndexer
from retriever import MultiModalRetriever
from vector_store import VectorStore
from config import Config


def create_sample_files():
    sample_dir = Path("./sample_media")
    sample_dir.mkdir(exist_ok=True)

    csv_path = sample_dir / "data.csv"
    if not csv_path.exists():
        with open(csv_path, 'w') as f:
            f.write("name,value,category\n")
            f.write("Item A,100,Category1\n")
            f.write("Item B,200,Category2\n")
            f.write("Item C,150,Category1\n")

    return str(sample_dir)


def main():
    print("=" * 80)
    print("Multi-Modal RAG System")
    print("=" * 80)

    config = Config()
    print(f"\nConfiguration:")
    print(f"  Embedding Model: {config.EMBEDDING_MODEL}")
    print(f"  Embedding Dimension: {config.EMBEDDING_DIMENSION}")
    print(f"  Chunk Size: {config.CHUNK_SIZE}")
    print(f"  Chunk Overlap: {config.CHUNK_OVERLAP}")

    indexer = MultiModalIndexer(use_pinecone=False)
    print("\nInitialized Multi-Modal Indexer (local mode)")

    sample_dir = create_sample_files()
    print(f"\nIndexing directory: {sample_dir}")

    indexing_result = indexer.index_directory(sample_dir)
    print("\nIndexing Results:")
    print(f"  Total Files: {indexing_result['total_files']}")
    print(f"  Successfully Indexed: {indexing_result['successfully_indexed']}")
    print(f"  Total Chunks Created: {indexing_result['total_chunks_created']}")
    print(f"  Media Type Breakdown: {indexing_result['media_type_breakdown']}")

    if indexing_result['failed_files']:
        print(f"  Failed Files:")
        for failed in indexing_result['failed_files']:
            print(f"    - {failed['file']}: {failed['error']}")

    indexed_files = indexer.get_indexed_files()
    print(f"\nIndexed Files ({len(indexed_files)}):")
    for file_path in indexed_files:
        print(f"  - {file_path}")

    stats = indexer.get_indexing_statistics()
    print(f"\nIndexing Statistics:")
    print(f"  Indexed Files: {stats['indexed_files']}")
    print(f"  Total Documents in Vector Store: {stats['vector_store']['total_documents']}")
    print(f"  Total Chunks: {stats['vector_store']['total_chunks']}")
    print(f"  Media Type Distribution: {stats['vector_store']['media_type_distribution']}")

    retriever = MultiModalRetriever(vector_store=indexer.vector_store)
    print("\nInitialized Multi-Modal Retriever")

    queries = [
        "What are the items and their values?",
        "Category1 items",
        "data values 100"
    ]

    print("\n" + "=" * 80)
    print("Retrieval Examples")
    print("=" * 80)

    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)

        result = retriever.retrieve(query, top_k=3)

        print(f"Found {len(result.documents)} relevant documents:")
        print(f"Source Files: {result.source_files}")
        print(f"Media Types: {result.media_types}")

        for idx, doc in enumerate(result.documents, 1):
            print(f"\n  Result {idx}:")
            print(f"    Similarity Score: {doc['similarity']:.4f}")
            print(f"    Media Type: {doc['metadata']['media_type']}")
            print(f"    File: {Path(doc['metadata']['file_path']).name}")
            print(f"    Chunk Index: {doc['metadata']['chunk_index']}")
            print(f"    Content: {doc['content'][:150]}...")

    print("\n" + "=" * 80)
    print("Media Type Filtering")
    print("=" * 80)

    query = "item"
    media_type = "table"

    print(f"\nQuery: {query}")
    print(f"Filter by Media Type: {media_type}")
    print("-" * 40)

    result = retriever.retrieve(query, top_k=3, media_type_filter=media_type)

    if result.documents:
        for idx, doc in enumerate(result.documents, 1):
            print(f"\n  Result {idx}:")
            print(f"    Similarity: {doc['similarity']:.4f}")
            print(f"    Content: {doc['content'][:150]}...")
    else:
        print("No results found for this filter.")

    print("\n" + "=" * 80)
    print("Retrieval with Context")
    print("=" * 80)

    query = "values"
    print(f"\nQuery: {query}")
    print(f"Retrieving with context expansion...")
    print("-" * 40)

    context_result = retriever.retrieve_with_context(query, top_k=2, context_expansion=1)

    print(f"Primary Results: {context_result['total_results']}")

    for idx, result_item in enumerate(context_result['results'], 1):
        print(f"\n  Result {idx}:")
        primary = result_item['primary_result']
        print(f"    Similarity: {primary['similarity']:.4f}")
        print(f"    Content: {primary['content'][:100]}...")

        if result_item['related_chunks']:
            print(f"    Related Chunks: {len(result_item['related_chunks'])}")
            for chunk in result_item['related_chunks']:
                print(f"      - Chunk {chunk['chunk_index']}: {chunk['content'][:80]}...")

    print("\n" + "=" * 80)
    print("Multi-Media Summary")
    print("=" * 80)

    query = "category"
    print(f"\nQuery: {query}")
    print("-" * 40)

    summary = retriever.retrieve_multi_media_summary(query, top_k=3)

    for media_type, type_summary in summary['media_type_summaries'].items():
        print(f"\n  Media Type: {media_type}")
        print(f"    Results Found: {type_summary['count']}")
        print(f"    Combined Text: {type_summary['combined_text'][:150]}...")

    print("\n" + "=" * 80)
    print("File-Based Retrieval")
    print("=" * 80)

    if indexed_files:
        file_to_query = indexed_files[0]
        print(f"\nFile: {file_to_query}")
        print("-" * 40)

        file_result = retriever.retrieve_by_file(file_to_query)

        if file_result.get('status') == 'success':
            print(f"Total Chunks in File: {file_result['total_chunks']}")

            for chunk in file_result['chunks'][:2]:
                print(f"\n  Chunk {chunk['index']}:")
                print(f"    Media Type: {chunk['metadata']['media_type']}")
                print(f"    Content: {chunk['content'][:150]}...")

    print("\n" + "=" * 80)
    print("Cross-Modal Relationships")
    print("=" * 80)

    query = "category"
    print(f"\nQuery: {query}")
    print("-" * 40)

    relationships = retriever.retrieve_cross_modal_relationships(query, top_k=5)

    print(f"Cross-Modal Connections Found: {len(relationships['cross_modal_connections'])}")

    for connection in relationships['cross_modal_connections']:
        print(f"\n  File: {connection['file']}")
        print(f"    Results: {connection['result_count']}")

    print("\n" + "=" * 80)
    print("Indexer Operations")
    print("=" * 80)

    print(f"\nTotal Indexed Files: {len(indexer.get_indexed_files())}")

    export_path = "./index_metadata.json"
    indexer.export_index_metadata(export_path)
    print(f"Exported index metadata to: {export_path}")

    with open(export_path, 'r') as f:
        metadata = json.load(f)
        print(f"\nExported Metadata:")
        print(f"  Indexed Files Count: {len(metadata['indexed_files'])}")
        print(f"  Config - Chunk Size: {metadata['config']['chunk_size']}")
        print(f"  Config - Embedding Model: {metadata['config']['embedding_model']}")

    print("\n" + "=" * 80)
    print("System Statistics")
    print("=" * 80)

    stats = retriever.get_retrieval_statistics()

    print(f"\nVector Store Statistics:")
    print(f"  Total Documents: {stats['vector_store']['total_documents']}")
    print(f"  Total Chunks: {stats['vector_store']['total_chunks']}")
    print(f"  Embedding Dimension: {stats['vector_store']['embedding_dimension']}")
    print(f"  Media Type Distribution: {stats['vector_store']['media_type_distribution']}")

    print(f"\nRetriever Configuration:")
    print(f"  Embedding Model: {stats['retriever_info']['embedding_model']}")
    print(f"  Embedding Dimension: {stats['retriever_info']['embedding_dimension']}")

    print("\n" + "=" * 80)
    print("Multi-Modal RAG System Demonstration Complete")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
