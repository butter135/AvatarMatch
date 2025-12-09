from itertools import combinations

import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter

def load_dummy():
    df = pd.read_csv("dummy.csv")
    responses = []

    for attrs in df ["attributes"]:
        attr_list = [a.strip() for a in str(attrs).split(",") if a.strip()]
        responses.append(attr_list)

    return responses

def create_cooccurrence_graph(responses):
    # nord size
    all_attrs = [attr for user_attrs in responses for attr in user_attrs]
    popularity = Counter(all_attrs)

    # edge size
    cooc = Counter()
    for user_attrs in responses:
        for a, b in combinations(sorted(user_attrs), 2):
            cooc[(a, b)] += 1

    graph = nx.Graph()

    # add node
    for attr, count in popularity.items():
        graph.add_node(attr, size=count)

    #add edge
    for (a, b), w in cooc.items():
        graph.add_edge(a, b, weight = w)

    return graph

def export_html(graph):
    net = Network(height = "700px", width = "100%", bgcolor = "#1e1e1e", font_color = "white")
    net.from_nx(graph)

    # ノードサイズ調整
    for node in net.nodes:
        if "size" in node:
            node["value"] = node["size"]

    # エッジ太さ調整
    for edge in net.edges:
        if "weight" in edge:
            edge["width"] = edge["weight"]

    # HTML 出力
    net.save_graph("network.html")
    print(f"network.html を生成しました")


responses = load_dummy()
graph = create_cooccurrence_graph(responses)
export_html(graph)