# Documentação — Monitor de Formação · Bootcamp DIOxAfyaxPdA

**Projeto:** Programadores do Amanhã (PdA)
**Responsável:** Leticia Santana — leticia@programadoresdoamanha.org.br
**Última atualização:** 16/05/2026

---

## 1. O que é este projeto

Dashboard de monitoramento do Bootcamp Automação de Dados com IA, uma parceria entre DIOxAfyaxPdA. O objetivo é acompanhar semana a semana o progresso dos alunos do grupo de diversidade e identificar quem tem maior probabilidade de se formar, concentrando os esforços de engajamento nas pessoas certas.

**Meta institucional:** formar 10% do grupo de diversidade (Preto/Pardo ou Indígena) até **12 de julho de 2026**.

---

## 2. Como usar no dia a dia

1. Toda segunda-feira, baixe o relatório CSV ou XLSX da plataforma DIO
2. Acesse a URL do dashboard no navegador
3. Clique no painel **"📂 Carregar relatório semanal da DIO"**
4. Selecione o novo arquivo (ou múltiplos arquivos de uma vez)
5. O dashboard atualiza automaticamente para toda a equipe

---

## 3. Estrutura de arquivos

```
monitor-bootcamp-afya/
├── app.py                  # Aplicação principal (Streamlit)
├── requirements.txt        # Dependências Python
├── DOCUMENTACAO.md         # Este arquivo
├── README.md               # Guia de publicação na nuvem
├── .streamlit/
│   └── config.toml         # Tema dark com cores PdA
└── data/
    ├── .gitkeep
    └── history.json        # Criado automaticamente — histórico acumulado
```

---

## 4. Formato dos dados de entrada

O app aceita os relatórios exportados diretamente da DIO nos formatos **CSV** e **XLSX**.

### Colunas reconhecidas

| Coluna | Descrição | Obrigatória |
|--------|-----------|-------------|
| `Nome` | Nome completo do aluno | Sim |
| `Email` | Usado como identificador único da pessoa | Sim |
| `Whatsapp` | Número de telefone | Não |
| `Progresso no bootcamp` | Float de 0 a 1 (ex: `0,25` = 25%) | Sim |
| `Diversidade - Preto ou Pardo` | Sim/Não | Não (tratado como Não se ausente) |
| `Diversidade - Indígenas` | Sim/Não | Não (tratado como Não se ausente) |
| `Graduado(a)` | Sim/Não | Não (tratado como Não se ausente) |

### Detecção automática de data

A data da semana é extraída do nome do arquivo automaticamente.
Exemplo: `relatorio_2026-05-16T14_30.csv` → detecta `2026-05-16`

Se o arquivo não tiver data no nome, o app solicita que você informe manualmente.

---

## 5. Os 6 blocos do dashboard

### Bloco 1 — Situação da meta
Responde de imediato: **"Estou no caminho de bater a meta?"**

- **Semanas restantes** até 12/07/2026
- **Formados vs meta** com barra de progresso visual
- **Projeção no ritmo atual** — alerta vermelho se abaixo da meta, verde se no caminho

### Bloco 2 — Distribuição e Momentum do Grupo
Visão panorâmica de onde o grupo de diversidade está.

- **Gráfico de rosca** com a distribuição por tier. Clique em "Ver critérios de classificação" para ver o que define cada grupo.
- **Subtítulo** mostra quantas pessoas representam o grupo de diversidade e qual % do total de inscritos
- **4 cards de momentum:** velocidade média semanal, progresso médio, quem acelerou e quem desacelerou esta semana
- **Comparativo com grupo não-diversidade** ao expandir "Comparar com grupo geral": velocidade, progresso médio, % que acelerou e % que desacelerou dentro de cada grupo (comparação proporcional, não absoluta)
- **Mini gráfico de tendência** mostrando a evolução das últimas semanas

### Funil de Progressão — Diversidade
Mostra quantas pessoas atingiram cada marco de progresso, com comparativo semana a semana.

- **Gráfico de barras horizontais:** cinza = semana anterior, amarelo = esta semana. Permite ver visualmente o avanço em direção à conclusão.
- **Tabela de variação:** Etapa | Semana Ant. | Esta Semana | Δ Abs. | Δ % — deltas em verde (positivo) ou vermelho (negativo)
- Marcos monitorados: 25% · Início, 50% · Meio, 75% · Avançado, 100% · Concluído

### Bloco 3 — Contatos desta semana
Lista focada em **Alta Prioridade** — as pessoas com maior potencial de conversão.

- Ordenada por score de conversão (quem mais vale o contato aparece primeiro)
- Cada pessoa tem uma **mensagem já escrita** personalizada com seu nome, pronta para envio
- Botão **"Exportar contatos (n8n)"** baixa o JSON com todas as mensagens para o n8n disparar via WhatsApp

### Bloco 4 — Evolução Semanal
Gráfico de linha mostrando o progresso médio semana a semana.

- **Linha amarela:** grupo de diversidade
- **Linha cinza pontilhada:** total geral do bootcamp
- **Linha verde pontilhada:** meta de conclusão (70%)
- **Leitura automática:** o dashboard interpreta se a diversidade está acelerando ou desacelerando em relação ao geral

### Bloco 5 — Lista Completa por Grupo
Tabela com todas as pessoas do grupo de diversidade, separadas por abas por tier.

- Colunas: Nome, Contato (email + WhatsApp formatado), Progresso, Δ semana, Projeção 12/07, Tier, Mensagem sugerida
- Cada aba tem seu próprio botão **"Exportar para n8n"** — exporta só aquele grupo

---

## 6. Tiers de prioridade

| Tier | Critério | Ação recomendada |
|------|----------|-----------------|
| 🎯 **Alta Prioridade** | Progredindo + projeção 40–69% | Contato focado via WhatsApp — pode converter |
| 🟡 **Atenção** | Progredindo, mas lento ou projeção < 40% | Check-in amigável — identificar barreiras |
| 🟢 **No Caminho** | Projeção ≥ 70% | Mensagem de celebração |
| 🔴 **Estagnado** | Sem progresso há 2+ semanas | Máximo 1 contato |
| ✅ **Formado** | Graduado(a) = Sim | Convidar para depoimento |
| ⚫ **Abandono** | Nunca progrediu | Não contatar |

### Fórmulas de cálculo

```
velocidade_media     = média dos últimos 3 deltas semanais de progresso
semanas_restantes    = (2026-07-12 − data_último_snapshot) / 7
progresso_projetado  = min(1.0, progresso_atual + velocidade_media × semanas_restantes)
score_conversao      = velocidade_media × (1 − gap_para_70%)
  onde gap_para_70%  = max(0, 0.70 − progresso_projetado)
```

A tabela é ordenada pelo `score_conversao` — maior score = mais vale o contato.

---

## 7. Mensagens geradas automaticamente

As mensagens são criadas pelo dashboard com base no tier de cada pessoa. O tom é sempre caloroso, encorajador e nunca cobrante.

**O que as mensagens NÃO fazem:**
- Não citam percentuais exatos de evolução semanal
- Não usam linguagem de cobrança ou pressão
- Não usam travessões (apenas vírgulas e pontos)

**O que as mensagens sempre incluem:**
- Nome da pessoa (primeiro nome)
- Nome completo do bootcamp: "Bootcamp Automação de Dados com IA, uma parceria entre DIOxAfyaxPdA"
- Contexto do prazo (12 de julho)
- Menção às monitorias síncronas gratuitas da PdA
- Link da comunidade no WhatsApp da PdA
- Missão da PdA de qualificar e empoderar pessoas negras e indígenas no mercado tech

**Para editar as mensagens:** abra o `app.py` e localize a função `generate_message` (linha ~261). Cada tier tem seu próprio bloco de texto para editar livremente.

### Tom por tier

| Tier | Tom da mensagem |
|------|----------------|
| 🎯 Alta Prioridade | Incentivo — "você está na reta final, não para agora!" |
| 🟡 Atenção | Encorajamento — "ainda tem tempo, cada semana conta" |
| 🟢 No Caminho | Celebração — "você está indo muito bem, parabéns!" |
| 🔴 Estagnado | Acolhimento — "a porta ainda está aberta, a gente apoia" |
| ✅ Formado | Gratidão — "você é prova de que é possível" |
| ⚫ Abandono | Convite gentil — "nunca é tarde para começar" |

---

## 8. Exportação para n8n (WhatsApp)

O JSON exportado tem este formato:

```json
[
  {
    "nome": "Maria Silva",
    "email": "maria@email.com",
    "whatsapp": "5511999990000",
    "tier": "Alta Prioridade",
    "progresso_atual_pct": 62.0,
    "projecao_pct": 71.0,
    "score_conversao": 18.4,
    "avancou_semana": true,
    "mensagem": "Oi, Maria! 👋\n\nVocê está na reta final...",
    "semana_referencia": "2026-05-16"
  }
]
```

- O campo `whatsapp` já vem formatado com DDI 55 (padrão Evolution API / Z-API)
- O campo `mensagem` contém o texto completo pronto para envio
- O n8n lê o JSON, percorre cada item e envia a mensagem via WhatsApp — sem precisar montar nada

---

## 9. Persistência dos dados

Os dados ficam em `data/history.json` no servidor do Streamlit Cloud.

| Situação | Dados mantidos? |
|----------|----------------|
| Carregar novo CSV no dashboard | ✅ Sim |
| Equipe acessar a mesma URL | ✅ Sim — dados são compartilhados |
| Subir novo arquivo no GitHub | ⚠️ Servidor pode reiniciar e perder os dados |

**O que fazer quando os dados sumirem:** use o painel de upload para recarregar os arquivos históricos. Selecione todos de uma vez para restaurar o histórico completo.

> **Dica:** na prática, o Streamlit Cloud às vezes preserva o `history.json` mesmo após um redeploy. Se ao abrir o dashboard os dados ainda estiverem lá, não precisa recarregar nada.

---

## 10. Como atualizar o app

Qualquer alteração no `app.py` dispara um redeploy automático no Streamlit Cloud em ~2 minutos.

Para atualizar um arquivo no GitHub sem terminal:
1. Acesse **github.com/leticiassantana/monitor-bootcamp-afya**
2. Clique em **"Add file"** → **"Upload files"**
3. Arraste o arquivo do seu computador
4. Clique em **"Commit changes"**

> Prefira sempre o "Upload files" ao invés do editor online (lápis ✏️) para evitar que arquivos grandes sejam cortados no meio.

---

## 11. Identidade visual

| Elemento | Valor |
|----------|-------|
| Cor de fundo | `#270028` (roxo escuro PdA) |
| Cor dos cards | `#3a003d` |
| Amarelo destaque | `#eddc11` |
| Fonte títulos | Dela Gothic One |
| Fonte corpo | IBM Plex Sans |
| Link WhatsApp PdA | https://chat.whatsapp.com/Cf2CicuO1Al1jVoYFe5i0l |

---

## 12. Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3.11+ | Linguagem principal |
| Streamlit ≥ 1.35 | Framework do dashboard |
| Pandas ≥ 2.0 | Leitura e processamento de CSV/XLSX |
| Plotly ≥ 5.18 | Gráficos interativos |
| openpyxl ≥ 3.1 | Leitura de XLSX |
| Streamlit Community Cloud | Hospedagem gratuita |
| GitHub | Controle de versão e deploy automático |

---

## 13. Problemas conhecidos e soluções

| Problema | Causa | Solução |
|----------|-------|---------|
| Dados sumiram após atualização de código | Servidor reiniciou com novo deploy | Recarregar os arquivos históricos pelo painel de upload |
| Arquivo CSV sem coluna `Graduado(a)` | Relatório antigo (ex: 29/04/2026) | Tratado automaticamente como Não |
| Data não detectada no nome do arquivo | Nome renomeado manualmente | App solicita a data via campo de texto |
| Arquivo cortado ao usar editor do GitHub | Limitação do copy-paste em arquivos grandes | Usar "Upload files" em vez do editor online |
