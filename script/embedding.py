import os
import openai
import pandas as pd
from scipy import spatial
openai.api_type = "azure"
openai.api_version = "2023-05-15"
EMBEDDING_MODEL = "text-embedding-ada-002"

stop_words = [
    "a", "an", "the", "this", "that", "these", "those", "some", "any", "every",
    "all", "both", "either", "neither", "such", "no", "none", "few", "several",
    "many", "much", "more", "most", "less", "least", "fewer", "fewest", "another",
    "other", "others", "and", "but", "or", "nor", "so", "yet", "in", "on", "at",
    "by", "for", "to", "from", "with", "without", "can", "could", "may", "might",
    "will", "would", "shall", "should", "must", "is", "are", "was", "were", "have",
    "has", "had", "do", "does", "did", "be", "been", "being", "get", "gets", "got",
    "getting", "go", "goes", "went", "going", "make", "makes", "made", "making",
    "take", "takes", "took", "taking", "come", "comes", "came", "coming", "give",
    "gives", "gave", "giving"
]

stop_words += [
    "en", "ett", "den", "det", "denna", "detta", "dessa", "de", "någon", "några", "varje",
    "alla", "båda", "antingen", "varken", "sådan", "ingen", "inga", "få", "flera",
    "många", "mycket", "mer", "mest", "mindre", "minst", "färre", "minst", "en annan",
    "annan", "andra", "och", "men", "eller", "eller inte", "så", "än", "i", "på", "vid",
    "av", "för", "till", "från", "med", "utan", "kan", "kunde", "får", "kunde",
    "kommer", "skulle", "ska", "bör", "måste", "är", "är", "var", "var", "har",
    "har", "hade", "gör", "gör", "gjorde", "vara", "varit", "varande", "få", "får", "fick",
    "få", "gå", "går", "gick", "gå", "göra", "gör", "gjorde", "gör",
    "ta", "tar", "tog", "tar", "komma", "kommer", "kom", "kommer", "ge",
    "ger", "gav", "ger"
]

def remove_words(text: str, words: list[str]) -> str:
    """Remove words from a string."""
    return " ".join([word for word in text.split() if word not in words])

with(open('openai.key')) as f:
    openai.api_key = f.read().strip()

with(open('openai.base')) as f:
    openai.api_base = f.read().strip()

def create_embedding(filepath):
    #Note: The openai-python library support for Azure OpenAI is in preview.
    import re
    from PyPDF2 import PdfReader
    filename = re.split(r'[/|\\]',filepath)[-1].replace(".pdf", "")
    reader = PdfReader(filename+".pdf")
    number_of_pages = len(reader.pages)
    pages = [page.extract_text() for page in reader.pages]

    BATCH_SIZE = 1

    embeddings = []
    for batch_start in range(0, len(pages), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = pages[batch_start:batch_end]
        print(f"Batch {batch_start} to {batch_end-1}")
        response = openai.Embedding.create(model=EMBEDDING_MODEL, input=batch, deployment_id=EMBEDDING_MODEL)
        for i, be in enumerate(response["data"]):
            assert i == be["index"]  # double check embeddings are in same order as input
        batch_embeddings = [e["embedding"] for e in response["data"]]
        embeddings.extend(batch_embeddings)

    df = pd.DataFrame({"text": pages, "embedding": embeddings})
    df.to_csv(f"data/{filename}.csv", index=False)
    return df

def get_embedding(filepath):
    import ast
    import pandas as pd
    import re
    from PyPDF2 import PdfReader
    filename = re.split(r'[/|\\]',filepath)[-1].replace(".pdf", "")
    try:
        df = pd.read_csv(f"data/{filename}.csv")
        print("Embedding found")
        return df
    except FileNotFoundError as e:
        print("No embedding found")
        return False

# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    import ast
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
        deployment_id=EMBEDDING_MODEL
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

