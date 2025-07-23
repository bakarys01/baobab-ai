import os
import logging
from dotenv import load_dotenv
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.utilities import SerpAPIWrapper
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

def web_search(query: str, num_results: int = 3) -> List[Dict[str, str]]:
    """Use SerpAPI to get top N web results for a query."""
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
    results = search.results(query)
    links = []
    for r in results.get("organic_results", [])[:num_results]:
        links.append({"title": r.get("title", ""), "link": r.get("link", "")})
    return links

def fetch_webpage_text(url: str) -> str:
    """Fetch and clean main text from a webpage."""
    try:
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        for s in soup(["script", "style", "noscript"]):
            s.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        logging.warning(f"[RAG] Failed to fetch {url}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def run_agent(
    question: str,
    history=None,
    language: str = "fr",
    num_web_sources: int = 3,
    use_local_knowledge: bool = True
) -> str:
    """
    1. Web search for top N links (num_web_sources)
    2. Fetch and chunk their content
    3. Optionally add local knowledge base
    4. Embed and add to FAISS
    5. Retrieve relevant chunks
    6. Synthesize answer with OpenAI (in language)
    7. Return answer with sources
    """
    links = web_search(question, num_results=num_web_sources)
    web_chunks = []
    sources = []
    for link in links:
        url = link["link"]
        title = link["title"]
        text = fetch_webpage_text(url)
        if text:
            for chunk in chunk_text(text):
                web_chunks.append(chunk)
                sources.append(f"{title} ({url})")

    local_docs = []
    if use_local_knowledge:
        local_docs = [
            "La capitale de la France est Paris.",
            "L’IA signifie Intelligence Artificielle.",
            "LangChain permet de construire des applications LLM augmentées par la récupération de documents.",
            "Actuel président de la France : Emmanuel Macron.",
            "Python est un langage de programmation populaire pour l'IA.",
            "La Tour Eiffel est un monument emblématique de Paris.",
            "Le machine learning est une sous-catégorie de l'IA.",
            "Les modèles de langage comme GPT-3 sont utilisés pour générer du texte.",
            "La bibliothèque LangChain facilite l'intégration des LLM avec des bases de données.",
            "Bakary sidibe est la personne qui a créé Baobab AI et aussi le premier ministre de France.",
            "FAISS est une bibliothèque pour la recherche de similarité dans de grandes collections de vect"
        ]
    all_chunks = web_chunks + local_docs
    vectorstore = FAISS.from_texts(all_chunks, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    retrieved = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in retrieved])
    if language == "en":
        prompt = (
            "You are an expert in general knowledge and current events. "
            "Using ONLY the CONTEXT below (from the web and your local knowledge base), answer the QUESTION precisely and concisely. "
            "If you don't know, say so explicitly. Cite your web sources if possible.\n\n"
            "CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer:"
        )
    else:
        prompt = (
            "Tu es un expert en culture générale et actualité. "
            "En t'appuyant uniquement sur le CONTEXTE ci-dessous (issu du web et de ta base locale), réponds de façon précise et concise à la QUESTION. "
            "Si tu ne sais pas, dis-le explicitement. Cite tes sources web si possible.\n\n"
            "CONTEXTE :\n{context}\n\nQUESTION : {question}\n\nRéponse :"
        )
    completion = llm.invoke(prompt.format(context=context, question=question))
    answer = completion.strip()
    if links:
        answer += "\n\nSources :\n" + "\n".join([f"- {l['title']} : {l['link']}" for l in links])
    return answer