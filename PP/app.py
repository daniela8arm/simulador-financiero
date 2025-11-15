from flask import Flask, render_template, request, redirect, url_for
from graphviz import Digraph
import os

app = Flask(__name__)
os.makedirs("static", exist_ok=True)


@app.route("/")
def inicio():
    return render_template("inicio.html")


@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        try:
            margen = float(request.form["margen"])
            liquidez = float(request.form["liquidez"])
            deuda = float(request.form["deuda"])

            margen_lim = float(request.form["margenLim"])
            liq_lim = float(request.form["liqLim"])
            deuda_lim = float(request.form["deudaLim"])
        except ValueError:
            return render_template(
                "formulario.html",
                error="Datos inválidos. Verifica los números."
            )

        # ------------------------------------------------------------------
        # Árbol de decisión "bonito" con Graphviz
        # ------------------------------------------------------------------
        tree = Digraph(comment="Árbol de decisiones", format="png")

        # Configuración global del gráfico
        tree.attr(rankdir="TB")
        tree.graph_attr.update(
            bgcolor="transparent",
            margin="0.15,0.15",
            pad="0.15",
            dpi="150",
            nodesep="0.35",
            ranksep="0.6",
        )

        # Estilo base para nodos y aristas
        tree.node_attr.update(
            shape="box",
            style="rounded,filled",
            fontname="Poppins",
            fontsize="12",
            color="#00897b",
            penwidth="1.5",
        )

        tree.edge_attr.update(
            fontname="Poppins",
            fontsize="11",
            color="#00695c",
            arrowsize="0.9",
        )

        # Función para crear nodos con colores personalizados
        def nodo(node_id, label, fill="#E0F7FA"):
            tree.node(
                node_id,
                label,
                fillcolor=fill,
                margin="0.25,0.18",
            )

        # Nodo 1: Margen
        nodo("A", f"¿Margen ≥ {margen_lim:.1f}%?", "#B3E5FC")

        if margen < margen_lim:
            nodo("B", "No invertir\n(margen insuficiente)", "#FFCDD2")
            tree.edge("A", "B", label="No")
            decision = "No invertir (margen insuficiente)"

        else:
            # Nodo 2: Liquidez
            nodo("C", f"¿Liquidez ≥ {liq_lim:.1f}?", "#B3E5FC")
            tree.edge("A", "C", label="Sí")

            if liquidez < liq_lim:
                nodo("D", "No invertir\n(liquidez insuficiente)", "#FFCDD2")
                tree.edge("C", "D", label="No")
                decision = "No invertir (liquidez insuficiente)"

            else:
                # Nodo 3: Deuda
                nodo("E", f"¿Deuda ≤ {deuda_lim:.1f}?", "#B3E5FC")
                tree.edge("C", "E", label="Sí")

                if deuda > deuda_lim:
                    nodo("F", "No invertir\n(exceso de deuda)", "#FFCDD2")
                    tree.edge("E", "F", label="No")
                    decision = "No invertir (exceso de deuda)"
                else:
                    nodo("G", "Invertir\n(cumple criterios)", "#C8E6C9")
                    tree.edge("E", "G", label="Sí")
                    decision = "Invertir (cumple criterios)"

        # Guardar imagen en /static/arbol.png
        output_path = os.path.join("static", "arbol")
        tree.render(output_path, cleanup=True)

        return redirect(url_for("resultado", decision=decision))

    return render_template("formulario.html")


@app.route("/resultado")
def resultado():
    decision = request.args.get("decision")
    image_path = "static/arbol.png"
    explicacion = generar_explicacion(decision)
    return render_template(
        "resultado.html",
        decision=decision,
        image_path=image_path,
        explicacion=explicacion,
    )


def generar_explicacion(decision):
    if decision is None:
        return "No se pudo generar una explicación clara."

    if "margen" in decision:
        return "La empresa no cumple con el margen mínimo que estableciste como criterio."
    elif "liquidez" in decision:
        return "La razón corriente es menor al umbral que consideras aceptable."
    elif "deuda" in decision:
        return "El nivel de endeudamiento supera el límite que definiste."
    elif "Invertir" in decision:
        return "La empresa cumple con todos tus criterios financieros. Podría ser una buena opción."
    else:
        return "No se pudo generar una explicación clara."


if __name__ == "__main__":
    app.run(debug=True)
