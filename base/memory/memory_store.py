import numpy as np
import time
import networkx as nx
import os

from datetime import datetime, timezone
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from collections import defaultdict
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from loguru import logger
from ..infrastructure.weaviate_vdb import connection
from ..ovm import VectorBaseModel
from .token_counter import TokenCounter
from weaviate.collections.classes.internal import Object
from weaviate.classes.query import Sort
from .memory_workflow import MemoryWorkflowOpenAI
from uuid import uuid4

class WeaviateMemoryStore():
    
    class Settings:
        name = "chat_history"
    
    def __init__(self, dimension=1536, num_latest_chunks=2, num_relevant_chunks=2, embedding_model="text-embedding-3-small"):
        
        # self.connection = connection
        self.token_counter = TokenCounter(model=embedding_model)
        self.memory_workflow = MemoryWorkflowOpenAI()
        
        # number of latest chunks to retrieve
        self.num_latest_chunks = num_latest_chunks
        self.num_relevant_chunks = num_relevant_chunks
        self.dimension = dimension
        self.graph = nx.Graph()
        self.semantic_memory = defaultdict(list)
        self.cluster_labels = []
        
        # name of the vector that will be used for retrieval
        self.vector_name = "summary_vector"
        self.memory_collection_name = "chat_history"
        
        # Tracking parameters
        self.max_interactions_per_chunk = 5
        self.token_length_threshold = 2048
        
        def get_collection(collection_name):
            return connection.collections.get(collection_name)
        
        self.memory_collection = get_collection(self.memory_collection_name)
    
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """
        Add an interaction to the memory store
        
        Args:
            interaction: a dictionary that contains:
            - user_id (str): user id
            - conversation (Dict[str, str]): a pair of human query + bot response:
            + key (str): role
            + value (str): content
        """

        chat_string = self._dict_to_string(interaction['conversation'])
        token_length = self.token_counter.count_tokens(chat_string)

        self._get_or_create_chunk(chat_string, token_length, interaction['user_id'])
        
    def _dict_to_string(self, interaction: Dict[str, Any]) -> str:
        return "\n".join([f"{key}: {value}" for key, value in interaction.items()])
    
    def _get_chunk_properties_to_update(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        # This function updates context_tags, what worked, what to avoid, user skill evaluation of a chunk & summary
        # We can either write a prompt to extract all the above information, or write a prompt to extract each information
        updated_fields = self.memory_workflow.extract_all(chunk['conversation'])
        
        return updated_fields
        
    
    def _get_or_create_chunk(self, chat_string: str, token_length: int, user_id: str = "_"):
        
        """
        Get an existing chunk or create a new one based on the latest chat history chunk's token length
        """
        
        chunks = self.memory_collection.query.fetch_objects(sort=Sort.by_property(name="created_date", ascending=False), limit=1)
        
        latest_chunk = chunks.objects[0] if len(chunks.objects) > 0 else None
        
        # if the latest chunk reach its capacity, update its fields
        if (latest_chunk is not None and
            (latest_chunk.properties['num_interactions'] >= self.max_interactions_per_chunk or
            latest_chunk.properties['total_token_length'] + token_length > self.token_length_threshold)):
            
            updated_fields = self._get_chunk_properties_to_update(latest_chunk.properties)
            
            self.update(str(latest_chunk.uuid), updated_fields)
            self._update_graph(updated_fields.get('context_tags', []))
        
        if (latest_chunk is None or
            latest_chunk.properties['num_interactions'] >= self.max_interactions_per_chunk or
            latest_chunk.properties['total_token_length'] + token_length > self.token_length_threshold):
            # Create new chunk
            new_chunk = {
                "user_id": user_id,
                "conversation_id": str(uuid4()), # create a new uuid
                "conversation": chat_string,
                "total_token_length": token_length,
                "context_tags": [],
                "conversation_summary": "",
                "what_worked": "",
                "what_to_avoid": "",
                "user_skill_evaluation": "",
                "created_date": datetime.now(),
                "last_accessed": datetime.now(),
                "num_interactions": 1, 
                "access_counts": 1,
                "decay_factor": 1.0
            } 
            return self.upsert(new_chunk)

        else:
            # Update existing chunk
            update_data = {
                "conversation": latest_chunk.properties['conversation'] + f"\n{chat_string}",
                "total_token_length": latest_chunk.properties['total_token_length'] + token_length,
                "num_interactions": latest_chunk.properties['num_interactions'] + 1,
                "last_accessed": datetime.now()
            }
            # temporary solution, need to be optimized
            uuid = str(latest_chunk.uuid)
            return self.update(uuid, update_data)
    
    def _update_graph(self, context_tags: List[str]):
        """
        Update the context_tags graph
        This def needs to be optimized
        """
        
        for context_tag in context_tags:
            self.graph.add_node(context_tag)
        for context_tag1 in context_tags:
            for context_tag2 in context_tags:
                # the exact match is way too strict
                if context_tag1 != context_tag2:
                    if self.graph.has_edge(context_tag1, context_tag2):
                        self.graph[context_tag1][context_tag2]['weight'] += 1
                    else:
                        self.graph.add_edge(context_tag1, context_tag2, weight=1)
    
    def retrieve_k_latest_chunks(self) -> Optional[List[Dict[str, Any]]]:
        
        """
        Retrieve the latest chunk
        """

        chunks = self.memory_collection.query.fetch_objects(sort=Sort.by_property(name="created_date", ascending=False), limit=self.num_latest_chunks)
        
        latest_chunks = None
        if chunks:
            latest_chunks = [chunk_object.properties for chunk_object in chunks.objects]
            
        return latest_chunks
    
    def retrieve_relevant_chunks(self, query_embedding, query_concepts, similarity_threshold=0.1):
        """
        Retrieve relevant interactions
        """
        
        # results = self.search(query=query, limit=5, include_vector=True)
        
        # normalize query embedding
        query_embedding_norm = normalize([query_embedding])
        
        # needs to be optimized
        results = self.memory_collection.query.near_vector(
            near_vector=query_embedding,
            # dunno which threshold works best in this case
            # distance=similarity_threshold/100,
            include_vector=True,
            limit=self.num_relevant_chunks
        )
        
        # Process retrieved interactions
        relevant_chunks = []
        current_time = datetime.now(timezone.utc)
        decay_rate = 0.001
        
        for chunk in results.objects:
            
            # Cosine similarity calculation
            embedding = np.array(chunk.vector[self.vector_name]).reshape(1, -1)
            similarity = cosine_similarity(query_embedding_norm, normalize(embedding))[0][0]
            
            # get chunk uuid
            chunk_uuid = str(chunk.uuid)
            # obtain the dictionary from the object
            chunk = chunk.properties
            
            # Time-based decay
            time_diff = (current_time - chunk.get('last_accessed', current_time)).seconds / (24 * 60)

            if chunk.get('decay_factor') is None:
                chunk['decay_factor'] = 1.0
            decay_factor = chunk.get('decay_factor', 1.0) * np.exp(-decay_rate * time_diff)
            
            # Reinforcement
            access_count = chunk.get('access_counts', 1)
            reinforcement_factor = np.log1p(access_count)
            
            # Adjusted similarity
            adjusted_similarity = similarity * decay_factor * reinforcement_factor
            
            if adjusted_similarity >= similarity_threshold:
                # Spreading activation
                activated_concepts = self.spreading_activation(query_concepts)
                activation_score = sum([activated_concepts.get(c, 0) for c in chunk.get('context_tags', [])])
                
                total_score = adjusted_similarity + activation_score
                # interaction['total_score'] = total_score
                
                relevant_chunks.append((total_score, chunk))
                # Increase decay factor and access count for relevant interaction
                self.update(chunk_uuid, {"access_counts": chunk.get('access_counts', 0) + 1, "decay_factor": decay_factor * 1.05})
    
        # Sort and return interactions
        relevant_chunks.sort(key=lambda x: x[0], reverse=True)
        relevant_chunks = [chunk for _, chunk in relevant_chunks]
        
        return relevant_chunks
        
    def spreading_activation(self, query_concepts):
        """
        Spreading activation for concept associations
        """
        
        activated_nodes = {}
        initial_activation = 1.0
        decay_factor = 0.5  # How much the activation decays each step

        # Initialize activation levels
        for concept in query_concepts:
            activated_nodes[concept] = initial_activation

        # needs to be revised
        # Spread activation over the graph
        for step in range(2):  # Number of steps to spread activation
            new_activated_nodes = {}
            for node in activated_nodes:
                if node in self.graph:  # Check if the node exists in the graph
                    for neighbor in self.graph.neighbors(node):
                        if neighbor not in activated_nodes:
                            weight = self.graph[node][neighbor]['weight']
                            new_activation = activated_nodes[node] * decay_factor * weight
                            new_activated_nodes[neighbor] = new_activated_nodes.get(neighbor, 0) + new_activation
            activated_nodes.update(new_activated_nodes)
        
        return activated_nodes
    
    def update(
        self,
        uuid: str,
        update_data: Dict[str, Any]
    ):
        try:
            result = self.memory_collection.data.update(uuid=uuid, properties=update_data)
            return result
        except Exception as e:
            logger.error(f"Failed to update document in {self.memory_collection_name}: {e}")
            raise
    
    def upsert(
        self,
        data: Dict[str, Any]
    ) -> str:
        try:
            result = self.memory_collection.data.insert(data)
            return result
        except Exception as e:
            logger.error(f"Failed to insert document into {self.memory_collection_name}: {e}")
            raise
