#!/usr/bin/env python3
"""
Gera imagens educacionais para marcadores bioquímicos
Cria diagramas em PNG para a aba Imagens
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

IMG_DIR = Path("data/images")
IMG_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────
# 1. ALT - Localização
# ──────────────────────────────────────────
def criar_alt_localizacao():
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Título
    ax.text(5, 9.5, 'Localização da ALT no Corpo', fontsize=18, fontweight='bold', ha='center')

    # Fígado
    fígado = patches.FancyBboxPatch((2, 5), 3, 2.5, boxstyle="round,pad=0.1",
                                     edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=3)
    ax.add_patch(fígado)
    ax.text(3.5, 6.5, 'FÍGADO', fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(3.5, 5.8, 'ALT: ~90%', fontsize=11, ha='center', va='center')
    ax.text(3.5, 5.3, 'Citoplasma', fontsize=10, ha='center', va='center', style='italic')

    # Coração
    coração = patches.FancyBboxPatch((6, 5), 2.5, 2.5, boxstyle="round,pad=0.1",
                                      edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(coração)
    ax.text(7.25, 6.5, 'CORAÇÃO', fontsize=12, fontweight='bold', ha='center', va='center')
    ax.text(7.25, 5.8, 'ALT: ~5%', fontsize=10, ha='center', va='center')

    # Músculos
    musculos = patches.FancyBboxPatch((2, 2), 2.5, 2, boxstyle="round,pad=0.1",
                                       edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2)
    ax.add_patch(musculos)
    ax.text(3.25, 3.3, 'MÚSCULOS', fontsize=12, fontweight='bold', ha='center', va='center')
    ax.text(3.25, 2.6, 'ALT: ~3%', fontsize=10, ha='center', va='center')

    # Rins
    rins = patches.FancyBboxPatch((6, 2), 2.5, 2, boxstyle="round,pad=0.1",
                                   edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(rins)
    ax.text(7.25, 3.3, 'RINS', fontsize=12, fontweight='bold', ha='center', va='center')
    ax.text(7.25, 2.6, 'ALT: ~2%', fontsize=10, ha='center', va='center')

    # Legenda
    ax.text(5, 0.8, 'ALT é marcador ESPECÍFICO para lesão hepática',
            fontsize=11, ha='center', style='italic', color='#16A44A', fontweight='bold')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'alt_localizacao.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("alt_localizacao.png")
    plt.close()

# ──────────────────────────────────────────
# 2. ALT - Padrão de elevação
# ──────────────────────────────────────────
def criar_alt_padrao():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    dias = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Hepatite viral (pico alto)
    hepatite = np.array([100, 500, 1200, 1500, 1200, 800, 500, 300, 150, 80, 50])

    # Cirrose (moderado)
    cirrose = np.array([100, 120, 130, 135, 140, 138, 135, 133, 130, 128, 125])

    # Valores normais
    normal = np.array([40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40])

    ax.plot(dias, hepatite, marker='o', linewidth=3, markersize=8, label='Hepatite Viral', color='#E11D48')
    ax.plot(dias, cirrose, marker='s', linewidth=2, markersize=7, label='Cirrose Hepática', color='#F69E3D')
    ax.axhline(y=56, color='#16A44A', linestyle='--', linewidth=2, label='Limite Normal (56 U/L)')

    ax.set_xlabel('Dias após início', fontsize=12, fontweight='bold')
    ax.set_ylabel('ALT (U/L)', fontsize=12, fontweight='bold')
    ax.set_title('Padrão de Elevação de ALT em Diferentes Doenças', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1600)

    # Anotações
    ax.annotate('Pico agudo\n(hepatite)', xy=(3, 1500), xytext=(4, 1350),
                arrowprops=dict(arrowstyle='->', color='#E11D48', lw=2),
                fontsize=10, ha='center', color='#E11D48', fontweight='bold')

    ax.annotate('Elevação crônica\n(cirrose)', xy=(5, 138), xytext=(7, 400),
                arrowprops=dict(arrowstyle='->', color='#F69E3D', lw=2),
                fontsize=10, ha='center', color='#F69E3D', fontweight='bold')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'alt_padrao.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("alt_padrao.png")
    plt.close()

# ──────────────────────────────────────────
# 3. AST - Distribuição
# ──────────────────────────────────────────
def criar_ast_distribuicao():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    tecidos = ['Fígado', 'Coração', 'Músculos\nEsqueléticos', 'Rins', 'Hemácias', 'Outros']
    percentuais = [30, 20, 25, 10, 10, 5]
    cores = ['#16A44A', '#E11D48', '#1D88B2', '#7C3A92', '#F69E3D', '#A1887F']

    wedges, texts, autotexts = ax.pie(percentuais, labels=tecidos, autopct='%1.0f%%',
                                        colors=cores, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    ax.set_title('Distribuição de AST no Corpo\n(Menos específica que ALT)',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'ast_distribuicao.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("ast_distribuicao.png")
    plt.close()

# ──────────────────────────────────────────
# 4. AST/ALT Ratio
# ──────────────────────────────────────────
def criar_ast_alt_ratio():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    condicoes = ['Normal', 'Hepatite\nViral', 'Hepatite\nAlcoólica', 'Cirrose', 'Esteatose']
    ast_alt_ratio = [0.8, 0.6, 2.5, 2.0, 0.7]
    cores = ['#16A44A', '#F69E3D', '#E11D48', '#7C3A92', '#1D88B2']

    bars = ax.bar(condicoes, ast_alt_ratio, color=cores, edgecolor='black', linewidth=2)

    # Linha de referência
    ax.axhline(y=1, color='black', linestyle='--', linewidth=2, label='AST = ALT (ratio = 1)')

    # Labels nos bars
    for i, (bar, ratio) in enumerate(zip(bars, ast_alt_ratio)):
        altura = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, altura + 0.1,
                f'{ratio:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Razão AST/ALT', fontsize=12, fontweight='bold')
    ax.set_title('Razão AST/ALT em Diferentes Condições Hepáticas', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 3)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Anotação
    ax.text(3, 2.3, 'AST > ALT sugere\nalcoolismo crônico',
            fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.8))

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'ast_alt_ratio.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("ast_alt_ratio.png")
    plt.close()

# ──────────────────────────────────────────
# 5. Creatinina - Metabolismo
# ──────────────────────────────────────────
def criar_creatinina_metabolismo():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(5, 9.5, 'Metabolismo da Creatinina', fontsize=16, fontweight='bold', ha='center')

    # Box 1: Fígado / rim - síntese de creatina
    box1 = patches.FancyBboxPatch((0.4, 6.4), 2.6, 2.1, boxstyle="round,pad=0.1",
                                   edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(box1)
    ax.text(1.7, 7.9, 'Fígado e Rim', fontsize=11, fontweight='bold', ha='center')
    ax.text(1.7, 7.1, 'Sintetizam\nCreatina', fontsize=9, ha='center')

    # Seta 1
    ax.annotate('', xy=(3.5, 7.45), xytext=(3.05, 7.45),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Box 2: Músculo - conversão espontânea
    box2 = patches.FancyBboxPatch((3.55, 6.4), 2.6, 2.1, boxstyle="round,pad=0.1",
                                   edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2)
    ax.add_patch(box2)
    ax.text(4.85, 7.9, 'Músculo', fontsize=11, fontweight='bold', ha='center')
    ax.text(4.85, 7.0, 'Creatina e fosfocreatina\nviram Creatinina\n(reação espontânea)',
            fontsize=8, ha='center')

    # Seta 2
    ax.annotate('', xy=(6.65, 7.45), xytext=(6.2, 7.45),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Box 3: Sangue
    box3 = patches.FancyBboxPatch((6.7, 6.4), 2.9, 2.1, boxstyle="round,pad=0.1",
                                   edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(box3)
    ax.text(8.15, 7.9, 'Sangue', fontsize=11, fontweight='bold', ha='center')
    ax.text(8.15, 7.1, 'Creatinina sérica\n(0.6-1.2 mg/dL)', fontsize=9, ha='center')

    # Seta 3 (Sangue -> filtração renal)
    ax.annotate('', xy=(8.15, 5.55), xytext=(8.15, 6.3),
                arrowprops=dict(arrowstyle='->', lw=3, color='black'))
    ax.text(8.35, 5.95, 'Filtração\nglomerular', fontsize=8, ha='left', va='center')

    # Box 4: Urina
    box4 = patches.FancyBboxPatch((6.7, 3.9), 2.9, 1.6, boxstyle="round,pad=0.1",
                                   edgecolor='#F69E3D', facecolor='#FFE0B2', linewidth=2)
    ax.add_patch(box4)
    ax.text(8.15, 4.9, 'URINA', fontsize=11, fontweight='bold', ha='center')
    ax.text(8.15, 4.3, 'Excreção renal', fontsize=9, ha='center')

    # Info box
    info = patches.FancyBboxPatch((0.4, 0.6), 5.9, 4.9, boxstyle="round,pad=0.15",
                                   edgecolor='#7C3A92', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(info)
    ax.text(3.35, 4.9, 'Importante:', fontsize=11, fontweight='bold', ha='center', color='#7C3A92')
    ax.text(3.35, 4.1, 'Produção diária praticamente constante,\nproporcional à massa muscular',
            fontsize=9, ha='center')
    ax.text(3.35, 3.1, 'O rim não produz creatinina:\nele a filtra e excreta',
            fontsize=9, ha='center')
    ax.text(3.35, 2.1, 'Creatinina alta no sangue indica\nqueda da filtração glomerular',
            fontsize=9, ha='center')
    ax.text(3.35, 1.15, 'Massa muscular baixa pode mascarar\ndoença renal (creatinina falsamente normal)',
            fontsize=8, ha='center', style='italic', color='#7C3A92')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'creatinina_metabolismo.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("creatinina_metabolismo.png")
    plt.close()

# ──────────────────────────────────────────
# 6. Creatinina - Função Renal
# ──────────────────────────────────────────
def criar_creatinina_funcao():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    egfr = np.linspace(100, 10, 100)
    creatinina = 80 / (egfr + 5)  # Relação aproximada

    ax.plot(egfr, creatinina, linewidth=3, color='#E11D48')
    ax.fill_between(egfr, creatinina, alpha=0.3, color='#E11D48')

    # Linhas de referência
    ax.axhline(y=1.2, color='#16A44A', linestyle='--', linewidth=2, label='Normal (1.2 mg/dL)')
    ax.axvline(x=60, color='#F69E3D', linestyle='--', linewidth=2, label='eGFR 60 (DRC estágio 3a)')
    ax.axvline(x=30, color='#7C3A92', linestyle='--', linewidth=2, label='eGFR 30 (DRC estágio 4)')
    ax.axvline(x=15, color='#A1887F', linestyle='--', linewidth=2, label='eGFR 15 (DRC estágio 5)')

    ax.set_xlabel('Taxa de Filtração Glomerular — eGFR (mL/min/1.73m²)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Creatinina Sérica (mg/dL)', fontsize=12, fontweight='bold')
    ax.set_title('Relação Exponencial: eGFR vs Creatinina', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(100, 10)
    ax.set_ylim(0, 10)

    # Anotação
    ax.text(50, 8, 'Pequenas mudanças em creatinina\nindicam GRANDES mudanças em função renal',
            fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.9),
            fontweight='bold', color='#E11D48')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'creatinina_funcao.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("creatinina_funcao.png")
    plt.close()

# ──────────────────────────────────────────
# 7. Glicose - Homeostase
# ──────────────────────────────────────────
def criar_glicose_homeostase():
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(5, 9.5, 'Homeostase da Glicose', fontsize=16, fontweight='bold', ha='center')

    # Intestino
    box_int = patches.FancyBboxPatch((1, 7), 2.5, 1.5, boxstyle="round,pad=0.1",
                                      edgecolor='#F69E3D', facecolor='#FFE0B2', linewidth=2)
    ax.add_patch(box_int)
    ax.text(2.25, 7.9, 'Intestino', fontsize=10, fontweight='bold', ha='center')
    ax.text(2.25, 7.4, 'Absorção', fontsize=9, ha='center')

    # Sangue
    ellipse = patches.Ellipse((5, 7.5), 3, 1.5, edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(ellipse)
    ax.text(5, 7.5, 'SANGUE\n(Glicose 70-99 mg/dL)', fontsize=11, fontweight='bold', ha='center', va='center')

    # Célula com insulina
    box_cel = patches.FancyBboxPatch((6.5, 7), 2.5, 1.5, boxstyle="round,pad=0.1",
                                      edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2)
    ax.add_patch(box_cel)
    ax.text(7.75, 7.9, 'Célula', fontsize=10, fontweight='bold', ha='center')
    ax.text(7.75, 7.4, 'Com Insulina →\nCaptação', fontsize=9, ha='center')

    # Fígado
    box_fig = patches.FancyBboxPatch((1, 4.5), 3, 1.8, boxstyle="round,pad=0.1",
                                      edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(box_fig)
    ax.text(2.5, 5.6, 'Fígado', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.5, 5.1, 'Armazena Glicogênio\n(Baixa glicose)\nLibera Glicose\n(Alta glicose)',
            fontsize=8, ha='center')

    # Pâncreas
    box_panc = patches.FancyBboxPatch((6, 4.5), 3, 1.8, boxstyle="round,pad=0.1",
                                       edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(box_panc)
    ax.text(7.5, 5.6, 'Pâncreas', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.5, 5.1, 'Células β:\n↑ Glicose → Insulina ↑\n↓ Glicose → Glucagon ↑',
            fontsize=8, ha='center')

    # Setas
    ax.annotate('', xy=(3.7, 7.5), xytext=(3.5, 7.5), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(6.5, 7.5), xytext=(6.3, 7.5), arrowprops=dict(arrowstyle='->', lw=2))

    # Legendas de setas
    ax.text(4.3, 5.2, 'Insulina facilita\ncaptação de glicose', fontsize=9, ha='center',
            bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.8))

    # Tipos de Diabetes
    diabetes_box = patches.FancyBboxPatch((0.5, 1.5), 9, 2.5, boxstyle="round,pad=0.15",
                                          edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(diabetes_box)
    ax.text(5, 3.6, 'Tipos de Diabetes', fontsize=11, fontweight='bold', ha='center', color='#E11D48')
    ax.text(2.5, 3, 'Tipo 1: Falta insulina\n(Pâncreas não produz)', fontsize=9, ha='center')
    ax.text(5, 3, 'Tipo 2: Resistência à insulina\n(Células não respondem)', fontsize=9, ha='center')
    ax.text(7.5, 3, 'Gestacional: Gravidez\n(Insulina aumenta mas\ninsufiça)', fontsize=9, ha='center')

    ax.text(5, 1.8, 'Glicose alta (Hiperglicemia) → Poliúria, Polidipsia, Cetose',
            fontsize=9, ha='center', style='italic', color='#E11D48', fontweight='bold')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'glicose_homeostase.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("glicose_homeostase.png")
    plt.close()

# ──────────────────────────────────────────
# 8. Glicose - TTOG
# ──────────────────────────────────────────
def criar_glicose_ttog():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    tempo = np.array([0, 30, 60, 90, 120])

    # Normal
    normal = np.array([80, 120, 110, 100, 90])

    # Intolerância à glicose
    igt = np.array([90, 160, 180, 160, 140])

    # Diabetes
    diabetes = np.array([110, 200, 220, 210, 200])

    ax.plot(tempo, normal, marker='o', linewidth=3, markersize=8, label='Normal', color='#16A44A')
    ax.plot(tempo, igt, marker='s', linewidth=3, markersize=8, label='Intolerância à Glicose', color='#F69E3D')
    ax.plot(tempo, diabetes, marker='^', linewidth=3, markersize=8, label='Diabetes', color='#E11D48')

    # Linhas de referência
    ax.axhline(y=100, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax.axhline(y=140, color='#F69E3D', linestyle='--', linewidth=2, alpha=0.7, label='Limite IGT (140 mg/dL em 2h)')
    ax.axhline(y=200, color='#E11D48', linestyle='--', linewidth=2, alpha=0.7, label='Limite Diabetes (200 mg/dL em 2h)')

    # Anotação
    ax.axvspan(0, 30, alpha=0.1, color='gray', label='Ingestão de 75g glicose')
    ax.text(15, 240, '← Ingestão de 75g glicose', fontsize=10, ha='center', fontweight='bold')

    ax.set_xlabel('Tempo (minutos)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Glicose (mg/dL)', fontsize=12, fontweight='bold')
    ax.set_title('Teste de Tolerância Oral à Glicose (TTOG)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-5, 130)
    ax.set_ylim(70, 250)

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'glicose_ttog.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("glicose_ttog.png")
    plt.close()

# ──────────────────────────────────────────
# 9. Colesterol - Estrutura
# ──────────────────────────────────────────
def criar_colesterol_estrutura():
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(5, 9.5, 'Colesterol e Aterosclerose', fontsize=16, fontweight='bold', ha='center')

    # Molécula normal
    ax.text(2.5, 8.5, 'Colesterol Normal', fontsize=12, fontweight='bold', ha='center', color='#16A44A')
    circle1 = patches.Circle((2.5, 7.5), 0.8, edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(circle1)
    ax.text(2.5, 7.5, 'C', fontsize=20, fontweight='bold', ha='center', va='center', color='#16A44A')
    ax.text(2.5, 6.5, 'Essencial para:\n- Membranas\n- Hormônios\n- Vitamina D',
            fontsize=9, ha='center')

    # Placa de aterosclerose
    ax.text(7.5, 8.5, 'Aterosclerose (Excesso)', fontsize=12, fontweight='bold', ha='center', color='#E11D48')
    ax.add_patch(patches.Wedge((7.5, 7), 1, 0, 360, width=0.4, edgecolor='#E11D48', facecolor='#FFE0B2', linewidth=2))
    ax.text(7.5, 7, 'LDL', fontsize=12, fontweight='bold', ha='center', va='center', color='#E11D48')

    # Vaso sanguíneo
    ax.add_patch(patches.Rectangle((5.5, 5), 4, 1.5, edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2))
    ax.text(7.5, 5.75, 'Artéria', fontsize=11, fontweight='bold', ha='center', va='center')

    # Depósito de colesterol
    ax.add_patch(patches.Wedge((6, 4.5), 0.6, 0, 180, edgecolor='#E11D48', facecolor='#FFE0B2', linewidth=2))
    ax.text(6, 4.2, 'Placa', fontsize=9, fontweight='bold', ha='center')

    ax.add_patch(patches.Wedge((7.5, 4.5), 0.6, 0, 180, edgecolor='#E11D48', facecolor='#FFE0B2', linewidth=2))
    ax.text(7.5, 4.2, 'Placa', fontsize=9, fontweight='bold', ha='center')

    ax.add_patch(patches.Wedge((9, 4.5), 0.6, 0, 180, edgecolor='#E11D48', facecolor='#FFE0B2', linewidth=2))
    ax.text(9, 4.2, 'Placa', fontsize=9, fontweight='bold', ha='center')

    # Risco
    risk_box = patches.FancyBboxPatch((0.5, 1.5), 9, 2, boxstyle="round,pad=0.15",
                                       edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(risk_box)
    ax.text(5, 3.1, 'Risco Cardiovascular ↑', fontsize=11, fontweight='bold', ha='center', color='#E11D48')
    ax.text(5, 2.5, 'LDL > 130: Risco moderado | LDL > 190: Risco muito alto',
            fontsize=9, ha='center')
    ax.text(5, 2, 'HDL alto é protetor (>60 mg/dL reduz risco)',
            fontsize=9, ha='center', color='#16A44A', fontweight='bold')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'colesterol_estrutura.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("colesterol_estrutura.png")
    plt.close()

# ──────────────────────────────────────────
# 10. Colesterol - Lipoproteínas
# ──────────────────────────────────────────
def criar_colesterol_lipoproteinas():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    lipoproteinas = ['Quilomícron', 'VLDL', 'IDL', 'LDL', 'HDL']
    tamanho = [1000, 70, 28, 18, 10]  # nm
    densidade = [0.95, 1.006, 1.019, 1.063, 1.21]  # g/cm³
    cores = ['#F69E3D', '#E11D48', '#1D88B2', '#7C3A92', '#16A44A']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='white')

    # Gráfico 1: Tamanho
    bars1 = ax1.bar(lipoproteinas, tamanho, color=cores, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Tamanho (nm)', fontsize=12, fontweight='bold')
    ax1.set_title('Tamanho das Lipoproteínas', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 1100)
    for bar in bars1:
        altura = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, altura + 20,
                f'{int(altura)} nm', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Gráfico 2: Densidade
    bars2 = ax2.bar(lipoproteinas, densidade, color=cores, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Densidade (g/cm³)', fontsize=12, fontweight='bold')
    ax2.set_title('Densidade das Lipoproteínas', fontsize=13, fontweight='bold')
    ax2.set_ylim(0.9, 1.25)
    for bar in bars2:
        altura = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, altura + 0.02,
                f'{altura:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Legenda
    fig.text(0.5, 0.02, 'LDL pequeno e denso = Mais aterogênico | HDL grande = Protetor cardiovascular',
            ha='center', fontsize=11, style='italic', fontweight='bold', color='#E11D48',
            bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.8))

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'colesterol_lipoproteinas.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("colesterol_lipoproteinas.png")
    plt.close()

# ──────────────────────────────────────────
# 11. Potássio - Bomba Na+/K+
# ──────────────────────────────────────────
def criar_potassio_bomba():
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(5, 9.5, 'Bomba Na⁺/K⁺ ATPase', fontsize=16, fontweight='bold', ha='center')

    # Exterior (sangue)
    ext_box = patches.Rectangle((1, 6.5), 8, 2.5, edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(ext_box)
    ax.text(9.2, 7.75, 'EXTERIOR\n(Sangue)', fontsize=10, fontweight='bold', ha='left', va='center')

    # Membrana
    membrane = patches.Rectangle((1, 5.8), 8, 0.7, edgecolor='black', facecolor='#D7CCC8', linewidth=2)
    ax.add_patch(membrane)
    ax.text(0.5, 6.15, 'Membrana', fontsize=9, fontweight='bold', ha='right', va='center')

    # Interior (célula)
    int_box = patches.Rectangle((1, 2.3), 8, 3.5, edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2)
    ax.add_patch(int_box)
    ax.text(9.2, 4, 'INTERIOR\n(Célula)', fontsize=10, fontweight='bold', ha='left', va='center')

    # Bomba
    pump = patches.FancyBboxPatch((3.5, 5.9), 3, 0.5, boxstyle="round,pad=0.05",
                                   edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(pump)
    ax.text(5, 6.15, 'Bomba Na⁺/K⁺', fontsize=11, fontweight='bold', ha='center', va='center')

    # Na+ fora
    circle_na_out = patches.Circle((2.5, 7.7), 0.4, edgecolor='#1D88B2', facecolor='#90CAF9', linewidth=2)
    ax.add_patch(circle_na_out)
    ax.text(2.5, 7.7, 'Na⁺', fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(2.5, 6.8, 'Alto', fontsize=9, ha='center', fontweight='bold')

    # K+ dentro
    circle_k_in = patches.Circle((7.5, 3.3), 0.4, edgecolor='#E11D48', facecolor='#FFCDD2', linewidth=2)
    ax.add_patch(circle_k_in)
    ax.text(7.5, 3.3, 'K⁺', fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(7.5, 2.4, 'Alto', fontsize=9, ha='center', fontweight='bold')

    # Na+ dentro (baixo)
    circle_na_in = patches.Circle((2.5, 3.3), 0.35, edgecolor='#1D88B2', facecolor='#90CAF9', linewidth=2)
    ax.add_patch(circle_na_in)
    ax.text(2.5, 3.3, 'Na⁺', fontsize=9, fontweight='bold', ha='center', va='center')
    ax.text(2.5, 2.4, 'Baixo', fontsize=8, ha='center', fontweight='bold')

    # K+ fora (baixo)
    circle_k_out = patches.Circle((7.5, 7.7), 0.35, edgecolor='#E11D48', facecolor='#FFCDD2', linewidth=2)
    ax.add_patch(circle_k_out)
    ax.text(7.5, 7.7, 'K⁺', fontsize=9, fontweight='bold', ha='center', va='center')
    ax.text(7.5, 6.8, 'Baixo', fontsize=8, ha='center', fontweight='bold')

    # Setas
    ax.annotate('', xy=(4.5, 6.2), xytext=(3.5, 7.3),
                arrowprops=dict(arrowstyle='->', lw=2, color='#1D88B2'))
    ax.annotate('', xy=(6.5, 6.2), xytext=(7.5, 3.7),
                arrowprops=dict(arrowstyle='->', lw=2, color='#E11D48'))

    # ATP
    ax.text(5, 5.4, 'ATP', fontsize=10, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round', facecolor='#FFEB3B', alpha=0.8))

    # Info
    info_box = patches.FancyBboxPatch((0.5, 0.2), 9, 2, boxstyle="round,pad=0.1",
                                       edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(info_box)
    ax.text(5, 1.9, 'Bomba ativa (consome ATP)', fontsize=10, fontweight='bold', ha='center')
    ax.text(5, 1.5, 'Expulsa 3 Na⁺ para fora | Traz 2 K⁺ para dentro',
            fontsize=9, ha='center')
    ax.text(5, 1, 'Digoxina inibe a bomba | Diuréticos de alça/tiazídicos causam hipocalemia',
            fontsize=9, ha='center', color='#E11D48', fontweight='bold')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'potassio_bomba.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("potassio_bomba.png")
    plt.close()

# ──────────────────────────────────────────
# 12. Potássio - ECG
# ──────────────────────────────────────────
def criar_potassio_ecg():
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), facecolor='white', sharex=True)

    t = np.linspace(0, 2.4, 2400)

    def gauss(t, centro, largura, altura):
        return altura * np.exp(-((t - centro) ** 2) / (2 * largura ** 2))

    def batimento(fase, p=0.15, t_altura=0.35, t_largura=0.040, u=0.0):
        onda = gauss(fase, 0.16, 0.022, p)                      # onda P
        onda += gauss(fase, 0.30, 0.006, -0.10)                 # Q
        onda += gauss(fase, 0.33, 0.008, 1.0)                   # R
        onda += gauss(fase, 0.36, 0.007, -0.22)                 # S
        onda += gauss(fase, 0.56, t_largura, t_altura)          # onda T
        if u:
            onda += gauss(fase, 0.72, 0.030, u)                 # onda U
        return onda

    def traçado(**kw):
        fase = t % 0.8
        return batimento(fase, **kw)

    cenarios = [
        ("K+ normal (3.5-5.0 mEq/L)", '#16A44A', dict(), []),
        ("Hipocalemia (K+ 2.8 mEq/L)", '#1D88B2',
         dict(t_altura=0.12, t_largura=0.045, u=0.18),
         [(0.56, 0.12, 1.30, 'onda T achatada'), (0.72, 0.18, 2.05, 'onda U proeminente')]),
        ("Hipercalemia (K+ 6.8 mEq/L)", '#E11D48',
         dict(p=0.03, t_altura=0.75, t_largura=0.020),
         [(0.16, 0.03, 0.35, 'onda P reduzida'), (0.56, 0.75, 1.75, 'onda T apiculada (em tenda)')]),
    ]

    for ax, (titulo, cor, kw, marcas) in zip(axes, cenarios):
        ax.plot(t, traçado(**kw), linewidth=1.8, color=cor)
        ax.set_ylabel(titulo, fontsize=9, fontweight='bold', color=cor)
        ax.set_ylim(-0.45, 1.7)
        ax.grid(True, alpha=0.25)
        ax.set_yticks([])
        for fase_x, altura, texto_x, rotulo in marcas:
            ax.annotate(rotulo, xy=(0.8 + fase_x, altura + 0.04), xytext=(texto_x, 1.45),
                        arrowprops=dict(arrowstyle='->', color=cor, lw=1.4),
                        fontsize=9, color=cor, fontweight='bold', ha='center', va='top')

    axes[0].set_title('Alterações Eletrocardiográficas com Potássio', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Tempo (segundos)', fontsize=11, fontweight='bold')

    fig.text(0.5, 0.005,
             'Hipercalemia progressiva: onda T apiculada -> P achatada -> QRS alargado -> risco de fibrilação ventricular',
             fontsize=9.5, ha='center', style='italic', color='#E11D48', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.9))

    plt.tight_layout(rect=(0, 0.04, 1, 1))
    plt.savefig(IMG_DIR / 'potassio_ecg.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("potassio_ecg.png")
    plt.close()

# ──────────────────────────────────────────
# 13. Troponina - Sarcômero
# ──────────────────────────────────────────
def criar_troponina_sarcomero():
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    ax.text(6, 5.7, 'Estrutura do Sarcômero e Troponina', fontsize=16, fontweight='bold', ha='center')

    # Filamento grosso (miosina)
    thick = patches.Rectangle((1, 2.5), 4, 0.8, edgecolor='#E11D48', facecolor='#FFCDD2', linewidth=2)
    ax.add_patch(thick)
    ax.text(3, 3, 'Filamento Grosso\n(Miosina)', fontsize=10, fontweight='bold', ha='center', va='center')

    # Filamento fino (actina)
    thin = patches.Rectangle((2, 1.5), 3, 0.6, edgecolor='#1D88B2', facecolor='#B3E5FC', linewidth=2)
    ax.add_patch(thin)
    ax.text(3.5, 1.8, 'Filamento Fino (Actina)', fontsize=9, fontweight='bold', ha='center', va='center')

    # Troponina
    trop = patches.FancyBboxPatch((4.3, 1.4), 1.2, 0.8, boxstyle="round,pad=0.05",
                                   edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(trop)
    ax.text(4.9, 1.8, 'Troponina', fontsize=9, fontweight='bold', ha='center', va='center')

    # Tropomiosina
    ax.plot([5, 5.8], [1.6, 1.6], linewidth=3, color='#F69E3D')
    ax.text(5.4, 1.3, 'Tropomiosina', fontsize=8, ha='center')

    # Contração
    contract = patches.FancyBboxPatch((7, 1.2), 4.5, 2.5, boxstyle="round,pad=0.1",
                                       edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(contract)
    ax.text(9.25, 3.2, 'Mecanismo de Contração', fontsize=11, fontweight='bold', ha='center')
    ax.text(9.25, 2.7, 'Ca²⁺ se liga à Troponina', fontsize=9, ha='center')
    ax.text(9.25, 2.3, 'Troponina muda forma', fontsize=9, ha='center')
    ax.text(9.25, 1.9, 'Tropomiosina se move', fontsize=9, ha='center')
    ax.text(9.25, 1.5, 'Miosina puxa actina', fontsize=9, ha='center')

    # Necrose
    necrose_box = patches.FancyBboxPatch((0.5, 0.1), 11, 0.8, boxstyle="round,pad=0.05",
                                          edgecolor='#E11D48', facecolor='#FECDD3', linewidth=2)
    ax.add_patch(necrose_box)
    ax.text(6, 0.5, 'INFARTO: Necrose do músculo cardíaco → Troponina LIBERADA no sangue (marcador altamente específico)',
            fontsize=10, fontweight='bold', ha='center', va='center', color='#E11D48')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'troponina_sarcomero.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("troponina_sarcomero.png")
    plt.close()

# ──────────────────────────────────────────
# 14. Troponina - Cinética
# ──────────────────────────────────────────
def criar_troponina_cinetica():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    dias = np.array([0, 1, 2, 3, 4, 5, 6, 7, 14])
    troponina = np.array([0.02, 0.5, 2.5, 5, 3.5, 1.5, 0.5, 0.15, 0.04])

    ax.plot(dias, troponina, marker='o', linewidth=3, markersize=10, color='#E11D48')
    ax.fill_between(dias, troponina, alpha=0.2, color='#E11D48')

    # Linhas de referência
    ax.axhline(y=0.04, color='#16A44A', linestyle='--', linewidth=2, label='Normal (< 0.04 ng/mL)')

    # Sombra de elevação
    ax.axvspan(0.5, 7, alpha=0.1, color='#E11D48', label='Período de elevação')

    # Anotações
    ax.annotate('Eleva em 3-4h', xy=(0.5, 0.5), xytext=(1.5, 1.5),
                arrowprops=dict(arrowstyle='->', color='#E11D48', lw=2),
                fontsize=10, ha='center', color='#E11D48', fontweight='bold')

    ax.annotate('Pico em 24-48h', xy=(3.5, 5), xytext=(4.5, 6),
                arrowprops=dict(arrowstyle='->', color='#E11D48', lw=2),
                fontsize=10, ha='center', color='#E11D48', fontweight='bold')

    ax.annotate('Normaliza em 7-14 dias', xy=(14, 0.04), xytext=(12, 1),
                arrowprops=dict(arrowstyle='->', color='#E11D48', lw=2),
                fontsize=10, ha='center', color='#E11D48', fontweight='bold')

    ax.set_xlabel('Dias após início do infarto', fontsize=12, fontweight='bold')
    ax.set_ylabel('Troponina I (ng/mL)', fontsize=12, fontweight='bold')
    ax.set_title('Cinética de Troponina após Infarto do Miocárdio', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.2, 6)
    ax.set_xlim(-0.5, 15)

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'troponina_cinetica.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("troponina_cinetica.png")
    plt.close()

# ──────────────────────────────────────────
# 15. Bilirrubina - Metabolismo
# ──────────────────────────────────────────
def criar_bilirrubina_metabolismo():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    ax.text(6, 9.5, 'Metabolismo da Bilirrubina', fontsize=16, fontweight='bold', ha='center')

    # 1. Hemácia
    box1 = patches.FancyBboxPatch((0.5, 7), 2, 1.8, boxstyle="round,pad=0.1",
                                   edgecolor='#E11D48', facecolor='#FFCDD2', linewidth=2)
    ax.add_patch(box1)
    ax.text(1.5, 8.2, 'Hemácia', fontsize=10, fontweight='bold', ha='center')
    ax.text(1.5, 7.6, 'Destruição\n(120 dias)', fontsize=8, ha='center')

    # Seta 1
    ax.annotate('', xy=(3.2, 8), xytext=(2.5, 8),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(2.85, 8.3, 'Heme', fontsize=8, ha='center', fontweight='bold')

    # 2. Baço
    box2 = patches.FancyBboxPatch((3.2, 7), 2, 1.8, boxstyle="round,pad=0.1",
                                   edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(box2)
    ax.text(4.2, 8.2, 'Baço', fontsize=10, fontweight='bold', ha='center')
    ax.text(4.2, 7.6, 'Bilirrubina\nINDIRETA', fontsize=8, ha='center')

    # Seta 2
    ax.annotate('', xy=(5.9, 8), xytext=(5.2, 8),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5.55, 8.3, 'Sangue', fontsize=8, ha='center', fontweight='bold')

    # 3. Fígado
    box3 = patches.FancyBboxPatch((5.9, 7), 2, 1.8, boxstyle="round,pad=0.1",
                                   edgecolor='#16A44A', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(box3)
    ax.text(6.9, 8.2, 'Fígado', fontsize=10, fontweight='bold', ha='center')
    ax.text(6.9, 7.6, 'Conjuga\nBilirrubina', fontsize=8, ha='center')

    # Seta 3
    ax.annotate('', xy=(8.6, 8), xytext=(7.9, 8),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(8.25, 8.3, 'Sangue', fontsize=8, ha='center', fontweight='bold')

    # 4. Bile/Intestino
    box4 = patches.FancyBboxPatch((8.6, 7), 2.5, 1.8, boxstyle="round,pad=0.1",
                                   edgecolor='#F69E3D', facecolor='#FFE0B2', linewidth=2)
    ax.add_patch(box4)
    ax.text(9.85, 8.2, 'Bile/Intestino', fontsize=10, fontweight='bold', ha='center')
    ax.text(9.85, 7.6, 'Bilirrubina\nDIRETA', fontsize=8, ha='center')

    # Seta 4 (Bile/Intestino -> Fezes)
    ax.annotate('', xy=(9.85, 5.8), xytext=(9.85, 6.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # 5. Fezes
    box5 = patches.FancyBboxPatch((8.6, 4.5), 2.5, 1.2, boxstyle="round,pad=0.1",
                                   edgecolor='#8D6E63', facecolor='#D7CCC8', linewidth=2)
    ax.add_patch(box5)
    ax.text(9.85, 5.2, 'Fezes (Estercobilina)', fontsize=9, fontweight='bold', ha='center')

    # Problemas (alinhados sob a etapa correspondente)
    problems = [
        ("Hemólise", "↑ Bili Indireta", 1.5, 3.2, '#E11D48'),
        ("Disfunção Hepática", "↑ Bili Indireta e Direta", 6.9, 3.2, '#E11D48'),
        ("Colestase / Obstrução Biliar", "↑ Bili Direta", 9.85, 3.2, '#E11D48')
    ]

    for titulo, tipo, x, y, cor in problems:
        ax.text(x, y, f'{titulo}\n{tipo}', fontsize=8, ha='center',
                bbox=dict(boxstyle='round', facecolor='#FECDD3', alpha=0.8),
                color=cor, fontweight='bold')

    # Icterícia
    icterica_box = patches.FancyBboxPatch((0.5, 0.5), 11, 1.5, boxstyle="round,pad=0.1",
                                          edgecolor='#7C3A92', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(icterica_box)
    ax.text(6, 1.7, 'ICTERÍCIA (Bili Total > 2.0 mg/dL)', fontsize=11, fontweight='bold', ha='center', color='#7C3A92')
    ax.text(6, 1.1, 'Pele e olhos ficam amarelados | Urina escura | Fezes claras',
            fontsize=9, ha='center', color='#7C3A92')

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'bilirrubina_metabolismo.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("bilirrubina_metabolismo.png")
    plt.close()

# ──────────────────────────────────────────
# 16. Bilirrubina - Icterícia
# ──────────────────────────────────────────
def criar_bilirrubina_ictericia():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    nivel = ['Normal', 'Leve', 'Moderada', 'Grave']
    bili_total = [0.8, 2.5, 5.0, 8.0]
    cores_amostra = ['#FFE082', '#F4A742', '#F77D2E', '#E74C3C']

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    # Gráfico de barras com cores
    bars = ax.barh(nivel, bili_total, color=cores_amostra, edgecolor='black', linewidth=2)

    # Valores nos bars
    for i, (bar, valor) in enumerate(zip(bars, bili_total)):
        ax.text(valor + 0.2, bar.get_y() + bar.get_height()/2,
                f'{valor} mg/dL', va='center', fontsize=11, fontweight='bold')

    # Linha de referência
    ax.axvline(x=1.2, color='#16A44A', linestyle='--', linewidth=2.5, label='Normal (< 1.2 mg/dL)')
    ax.axvline(x=2, color='#F69E3D', linestyle='--', linewidth=2.5, label='Icterícia visível (> 2.0 mg/dL)')

    ax.set_xlabel('Bilirrubina Total (mg/dL)', fontsize=12, fontweight='bold')
    ax.set_title('Escalas de Icterícia', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim(0, 9)

    # Anotações
    ax.text(4.5, 3.2, 'Bili Indireta elevada:\nHemólise ou disfunção hepática',
            fontsize=9, ha='center', bbox=dict(boxstyle='round', facecolor='#B3E5FC', alpha=0.8))

    ax.text(4.5, 0.2, 'Bili Direta elevada:\nColestase ou obstrução biliar',
            fontsize=9, ha='center', bbox=dict(boxstyle='round', facecolor='#FFE0B2', alpha=0.8))

    plt.tight_layout()
    plt.savefig(IMG_DIR / 'bilirrubina_ictericia.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("bilirrubina_ictericia.png")
    plt.close()

# ──────────────────────────────────────────
# EXECUTAR TUDO
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n📊 Gerando imagens educacionais...\n")

    criar_alt_localizacao()
    criar_alt_padrao()
    criar_ast_distribuicao()
    criar_ast_alt_ratio()
    criar_creatinina_metabolismo()
    criar_creatinina_funcao()
    criar_glicose_homeostase()
    criar_glicose_ttog()
    criar_colesterol_estrutura()
    criar_colesterol_lipoproteinas()
    criar_potassio_bomba()
    criar_potassio_ecg()
    criar_troponina_sarcomero()
    criar_troponina_cinetica()
    criar_bilirrubina_metabolismo()
    criar_bilirrubina_ictericia()

    print("\nTodas as imagens foram criadas em: data/images/")
    print(f"📁 Total de arquivos: {len(list(IMG_DIR.glob('*.png')))}")
