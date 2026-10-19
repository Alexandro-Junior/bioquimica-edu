"""Copia o conteúdo curado do app para dentro do servidor do tutor.

    python servidor/atualizar_worker.py

Por que o servidor tem a própria cópia: antes, o app mandava as fichas dos
marcadores junto com cada pergunta, e o servidor repassava ao Gemini o que
chegasse. Como o endereço do servidor vai dentro do APK e do instalador,
qualquer pessoa podia mandar outro texto no lugar das fichas e usar a cota do
Gemini para qualquer coisa. Agora o servidor aceita só a pergunta, a conversa
e a sigla do marcador, e monta o contexto com as fichas daqui.

Rode depois de mudar data/marcadores.csv ou os exemplos de
data/marcadores_extras.json e cole de novo servidor/tutor_worker.js no
Cloudflare (docs/TUTOR_GEMINI.md). O test_tutor.py avisa se esquecer.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from assistente import ficha, linha_exemplo   # noqa: E402  (depois do sys.path)
from mobile import dados                       # noqa: E402

WORKER = RAIZ / "servidor" / "tutor_worker.js"
INICIO = "// <dados do app> gerado por servidor/atualizar_worker.py: não edite à mão\n"
FIM = "// </dados do app>\n"


def bloco_de_dados():
    """As fichas e os exemplos de cada marcador, como o app monta (assistente.py)."""
    marcadores = dados.carregar_marcadores()
    extras = dados.carregar_extras()
    fichas = {m["sigla"]: ficha(m) for m in marcadores}
    exemplos = {m["sigla"]: [linha_exemplo(ex)
                             for ex in extras.get(m["sigla"], {}).get("exemplos", [])[:3]]
                for m in marcadores}
    return (INICIO
            + "const FICHAS = " + json.dumps(fichas, ensure_ascii=False, indent=1) + ";\n"
            + "const EXEMPLOS = " + json.dumps(exemplos, ensure_ascii=False, indent=1) + ";\n"
            + FIM)


def codigo_atualizado(codigo):
    antes, resto = codigo.split(INICIO, 1)
    _velho, depois = resto.split(FIM, 1)
    return antes + bloco_de_dados() + depois


def main():
    codigo = WORKER.read_text(encoding="utf-8")
    novo = codigo_atualizado(codigo)
    if novo == codigo:
        print("servidor/tutor_worker.js já está com o conteúdo atual do app")
        return
    WORKER.write_text(novo, encoding="utf-8", newline="\n")
    print("servidor/tutor_worker.js atualizado: cole de novo no Cloudflare (Edit code › Deploy)")


if __name__ == "__main__":
    main()
