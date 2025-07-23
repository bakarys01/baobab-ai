"""Enhanced RAG service with African language support and contextual knowledge."""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.utilities import SerpAPIWrapper
import requests
from bs4 import BeautifulSoup

load_dotenv()

class AfricanRAGService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = OpenAI(openai_api_key=self.openai_api_key)
        self.african_knowledge_base = self._load_african_knowledge()
        
    def _load_african_knowledge(self) -> List[str]:
        """Load comprehensive African AI and business context."""
        return [
            # AI Market & Business Context
            "Africa's AI market is projected to reach $16.5B by 2030 with 28% annual growth rate.",
            "Only 14% of African companies are ready to integrate AI into their operations as of 2024.",
            "South Africa, Nigeria, and Kenya lead AI adoption in Africa with the most startups and investments.",
            "Mobile-first AI solutions are crucial in Africa due to high mobile phone penetration (>80%) vs low desktop access.",
            "Data sovereignty and local language support are key challenges for AI adoption in Africa.",
            
            # African Languages & Culture
            "Major African languages for AI development: Swahili (100M+ speakers), Hausa (70M+), Yoruba (45M+), Amharic (32M+).",
            "French is spoken by 280M+ people across 29 African countries, making it crucial for AI applications.",
            "Arabic is dominant in North Africa with 200M+ speakers across countries like Egypt, Algeria, Morocco.",
            "Indigenous languages like Igbo, Zulu, Xhosa need AI support for inclusive technology development.",
            "Cultural context matters: African storytelling traditions, community-based decision making, ubuntu philosophy.",
            
            # Tech Infrastructure
            "Africa has over 600 active tech hubs, with Nigeria (90+), South Africa (80+), and Kenya (50+) leading.",
            "Cloud adoption growing rapidly: AWS, Google Cloud, Microsoft Azure all expanding African data centers.",
            "Internet penetration varies widely: urban areas 70%+, rural areas often <30%, affecting AI deployment strategies.",
            "Mobile money systems like M-Pesa demonstrate African fintech innovation leadership globally.",
            
            # AI Success Stories
            "African AI startups: DataProphet (South Africa) - predictive maintenance, Zindi - data science competitions.",
            "Healthcare AI: Ubenwa (Nigeria) analyzes infant cries, Ilara Health (Kenya) provides diagnostic tools.",
            "Agriculture AI: Aerobotics (South Africa) crop monitoring, iCow (Kenya) farmer advisory via SMS.",
            "Education AI: Eneza Education (Kenya) serves 6M+ students via SMS/WhatsApp learning platforms.",
            
            # MLOps & Development
            "African developers prefer Python (85%), JavaScript (70%), Java (45%) for AI development.",
            "Popular AI frameworks in Africa: TensorFlow, PyTorch, scikit-learn, Hugging Face transformers.",
            "Cloud-first MLOps approach recommended due to limited on-premise infrastructure in many regions.",
            "AutoML tools gaining traction to bridge AI skills gap: H2O.ai, DataRobot, Google AutoML.",
            
            # Challenges & Opportunities
            "Data quality and availability major challenges: 60% of African businesses lack quality data for AI.",
            "AI talent shortage: Africa needs 3M+ more AI professionals by 2030 to meet demand.",
            "Regulatory frameworks developing: South Africa's POPIA, Nigeria's NDPR lead data protection efforts.",
            "Investment growing: African AI startups raised $200M+ in 2023, 5x increase from 2019.",
            
            # Baobab AI Labs Specific
            "Baobab AI Labs focuses on practical AI education for African businesses and developers.",
            "Our mission: Make AI accessible, practical, and impactful for every African business.",
            "We provide MLOps guides optimized for African cloud environments and connectivity patterns.",
            "Community-driven approach: African AI pioneers sharing real success stories and implementation guides.",
        ]
    
    def _get_language_prompts(self, language: str) -> Dict[str, str]:
        """Get culturally appropriate prompts for different languages."""
        prompts = {
            "en": {
                "system": "You are an AI expert specializing in African business contexts and AI implementation. ",
                "context_intro": "Using the CONTEXT below (from web sources and African AI knowledge base), answer precisely and practically. ",
                "no_answer": "I don't have enough information about that specific topic. ",
                "cite_sources": "Cite web sources when available and reference African case studies when relevant."
            },
            "fr": {
                "system": "Tu es un expert en IA spécialisé dans les contextes d'affaires africains et l'implémentation d'IA. ",
                "context_intro": "En utilisant le CONTEXTE ci-dessous (sources web et base de connaissances IA africaine), réponds de façon précise et pratique. ",
                "no_answer": "Je n'ai pas assez d'informations sur ce sujet spécifique. ",
                "cite_sources": "Cite les sources web quand disponibles et référence les études de cas africaines quand pertinentes."
            },
            "sw": {  # Swahili
                "system": "Wewe ni mtaalamu wa AI unayejumuisha mazingira ya biashara za Kiafrika na utekelezaji wa AI. ",
                "context_intro": "Kwa kutumia MUKTADHA hapo chini (vyanzo vya wavuti na msingi wa maarifa ya AI ya Kiafrika), jibu kwa usahihi na vitendo. ",
                "no_answer": "Sina habari za kutosha kuhusu mada hiyo mahususi. ",
                "cite_sources": "Taja vyanzo vya wavuti vinapokona na rejelea masomo ya kesi za Kiafrika vinapofaa."
            }
        }
        return prompts.get(language, prompts["en"])
    
    def web_search(self, query: str, num_results: int = 5, african_focus: bool = True) -> List[Dict[str, str]]:
        """Enhanced web search with African context prioritization."""
        search = SerpAPIWrapper(serpapi_api_key=self.serpapi_key)
        
        # Add African context to search if relevant
        if african_focus and not any(term in query.lower() for term in ['africa', 'african', 'nigeria', 'kenya', 'south africa']):
            query = f"{query} Africa African business"
        
        try:
            results = search.results(query)
            links = []
            for r in results.get("organic_results", [])[:num_results]:
                links.append({
                    "title": r.get("title", ""),
                    "link": r.get("link", ""),
                    "snippet": r.get("snippet", "")
                })
            return links
        except Exception as e:
            logging.error(f"Web search failed: {e}")
            return []
    
    def fetch_webpage_content(self, url: str, max_chars: int = 8000) -> str:
        """Enhanced webpage content extraction with better cleaning."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(url, timeout=10, headers=headers)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe"]):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup
            text = " ".join(main_content.stripped_strings)
            
            return text[:max_chars]
        except Exception as e:
            logging.warning(f"Failed to fetch {url}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Improved text chunking with better boundary detection."""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) > 50:  # Only add substantial chunks
                chunks.append(chunk_text)
        
        return chunks
    
    def generate_response(self, 
                         question: str, 
                         context: str, 
                         language: str = "en",
                         sources: List[Dict] = None) -> str:
        """Generate contextual response with African business focus."""
        
        prompts = self._get_language_prompts(language)
        
        system_prompt = (
            f"{prompts['system']}"
            f"{prompts['context_intro']}"
            f"Focus on practical implementation for African businesses. "
            f"Consider local infrastructure, mobile-first approaches, and cost-effective solutions. "
            f"{prompts['cite_sources']}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            f"RESPONSE:"
        )
        
        try:
            response = self.llm.invoke(system_prompt)
            answer = response.strip()
            
            # Add sources if available
            if sources:
                if language == "fr":
                    answer += "\n\n📚 Sources :\n"
                elif language == "sw":
                    answer += "\n\n📚 Vyanzo :\n"
                else:
                    answer += "\n\n📚 Sources :\n"
                    
                for source in sources[:3]:  # Limit to top 3 sources
                    answer += f"• {source.get('title', 'Unknown')} - {source.get('link', '')}\n"
            
            return answer
            
        except Exception as e:
            logging.error(f"Response generation failed: {e}")
            if language == "fr":
                return "Désolé, je ne peux pas répondre à cette question pour le moment."
            elif language == "sw":
                return "Samahani, siwezi kujibu swali hilo kwa sasa."
            else:
                return "Sorry, I cannot answer that question at the moment."
    
    def run_enhanced_rag(self, 
                        question: str,
                        language: str = "en",
                        num_web_sources: int = 5,
                        include_african_context: bool = True,
                        search_african_focus: bool = True) -> str:
        """
        Enhanced RAG pipeline with African context and multi-language support.
        """
        try:
            # 1. Web search with African focus
            web_sources = self.web_search(question, num_web_sources, search_african_focus)
            
            # 2. Extract and chunk web content
            web_chunks = []
            for source in web_sources:
                content = self.fetch_webpage_content(source["link"])
                if content:
                    chunks = self.chunk_text(content)
                    web_chunks.extend(chunks)
            
            # 3. Combine with African knowledge base
            all_chunks = web_chunks
            if include_african_context:
                all_chunks.extend(self.african_knowledge_base)
            
            # 4. Create vector store and retrieve relevant context
            if all_chunks:
                vectorstore = FAISS.from_texts(all_chunks, embedding=self.embeddings)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
                relevant_docs = retriever.get_relevant_documents(question)
                context = "\n".join([doc.page_content for doc in relevant_docs])
            else:
                context = "\n".join(self.african_knowledge_base[:5])  # Fallback to local knowledge
            
            # 5. Generate response
            response = self.generate_response(question, context, language, web_sources)
            
            return response
            
        except Exception as e:
            logging.error(f"Enhanced RAG failed: {e}")
            return f"Error processing your question: {str(e)}"