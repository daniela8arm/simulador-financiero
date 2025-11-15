from flask import Flask, render_template, request, redirect, url_for, send_file
from graphviz import Digraph
import os

app = Flask(__name__)

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
        # Árbol de decisión
        # ------------------------------------------------------------------
        tree = Digraph(comment="Árbol de decisiones", format="png")

        tree.attr(rankdir="TB")
        tree.graph_attr.update(
            bgcolor="transparent",
            margin="0.15,0.15",
            pad="0.15",
            dpi="150",
            nodesep="0.35",
            ranksep="0.6",
        )

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

        def nodo(node_id, label, fill="#E0F7FA"):
            tree.node(
                node_id,
                label,
                fillcolor=fill,
                margin="0.25,0.18",
            )

        nodo("A", f"¿Margen ≥ {margen_lim:.1f}%?", "#B3E5FC")

        if margen < margen_lim:
            nodo("B", "No invertir\n(margen insuficiente)", "#FFCDD2")
            tree.edge("A", "B", label="No")
            decision = "No invertir (margen insuficiente)"

        else:
            nodo("C", f"¿Liquidez ≥ {liq_lim:.1f}?", "#B3E5FC")
            tree.edge("A", "C", label="Sí")

            if liquidez < liq_lim:
                nodo("D", "No invertir\n(liquidez insuficiente)", "#FFCDD2")
                tree.edge("C", "D", label="No")
                decision = "No invertir (liquidez insuficiente)"

            else:
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

        # ------------ AQUÍ EL CAMBIO IMPORTANTE --------------
        # Guardar imagen en /tmp (Render permite escribir ahí)
        output_path = "/tmp/arbol"
        tree.render(output_path, cleanup=True)
        # Archivo final: /tmp/arbol.png
        # ------------------------------------------------------

        return redirect(url_for("resultado", decision=decision))

    return render_template("formulario.html")


@app.route("/resultado")
def resultado():
    decision = request.args.get("decision")
    explicacion = generar_explicacion(decision)

    # enviar ruta interna
    return render_template(
        "resultado.html",
        decision=decision,
        explicacion=explicacion,
        image_path="/resultado_imagen"
    )


# Ruta que sirve la imagen generada en /tmp
@app.route("/resultado_imagen")
def resultado_imagen():
    return send_file("/tmp/arbol.png", mimetype="image/png")


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
    app.run(host="0.0.0.0", port=10000)
