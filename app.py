from flask import Flask, render_template, request, send_file, session, redirect, url_for
import pandas as pd
import io

from module_promoleads import REGIOES, buscar_por_estado, extrair_dados

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"  # necessário para sessão

@app.route("/", methods=["GET", "POST"])
def index():
    # Recupera dados previamente buscados (se existirem)
    resultados = session.get("dados", [])

    if request.method == "POST":
        action = request.form.get("action")

        # Se for busca, executa a pesquisa e armazena em sessão
        if action == "search":
            termo    = request.form["termo"]
            regiao   = request.form["regiao"]
            cidade   = request.form.get("cidade", "").strip()
            tipo_tel = request.form["tipo_tel"]
            limite   = int(request.form.get("limite", 120))
            restante = limite

            resultados = []
            for nome, sigla in REGIOES.get(regiao, {}).items():
                if restante <= 0:
                    break
                res_est     = buscar_por_estado(nome, termo)
                dados_est   = extrair_dados(res_est, sigla, cidade, tipo_tel, restante)
                resultados.extend(dados_est)
                restante = limite - len(resultados)

            # armazena em sessão
            session["dados"] = resultados

        # Se for download, apenas gera o Excel a partir da sessão
        elif action == "download":
            resultados = session.get("dados", [])

            df = pd.DataFrame(resultados, columns=["Nome", "Telefone", "Site", "Cidade", "Estado"])
            buf = io.BytesIO()
            df.to_excel(buf, index=False, engine="openpyxl")
            buf.seek(0)

            return send_file(
                buf,
                as_attachment=True,
                download_name="resultados_promotoras.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Após POST de busca, redireciona para GET para evitar reenvio de formulário
        return redirect(url_for("index"))

    # GET: renderiza a página com resultados (ou vazia)
    return render_template("index.html", regioes=REGIOES.keys(), dados=resultados)

if __name__ == "__main__":
    app.run(debug=True)
