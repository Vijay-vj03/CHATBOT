import google.generativeai as genai
import logging
from typing import List, Dict, Any, Tuple
import os

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Generate an answer using the LLM with retrieved context"""
        try:
            if not context_docs:
                return "I don't have enough information to answer your question.", 0.0
            
            # Prepare context from retrieved documents
            context_text = self._format_context(context_docs)
            
            # Create prompt with context and query
            prompt = self._create_prompt(query, context_text)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return "I couldn't generate a response. Please try rephrasing your question.", 0.0
            
            # Calculate confidence based on context relevance
            confidence = self._calculate_confidence(context_docs)
            
            # Ensure the response includes source references
            answer = self._add_source_references(response.text, context_docs)
            
            return answer, confidence
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"An error occurred while generating the answer: {str(e)}", 0.0
    
    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context text"""
        context_parts = []
        
        for i, doc in enumerate(context_docs):
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', f'Document {i+1}')
            content = doc.get('content', '')
            
            context_parts.append(f"Source {i+1} (from {filename}):\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a prompt for the LLM"""
        prompt = f"""You are a helpful AI assistant that answers questions based on provided context documents. 

IMPORTANT INSTRUCTIONS:
1. Answer the question using ONLY the information provided in the context below
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Always cite your sources by mentioning the specific document/file when referencing information
4. Be concise but comprehensive in your response
5. If multiple sources support your answer, mention all relevant sources

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {query}

Please provide a well-structured answer with proper source citations:"""

        return prompt
    
    def _calculate_confidence(self, context_docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on context relevance"""
        if not context_docs:
            return 0.0
        
        # Use the average relevance score of top documents
        scores = [doc.get('score', 0.0) for doc in context_docs]
        avg_score = sum(scores) / len(scores)
        
        # Normalize to 0-1 range and apply some heuristics
        confidence = min(avg_score * 1.2, 1.0)  # Boost slightly but cap at 1.0
        
        # Reduce confidence if we have very few relevant documents
        if len(context_docs) < 2:
            confidence *= 0.8
        
        return round(confidence, 2)
    
    def _add_source_references(self, answer: str, context_docs: List[Dict[str, Any]]) -> str:
        """Ensure the answer includes proper source references"""
        if not context_docs:
            return answer
        
        # If the answer doesn't seem to include source references, add them
        if "source" not in answer.lower() and "document" not in answer.lower():
            sources = []
            for i, doc in enumerate(context_docs):
                metadata = doc.get('metadata', {})
                filename = metadata.get('filename', f'Document {i+1}')
                sources.append(f"- {filename}")
            
            source_text = "\n\nSources:\n" + "\n".join(sources)
            answer += source_text
        
        return answer
