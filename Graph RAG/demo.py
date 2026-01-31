import os
import tempfile
from document_loader import document_loader
from graph_builder import graph_builder
from query_engine import query_engine
from answer_generator import answer_generator
from graph_db import graph_db

def create_sample_documents() -> list:
    sample_docs = [
        (
            "sample_doc_1.txt",
            """Apple Inc. is a technology company founded by Steve Jobs and Steve Wozniak.
            The company is headquartered in Cupertino, California.
            Apple produces iPhones, MacBooks, and iPads.
            Tim Cook is the current CEO of Apple.
            Apple Park is the headquarters of Apple in Cupertino."""
        ),
        (
            "sample_doc_2.txt",
            """Microsoft is a software company founded by Bill Gates and Paul Allen.
            Satya Nadella is the CEO of Microsoft since 2014.
            Microsoft develops Windows, Office, and Azure cloud services.
            Microsoft is headquartered in Redmond, Washington.
            Microsoft and Apple are major competitors in the technology industry."""
        ),
        (
            "sample_doc_3.txt",
            """Steve Jobs was the founder of Apple Inc. and also founded Pixar.
            Jobs was born in San Francisco, California.
            He revolutionized personal computing with the Macintosh.
            Jobs led Apple to become one of the most valuable companies in the world.
            Jobs passed away in 2011 after battling cancer."""
        )
    ]

    temp_files = []
    for filename, content in sample_docs:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        temp_files.append(temp_file.name)

    return temp_files

def demo():
    print("=" * 60)
    print("Graph RAG Demo")
    print("=" * 60)

    print("\n1. Creating sample documents...")
    sample_files = create_sample_documents()

    print("\n2. Loading and chunking documents...")
    documents = []
    for file_path in sample_files:
        try:
            chunks, doc_id = document_loader.load_and_chunk_document(file_path)
            documents.append((chunks, doc_id))
            print(f"   Loaded {file_path}: {len(chunks)} chunks, ID: {doc_id}")
        except Exception as e:
            print(f"   Error loading {file_path}: {e}")
        finally:
            os.unlink(file_path)

    print("\n3. Building knowledge graph...")
    stats = graph_builder.build_graph_from_documents(documents)
    print(f"   Total Entities: {stats['total_entities']}")
    print(f"   Total Relationships: {stats['total_relationships']}")

    print("\n4. Graph Summary:")
    summary = query_engine.get_graph_summary()
    print(f"   Entities: {summary['stats']['entities']}")
    print(f"   Relationships: {summary['stats']['relationships']}")

    print("\n5. Top Entities in the Graph:")
    for entity in summary["top_entities"][:5]:
        print(f"   - {entity['name']} ({entity['type']}): {entity['in_degree']} connections")

    print("\n6. Testing Queries:")
    test_queries = [
        "Who founded Apple?",
        "What is the relationship between Apple and Microsoft?",
        "Where is Apple headquartered?"
    ]

    for query in test_queries:
        print(f"\n   Query: {query}")
        try:
            graph_context = query_engine.execute_graph_query(query)

            result = answer_generator.generate_answer(query, graph_context)
            print(f"   Answer: {result['answer'][:300]}...")
        except Exception as e:
            print(f"   Error: {e}")

    print("\n7. Entity Search:")
    search_results = query_engine.search_entities("Apple")
    print(f"   Found {len(search_results)} results for 'Apple'")
    for result in search_results[:3]:
        print(f"   - {result.get('name', 'Unknown')}")

    print("\n8. Graph Statistics:")
    final_stats = graph_db.get_graph_stats()
    print(f"   Final Entity Count: {final_stats['entities']}")
    print(f"   Final Relationship Count: {final_stats['relationships']}")

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)

if __name__ == "__main__":
    demo()
