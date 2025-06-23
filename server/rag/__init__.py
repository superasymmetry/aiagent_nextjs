import os
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoModel
import time
from tqdm.auto import tqdm
from semantic_router.encoders import HuggingFaceEncoder
import requests
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# class state(TypedDict):
#     messages: Annotated[list, add_messages]

# def chatbot(state: State):
#     return {"messages": }

class ragStore():
    def __init__(self, data):
        os.environ["PINECONE_API_KEY"] = "pcsk_6Z7zeR_7fncnEvXrmxbM4eWmXhUcpoYPzzsCVC3sgNCn3nPJFzikckHZnMs3mnoobnTmpV"
        self.embeddings = PineconeEmbeddings(model="multilingual-e5-large", api_key=os.environ["PINECONE_API_KEY"])

        self.batch_size = 128  # how many embeddings we create and insert at once
        
        texts = []
        for control_type, elements in data.items():
            for element in elements:
                # Create a string representation of the feature and coordinates
                text = f"Control Type: {control_type}. Feature: {element['feature']}. Coordinates: {element['coordinates']}"
                texts.append(text)

        # Now embed the list of texts
        self.feature_embeds = self.embeddings.embed_documents(texts)
        self.pc = Pinecone(api_key="pcsk_6Z7zeR_7fncnEvXrmxbM4eWmXhUcpoYPzzsCVC3sgNCn3nPJFzikckHZnMs3mnoobnTmpV")
        index = self.pc.Index('aiindex')

        self.vector_store = PineconeVectorStore(embedding=self.embeddings, index=index)


        # chat history
        self.convo = []

    def retrieve(self,query):
        # query_embed = self.embeddings.embed_query(query)

        # results = self.embeddings.retrieve(query_embed, self.doc_embeds)

        # return results
        retrieved_docs = self.vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    def add_chat_history(self, query, response):
        self.convo.append((query, response))

if __name__ == "__main__":
    ui_features = {'WindowControl': [{'feature': 'Grammarly Anchor Window', 'coordinates': (2837, 1803, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (15, 1803, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (2837, 9, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (15, 9, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (1774, 1748, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (680, 1748, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (1676, 1644, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (794, 1644, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (794, 1748, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (196, 196, 44, 44)}, {'feature': 'Grammarly Anchor Window', 'coordinates': (1676, 1748, 44, 44)}], 'PaneControl': [{'feature': 'Desktop 1', 'coordinates': (0, 0, 2880, 1920)}, {'feature': 'Taskbar', 'coordinates': (0, 1776, 2880, 144)}, {'feature': 'Running applications', 'coordinates': (552, 1824, 1330, 96)}, {'feature': 'DesktopWindowXamlSource', 'coordinates': (0, 1776, 2880, 144)}, {'feature': 'store.py - aiagent - Visual Studio Code', 'coordinates': (-13, -13, 2906, 1850)}, {'feature': 'GroqCloud - Google Chrome - Coco', 'coordinates': (-13, -13, 2906, 1850)}, {'feature': 'core.py - ElleHacks-2025 - Visual Studio Code', 'coordinates': (-13, -13, 2906, 1850)}, {'feature': 'algs.py - Desktop-Helper-app - Visual Studio Code', 'coordinates': (240, 160, 2400, 1600)}, {'feature': 'Program Manager', 'coordinates': (0, 0, 2880, 1920)}], 'DocumentControl': [{'feature': 'store.py - aiagent - Visual Studio Code', 'coordinates': (0, 0, 2880, 1824)}, {'feature': 'core.py - ElleHacks-2025 - Visual Studio Code', 'coordinates': (0, 0, 2880, 1824)}, {'feature': 'algs.py - Desktop-Helper-app - Visual Studio Code', 'coordinates': (240, 160, 2400, 1600)}], 'ButtonControl': [], 'EditControl': [], 'CheckBoxControl': [], 'RadioButtonControl': [], 'ComboBoxControl': [], 'ListControl': [], 'ListItemControl': [], 'MenuControl': [], 'TreeControl': [], 'TabControl': [], 'SliderControl': [], 'CustomControl': []}
    rag_store = ragStore(ui_features)

    print(rag_store.retrieve("What are the coordinates of google chrome?"))