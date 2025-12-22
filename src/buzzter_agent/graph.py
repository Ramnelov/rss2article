from langgraph.graph import END, START, StateGraph

from buzzter_agent.nodes.fulltext import fetch_fulltext
from buzzter_agent.nodes.notis import generate_notis
from buzzter_agent.nodes.qa import qa_check
from buzzter_agent.nodes.relevance import classify_relevance
from buzzter_agent.nodes.rss import load_rss
from buzzter_agent.state import State


def build_graph():
    graph = StateGraph(State)

    graph.add_node("load_rss", load_rss)
    graph.add_node("classify_relevance", classify_relevance)
    graph.add_node("fetch_fulltext", fetch_fulltext)
    graph.add_node("generate_notis", generate_notis)
    graph.add_node("qa_check", qa_check)

    graph.add_edge(START, "load_rss")
    graph.add_edge("load_rss", "classify_relevance")
    graph.add_edge("classify_relevance", "fetch_fulltext")
    graph.add_edge("fetch_fulltext", "generate_notis")
    graph.add_edge("generate_notis", "qa_check")
    graph.add_edge("qa_check", END)

    return graph.compile()
