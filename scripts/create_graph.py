from itertools import combinations
import datetime
import pandas as pd
import networkx as nx
import numpy as np
import colorsys
from pyvis.network import Network
from collections import Counter

class CreateGraph:
    def __init__(self, repo_root) -> None:
        self.csv_path = (repo_root / "csv" / "avatar_match.csv")
        self.graph_path = str(repo_root / "docs" / "network.html")
    def load_dummy(self):
        df = pd.read_csv(self.csv_path)
        responses = []

        for _, row in df.iterrows():
            height = str(row["好みの身長タイプを教えて下さい"]).strip()
            attrs = row["以下の特徴タグから、「好き」「魅力を感じる」と思うものを最大5つ選んでください"]
            attr_list = [a.strip() for a in str(attrs).split(",") if a.strip()]
            merged = [height] + attr_list
            responses.append(merged)

        return responses

    def create_cooccurrence_graph(self, responses):
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
        threshold = np.percentile(list(cooc.values()), 70)
        strong_edges = {pair: w for pair, w in cooc.items() if w > threshold}
        if strong_edges:
            w_min = min(strong_edges.values())
            w_max = max(strong_edges.values())
        else:
            w_min = w_max = 1

        graph = nx.Graph()

        # add node
        for attr, count in popularity.items():
            if max_population == min_population:
                norm = 0.5
            else:
                norm = (count - min_population) / (max_population - min_population)
            color = norm_color(norm)
            graph.add_node(attr, label = f"{attr} ({round(norm, 2)})", shape = "box", color = { "background" : color, "border" : "#1e1e1e"})

        #add edge
        for (a, b), w in strong_edges.items():
            if w_max == w_min:
                norm = 0.5
            else:
                norm = (w - w_min) / (w_max - w_min)
            color = norm_color(norm)
            graph.add_edge(a, b, weight = w, width = (2 + norm * 50), color = color)

        return graph

    def export_html(self, graph):
        net = Network(height = "700px", width = "100%", bgcolor = "#c2e1ff", font_color = "#1e1e1e")
        net.from_nx(graph)

        # ノードサイズ調整
        for node in net.nodes:
            if "size" in node:
                node["value"] = node["size"]

        net.toggle_physics(False)

        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "centralGravity": 0.3,
                    "springLength": 300,
                    "springConstant": 0.005
                }
            }
        }
        """)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # HTML 出力
        net.save_graph(self.graph_path)

        with open(self.graph_path, "r", encoding="utf-8") as f:
            htmlfile = f.read()

        # 追加する CSS + DIV
        legend_html = f"""
        <style>
        .color-legend {{
        width: 60%;
        height: 20px;
        margin: 20px auto;
        border-radius: 4px;
        background: linear-gradient(to right,
        rgb(255, 255, 255),
        rgb(255, 0, 0)
        );
        border: 1px solid #1e1e1e;
        }}
        .legend-labels {{
        width: 60%;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #333;
        }}
        </style>

        <div class="color-legend"></div>
        <div class="legend-labels">
        <span>低頻度</span>
        <span>高頻度</span>
        </div>
        <div class="legend-description" style="
        width: 60%;
        margin: 20px auto 30px auto;
        font-size: 13px;
        color: #444;
        text-align: center;
        line-height: 1.5;
        ">
        <b>最終更新日時[{now}]</b></br>
        ノードの色は、その特徴がどれくらいの人に選ばれたかを表しています。</br>
        エッジの色や太さは、2つの特徴が同じ回答の中で一緒に選ばれた頻度を示します。</br>
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfxQ6kSiMD_cHL5kEaMKI_k2iKhG18PRbCsoSENjb54kG6jow/viewform">アンケートの回答はこちらから</a>
        </div>
        """

        # </body> の直前に差し込む
        htmlfile = htmlfile.replace("</body>", legend_html + "\n</body>")

        with open(self.graph_path, "w", encoding="utf-8") as f:
            f.write(htmlfile)
        print(f"network.html を生成しました")

    def run(self):
        responses = self.load_dummy()
        graph = self.create_cooccurrence_graph(responses)
        self.export_html(graph)


def norm_rgb(norm) -> str:
        r = 255
        g = int(255 * (1 - norm))
        b = int(255 * (1 - norm))
        return f"rgb({r},{g},{b})"

def norm_color(norm):
        r, g, b = colorsys.hsv_to_rgb(0, norm, 1.0)
        return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

