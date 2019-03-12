import pygraphviz as pgv
import networkx as nx
import matplotlib.pyplot as plt
import sys

DATA=1
METHOD=2
RESULT=3

INPUT="入力/使用"
CONVERT="変換/抽出"
OUTPUT="出力/結果"
SAME="同義"
FLOW="処理の流れ"

graph=nx.DiGraph()

# Test
#nodes=[{"Corpus":DATA},{"Input Text":DATA},{"Word Vector":DATA},{"SVM":METHOD},{"Classifier":RESULT}]
#edges=[["Corpus","Word Vector","Input/Use"],["Input Text","Word Vector","Convert"],["Word Vector","SVM","Input/Use"],["SVM","Classifier","Output/Result"]]

# Automatic
#V11-03-01
#outfilename="V11-03-01.png"
#nodes=[{"先行詞":DATA},{"省略解析":RESULT},{"格フレーム辞書":DATA},{"格解析":DATA},{"選択制限":METHOD},{"ゼロ代名詞の検出":METHOD},{"先行詞の同定":RESULT},{"ゼロ代名詞":DATA},{"先行詞":RESULT}]
#edges=[["先行詞","省略解析",OUTPUT],["格フレーム辞書","省略解析",OUTPUT],["格フレーム辞書","格解析",CONVERT],["格解析","ゼロ代名詞の検出",INPUT],["選択制限","先行詞の同定",OUTPUT],["ゼロ代名詞","先行詞",OUTPUT]]

#V05-03-05
#outfilename="V05-03-05.png"
#nodes=[{"構文的優先度":METHOD},{"統計情報の反映":METHOD},{"構文モデル":METHOD},{"統計情報":DATA},{"統計情報の統合":METHOD},{"構文解析の曖昧性解消":RESULT}]
#edges=[["構文的優先度","統計情報の反映",FLOW],["統計情報の反映","構文モデル",FLOW],["統計情報","構文モデル",INPUT],["統計情報","統計情報の統合",INPUT],["統計情報の統合","構文解析の曖昧性解消",OUTPUT]]

#V17-01-07
#outfilename="V17-01-07.png"
#nodes=[{"名詞句":DATA},{"コーパス":DATA},{"語彙統語パターン":DATA},{"事態性名詞の項構造解析":RESULT},{"名詞":DATA},{"機械学習":METHOD},{"解析手法":RESULT}]
#edges=[["名詞句","語彙統語パターン",CONVERT],["コーパス","語彙統語パターン",CONVERT],["語彙統語パターン","事態性名詞の項構造解析",OUTPUT],["名詞","機械学習",INPUT],["機械学習","解析手法",OUTPUT]]

#Formal
#V10-02-04
outfilename="V10-02-04.png"
nodes=[{"総索引":DATA},{"最長一致法":METHOD},{"先読み法":METHOD},{"品詞タグ付きコーパスの作成":RESULT}]
edges=[["総索引","最長一致法",INPUT],["総索引","先読み法",INPUT],["最長一致法","品詞タグ付きコーパスの作成",OUTPUT],["先読み法","品詞タグ付きコーパスの作成",OUTPUT]]

#V03-01-02
#outfilename="V03-01-02.png"
#nodes=[{"4文字漢字語16万語":DATA},{"共起データ":DATA},{"意味的関係":DATA},{"相互情報量":METHOD},{"ヒューリスティクス":METHOD},{"機械可読辞書":DATA},{"言語知識":DATA},{"複合名詞の解析":RESULT}]
#edges=[["4文字漢字語16万語","共起データ",CONVERT],["共起データ","相互情報量",INPUT],["相互情報量","意味的関係",OUTPUT],["意味的関係","複合名詞の解析",OUTPUT],["ヒューリスティクス","複合名詞の解析",OUTPUT],["機械可読辞書","言語知識",CONVERT],["言語知識","複合名詞の解析",OUTPUT]]

#V05-04-05
#outfilename="V05-04-05.png"
#nodes=[{"入力キュエリ":DATA},{"対訳辞書":DATA},{"入力共起頻度ベクトル":DATA},{"翻訳キュエリ候補の生成":METHOD},{"翻訳共起頻度ベクトル":DATA},{"ランキング":METHOD},{"検索キュエリ":DATA},{"日英クロス言語検索":RESULT},{"クロス言語検索手法GDMAX":RESULT}]
#edges=[["入力キュエリ","入力共起頻度ベクトル",CONVERT],["入力キュエリ","翻訳キュエリ候補の生成",INPUT],["対訳辞書","翻訳キュエリ候補の生成",INPUT],["翻訳キュエリ候補の生成","翻訳共起頻度ベクトル",OUTPUT],["入力共起頻度ベクトル","ランキング",INPUT],["翻訳共起頻度ベクトル","ランキング",INPUT],["ランキング","検索キュエリ",OUTPUT],["検索キュエリ","クロス言語検索手法GDMAX",OUTPUT],["クロス言語検索手法GDMAX","日英クロス言語検索",SAME]]


def equalNodeType(term,TYPE):
    for node in nodes:
        if term in node:
            if node[term]==TYPE:
                return True
            else:
                return False
    return False

for node in nodes:
    name=list(node.keys())[0]
    graph.add_node(name)
    graph.node[name]["size"]=16
    graph.node[name]["color"]="red"
 
for edge in edges:
    graph.add_edge(edge[0],edge[1])
    graph.edges[edge[0],edge[1]]["color"]="black"
    graph.edges[edge[0],edge[1]]["label"]=edge[2]

pos=nx.spring_layout(graph,k=3.5)
nx.draw_networkx_nodes(graph,pos)
nx.draw_networkx_edges(graph,pos)

agraph=nx.nx_agraph.to_agraph(graph)
#agraph.get_node("Corpus").attr["shape"]="box"
for node in agraph.nodes():
    if equalNodeType(str(node),DATA):
        node.attr["shape"]="ellipse"
    elif equalNodeType(str(node),METHOD):
        node.attr["shape"]="rect"
    elif equalNodeType(str(node),RESULT):
        node.attr["shape"]="doubleoctagon"

agraph.draw(outfilename,prog="dot")
