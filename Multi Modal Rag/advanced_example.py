import sys
import json
from pathlib import Path

from rag_pipeline import MultiModalRAGPipeline
from utils import FileUtils, TextUtils, PerformanceUtils, ReportGenerator, ValidationUtils


def setup_sample_environment():
    sample_dir = Path("./sample_media")
    sample_dir.mkdir(exist_ok=True)

    files_created = []

    csv_file = sample_dir / "products.csv"
    if not csv_file.exists():
        with open(csv_file, 'w') as f:
            f.write("product_id,name,category,price,quantity\n")
            f.write("1,Laptop,Electronics,1200,5\n")
            f.write("2,Monitor,Electronics,300,10\n")
            f.write("3,Keyboard,Electronics,50,20\n")
            f.write("4,Desk Chair,Furniture,200,8\n")
            f.write("5,Office Desk,Furniture,400,3\n")
        files_created.append(str(csv_file))

    inventory_file = sample_dir / "inventory.csv"
    if not inventory_file.exists():
        with open(inventory_file, 'w') as f:
            f.write("item,warehouse_a,warehouse_b,warehouse_c\n")
            f.write("Electronics,100,150,75\n")
            f.write("Furniture,50,60,40\n")
            f.write("Accessories,200,180,220\n")
        files_created.append(str(inventory_file))

    return str(sample_dir), files_created


def main():
    print("\n" + "=" * 100)
    print("Advanced Multi-Modal RAG Pipeline Demonstration")
    print("=" * 100)

    print("\n1. Environment Setup")
    print("-" * 100)

    sample_dir, created_files = setup_sample_environment()
    print(f"Sample Media Directory: {sample_dir}")
    print(f"Files Created: {len(created_files)}")
    for file_path in created_files:
        print(f"  - {file_path}")

    print("\n2. File Validation")
    print("-" * 100)

    validation = ValidationUtils.validate_directory(sample_dir)
    print(f"Directory Valid: {validation.get('valid')}")
    print(f"Total Items: {validation.get('total_items')}")
    print(f"Supported Files: {validation.get('supported_files')}")
    print(f"Unsupported Files: {validation.get('unsupported_files')}")

    print("\n3. Supported Files Analysis")
    print("-" * 100)

    supported_files = FileUtils.get_supported_files(sample_dir)
    print(f"Supported Files Found: {len(supported_files)}")

    for file_path in supported_files:
        file_size = FileUtils.get_file_size_mb(file_path)
        print(f"  - {Path(file_path).name} ({file_size:.2f} MB)")

    print("\n4. Performance Estimation")
    print("-" * 100)

    if supported_files:
        avg_size = sum(FileUtils.get_file_size_mb(f) for f in supported_files) / len(supported_files)
        time_estimate = PerformanceUtils.estimate_indexing_time(
            len(supported_files),
            avg_size
        )

        print(f"Files to Index: {len(supported_files)}")
        print(f"Average File Size: {avg_size:.2f} MB")
        print(f"Estimated Indexing Time: {time_estimate['estimated_time']}")
        print(f"Time per File: {time_estimate['per_file_seconds']:.2f}s")

    print("\n5. RAG Pipeline Initialization")
    print("-" * 100)

    pipeline = MultiModalRAGPipeline(use_llm=False)
    print("Multi-Modal RAG Pipeline initialized (LLM disabled for demo)")

    print("\n6. Indexing Phase")
    print("-" * 100)

    indexing_result = pipeline.index_directory(sample_dir)

    print(f"Indexing Results:")
    print(f"  Total Files: {indexing_result['total_files']}")
    print(f"  Successfully Indexed: {indexing_result['successfully_indexed']}")
    print(f"  Total Chunks Created: {indexing_result['total_chunks_created']}")
    print(f"  Media Type Distribution:")
    for media_type, count in indexing_result['media_type_breakdown'].items():
        print(f"    - {media_type}: {count}")

    if indexing_result['failed_files']:
        print(f"  Failed Files:")
        for failed in indexing_result['failed_files']:
            print(f"    - {failed['file']}: {failed['error']}")

    report_path = ReportGenerator.generate_indexing_report(indexing_result)
    print(f"\nIndexing Report saved to: {report_path}")

    print("\n7. Query Processing Phase")
    print("-" * 100)

    queries = [
        "What electronics are in stock?",
        "Show me the furniture products",
        "Tell me about inventory levels",
        "What are the most expensive items?"
    ]

    retrieval_results = []

    for idx, query in enumerate(queries, 1):
        print(f"\nQuery {idx}: {query}")
        print("-" * 60)

        result = pipeline.query(query, top_k=3, use_llm=False)

        print(f"  Retrieved Documents: {result['retrieved_documents']}")
        print(f"  Media Types: {', '.join(result['media_types'])}")
        print(f"  Source Files: {', '.join([Path(f).name for f in result['source_files']])}")
        print(f"  Confidence Scores: {[f'{score:.4f}' for score in result['confidence_scores']]}")

        context_preview = TextUtils.truncate_text(result['context'], max_length=150)
        print(f"  Context Preview: {context_preview}")

        if result.get('answer'):
            answer_preview = TextUtils.truncate_text(result['answer'], max_length=150)
            print(f"  Answer Preview: {answer_preview}")

        retrieval_results.append({
            "query": query,
            "documents": result['retrieved_documents'],
            "media_types": result['media_types'],
            "confidence_scores": result['confidence_scores']
        })

    print("\n8. Media Type Filtering")
    print("-" * 100)

    media_filtered_query = "products and pricing"
    print(f"Query: {media_filtered_query}")
    print(f"Filter: table")
    print("-" * 60)

    result = pipeline.query_by_media_type(
        media_filtered_query,
        "table",
        top_k=3,
        use_llm=False
    )

    print(f"  Retrieved Documents: {result['retrieved_documents']}")
    print(f"  Context: {TextUtils.truncate_text(result['context'], 150)}")

    print("\n9. Summarization")
    print("-" * 100)

    summary_query = "inventory and products"
    print(f"Query: {summary_query}")
    print("-" * 60)

    summary_result = pipeline.summarize(summary_query, top_k=5, use_llm=False)

    print(f"  Retrieved Documents: {summary_result['retrieved_documents']}")
    print(f"  Media Types Found: {', '.join(summary_result['media_types'])}")

    summary_preview = TextUtils.truncate_text(summary_result['summary'], 150)
    print(f"  Summary Preview: {summary_preview}")

    print("\n10. Analysis")
    print("-" * 100)

    analysis_query = "what products do we have"
    print(f"Query: {analysis_query}")
    print("-" * 60)

    analysis_result = pipeline.analyze(analysis_query, top_k=5, use_llm=False)

    print(f"  Retrieved Documents: {analysis_result['retrieved_documents']}")
    print(f"  Media Types: {', '.join(analysis_result['media_types'])}")

    analysis_preview = TextUtils.truncate_text(analysis_result['analysis'], 150)
    print(f"  Analysis Preview: {analysis_preview}")

    print("\n11. Comparison")
    print("-" * 100)

    comparison_query = "compare items"
    print(f"Query: {comparison_query}")
    print("-" * 60)

    comparison_result = pipeline.compare(comparison_query, top_k=5, use_llm=False)

    print(f"  Retrieved Documents: {comparison_result['retrieved_documents']}")
    print(f"  Comparison Sources: {', '.join([Path(f).name for f in comparison_result['comparison_sources']])}")

    comparison_preview = TextUtils.truncate_text(comparison_result['comparison'], 150)
    print(f"  Comparison Preview: {comparison_preview}")

    print("\n12. Retrieval Statistics")
    print("-" * 100)

    stats = pipeline.retriever.get_retrieval_statistics()

    print(f"Vector Store Statistics:")
    print(f"  Total Documents: {stats['vector_store']['total_documents']}")
    print(f"  Total Chunks: {stats['vector_store']['total_chunks']}")
    print(f"  Embedding Dimension: {stats['vector_store']['embedding_dimension']}")
    print(f"  Media Type Distribution: {stats['vector_store']['media_type_distribution']}")

    print(f"\nRetriever Configuration:")
    print(f"  Embedding Model: {stats['retriever_info']['embedding_model']}")
    print(f"  Embedding Dimension: {stats['retriever_info']['embedding_dimension']}")

    print("\n13. Report Generation")
    print("-" * 100)

    retrieval_report = ReportGenerator.generate_retrieval_report(retrieval_results)
    print(f"Retrieval Report saved to: {retrieval_report}")

    health_report = ReportGenerator.generate_system_health_report(stats)
    print(f"Health Report saved to: {health_report}")

    pipeline_config = pipeline.export_pipeline_config()
    print(f"Pipeline Config saved to: {pipeline_config}")

    print("\n14. Configuration Export")
    print("-" * 100)

    with open(pipeline_config, 'r') as f:
        config = json.load(f)

    print(f"Embedding Model: {config['embedding_model']}")
    print(f"Chunk Size: {config['chunk_size']}")
    print(f"Chunk Overlap: {config['chunk_overlap']}")
    print(f"LLM Enabled: {config['llm_enabled']}")

    print("\n" + "=" * 100)
    print("Advanced Multi-Modal RAG Pipeline Demonstration Complete")
    print("=" * 100)

    print("\n📊 Generated Reports:")
    print(f"  1. Indexing Report: {report_path}")
    print(f"  2. Retrieval Report: {retrieval_report}")
    print(f"  3. Health Report: {health_report}")
    print(f"  4. Pipeline Config: {pipeline_config}")

    print("\n📁 Sample Data Directory:")
    print(f"  {sample_dir}")

    print("\n✅ All demonstrations completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
