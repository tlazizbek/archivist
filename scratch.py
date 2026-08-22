from pathlib import Path

from archivist.db.database import(
    init_db,
    insert_chunks,
    insert_document,
    get_all_chunks,
)
from archivist.models import Chunk, RawDocument


init_db()

document = RawDocument(
    path=Path("fake.txt"),
    title="Fake Document",
    source_type="text",
    raw_text="This is fake document content.",
)

document_id = insert_document(document)

chunks = [
    Chunk(
        document_id=document_id,
        chunk_index=0,
        content="This is the first chunk content.",
        token_count=7,
    ),
    Chunk(
        document_id=document_id,
        chunk_index=1,
        content="This is the second chunk content.",
        token_count=7,
    ),
]

insert_chunks(document_id, chunks)

results = get_all_chunks()

for chunk in results:
    print(chunk)