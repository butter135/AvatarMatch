from itertools import combinations

import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network
from collections import Counter

def load_dummy():
    df = pd.read_csv("avatar_dummy_100.csv")
    responses = []

    for attrs in df ["以下の特徴タグから、「好き」「魅力を感じる」と思うものを最大5つ選んでください"]:
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

    max_population = max(popularity.values())
    min_population = min(popularity.values())
    threshold = np.percentile(list(cooc.values()), 60)
    strong_edges = {pair: w for pair, w in cooc.items() if w > threshold}
    w_min = min(strong_edges.values())
    w_max = max(strong_edges.values())

    graph = nx.Graph()

    # add node
    for attr, count in popularity.items():
        if max_population == min_population:
            norm = 0.5
        else:
            norm = (count - min_population) / (max_population - min_population)
        graph.add_node(attr, size = (3 + norm * 30))

    #add edge
    for (a, b), w in strong_edges.items():
        if w_max == w_min:
            norm = 0.5
        else:
            norm = (w - w_min) / (w_max - w_min)

        graph.add_edge(a, b, weight = w, width = (2 + (norm ** 1.5) * 50))

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

    net.toggle_physics(False)


    # HTML 出力
    net.save_graph("network.html")
    print(f"network.html を生成しました")


responses = load_dummy()
graph = create_cooccurrence_graph(responses)
export_html(graph)