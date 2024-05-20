import gradio as gr
import plotly.graph_objects as go
import networkx as nx
import random
from fastapi import FastAPI

# List of some European cities with their coordinates
cities = [
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964},
    {"name": "Vienna", "lat": 48.2082, "lon": 16.3738},
    {"name": "Prague", "lat": 50.0755, "lon": 14.4378},
    {"name": "Budapest", "lat": 47.4979, "lon": 19.0402},
    {"name": "Warsaw", "lat": 52.2297, "lon": 21.0122},
    {"name": "Amsterdam", "lat": 52.3676, "lon": 4.9041},
]


# Function to compute the MST and plot it on a map
def plot_mst(num_cities):
    selected_cities = random.sample(cities, num_cities)

    G = nx.Graph()
    for city in selected_cities:
        G.add_node(city["name"], pos=(city["lon"], city["lat"]))

    for i in range(len(selected_cities)):
        for j in range(i + 1, len(selected_cities)):
            city1 = selected_cities[i]
            city2 = selected_cities[j]
            distance = (
                (city1["lat"] - city2["lat"]) ** 2 + (city1["lon"] - city2["lon"]) ** 2
            ) ** 0.5
            G.add_edge(city1["name"], city2["name"], weight=distance)

    mst = nx.minimum_spanning_tree(G)

    edge_x = []
    edge_y = []
    for edge in mst.edges():
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    node_x = [G.nodes[city["name"]]["pos"][0] for city in selected_cities]
    node_y = [G.nodes[city["name"]]["pos"][1] for city in selected_cities]

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lon=edge_x,
            lat=edge_y,
            mode="lines",
            line=dict(width=2, color="blue"),
            hoverinfo="none",
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lon=node_x,
            lat=node_y,
            mode="markers+text",
            marker=dict(size=10, color="red"),
            text=[city["name"] for city in selected_cities],
            textposition="top right",
            hoverinfo="text",
        )
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=go.layout.mapbox.Center(lat=50, lon=10), zoom=3),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


# Gradio interface
with gr.Blocks() as demo:
    num_cities = gr.Slider(
        minimum=2, maximum=len(cities), value=5, step=1, label="Number of Cities"
    )
    plot = gr.Plot()
    btn = gr.Button("Generate MST")

    btn.click(plot_mst, inputs=num_cities, outputs=plot)


app = FastAPI()


@app.get("/")
def read_main():
    return {"message": "This is your main app"}


app = gr.mount_gradio_app(app, demo, path="/gradio")
