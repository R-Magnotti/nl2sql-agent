CREATE EXTENSION IF NOT EXISTS vector; --pg vector import

CREATE TABLE IF NOT EXISTS column_embeddings (
    table_name varchar(255),
    col_name varchar(255), 
    col_desc text, 
    embedding_input text, --embedding_input = table_name + col_name + col_desc

    --size of allmini embedding vectors, scale to whatever size of embedding for your model of choice
    doc_embedding vector(384), --embedding of input text

    --to avoid duplicate entries in the event of updated data upon rerunning the preprocess step
    UNIQUE (table_name, col_name)
);