# Estudo de Qualidade de Dados com Arquitetura Medallion em Python

Este repositório contém uma implementação prática, modular e profissional da **Arquitetura Medallion** (Bronze, Silver e Gold) em Python, com foco central em **Qualidade de Dados (Data Quality)**, **Padrão de Quarentena (Dead-Letter Queue / Observability)** e **Testes Automatizados**.

---

## ⚡ Resumo Rápido: Como Usar (Quick Start)

Se você quer apenas rodar o projeto e ver a mágica acontecer:

```bash
# 1. Clone o repositório
git clone https://github.com/lvcasTW/data-qa.git
cd data-qa

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # No Windows: .venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a pipeline completa
python main.py

# 5. Rode a suíte de testes automatizados
pytest -v
```

### 🎯 O que esperar da execução:
1. **Geração Sintética Automática**: Se a pasta de entrada (`data/raw`) estiver vazia, 25 transações fictícias com anomalias propositais (e-mail incorreto, preço negativo, data no futuro, erro de cálculo) são geradas automaticamente.
2. **Ingestão Bronze**: Os dados brutos são persistidos com metadados de linhagem (`_bronze_source_file`, `_bronze_ingested_at`).
3. **Validação Silver & Quarentena**: Cada registro é validado via **Pydantic v2**. Registros aprovados vão para `data/silver/orders_silver.csv`; registros com qualquer anomalia são roteados para `data/quarantine/orders_quarantine.csv` acompanhados do motivo exato do erro e timestamp.
4. **Agregação Gold**: Três tabelas analíticas prontas para BI/Data Science são criadas em `data/gold/`:
   - `daily_sales.csv`: Vendas diárias agregadas.
   - `customer_metrics.csv`: LTV e total gasto por cliente.
   - `category_metrics.csv`: Volume e faturamento por categoria de produto.
5. **Relatório no Console**: A execução exibe no terminal um resumo estatístico e a lista detalhada de cada registro enviado para quarentena.

---

## 🔄 Fluxo de Dados e Arquitetura

```text
               ┌──────────────────────────────┐
               │    data/raw/ (Landing Zone)  │
               └──────────────┬───────────────┘
                              │ Ingestão & Linhagem
                              ▼
               ┌──────────────────────────────┐
               │    data/bronze/ (Bruto)      │
               └──────────────┬───────────────┘
                              │
               Validação Pydantic (Data Quality)
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
   ┌───────────────────────┐     ┌───────────────────────┐
   │ data/silver/ (Limpo)  │     │ data/quarantine/      │
   │ Registros 100% válidos│     │ Erros, logs e motivos │
   └───────────┬───────────┘     └───────────────────────┘
               │ Agregações de Negócio
               ▼
   ┌─────────────────────────────────────────────────────┐
   │ data/gold/ (Analítico / BI)                         │
   │ - daily_sales.csv                                   │
   │ - customer_metrics.csv                              │
   │ - category_metrics.csv                              │
   └─────────────────────────────────────────────────────┘
```

---

## 🏗️ As Camadas Medallion em Detalhes

1. **Bronze (Raw / Dados Brutos):** 
   - Armazena os dados exatamente como foram extraídos do sistema de origem. Não há limpeza de esquema ou transformações.
   - **Boa Prática:** Preserva a integridade do histórico absoluto das origens (incluindo erros) para fins de auditoria, governança e reprocessamento completo.

2. **Silver (Cleaned / Dados Limpos e Validados):**
   - Os dados são limpos, tipados, padronizados e validados rigorosamente em relação a um esquema definido.
   - **Boa Prática (Quarentena):** Em vez de quebrar a pipeline inteira ou descartar silenciosamente registros incorretos, o pipeline utiliza uma **Quarentena**. Registros reprovados são salvos em `data/quarantine` com o erro catalogado. Dados limpos vão para `data/silver`.

3. **Gold (Curated / Dados Analíticos e Agregados):**
   - Dados refinados que passaram pela camada Silver são agregados e formatados para atender a necessidades específicas de inteligência de negócios (BI), dashboards e modelos estatísticos.

---

## 🛒 Regras de Qualidade de Dados (Data Quality)

O pipeline valida as transações de e-commerce contra as seguintes regras declarativas:

| Campo | Regra / Validação | Comportamento se Inválido |
| :--- | :--- | :--- |
| `order_id` | String obrigatória, não vazia | Enviado para Quarentena |
| `customer_id` | String obrigatória, não vazia | Enviado para Quarentena |
| `customer_email` | Formato padrão de e-mail (RFC 5322 via `EmailStr`) | Enviado para Quarentena |
| `product_category` | Permitidos: `Electronics`, `Home`, `Clothing`, `Books`, `Sports` | Normaliza capitalização ou quarentena se desconhecida |
| `order_date` | Formato `YYYY-MM-DD`, não permite datas no futuro | Enviado para Quarentena |
| `quantity` | Inteiro estritamente positivo (`gt=0`) | Enviado para Quarentena |
| `unit_price` | Decimal estritamente positivo (`gt=0`) | Enviado para Quarentena |
| `total_amount` | Consistência matemática: `quantity * unit_price == total_amount` | Enviado para Quarentena se divergir além da tolerância float |

---

## 📂 Estrutura de Diretórios

```text
data-qa/
├── README.md               # Documentação e guia de uso
├── requirements.txt         # Dependências do projeto (pandas, pydantic, pytest)
├── main.py                  # Orquestrador central e executor do pipeline
├── data/                    # Lakehouse local simulado
│   ├── raw/                 # Landing zone para arquivos CSV de entrada
│   ├── bronze/              # Tabela Bronze com metadados de ingestão
│   ├── silver/              # Tabela Silver purificada com dados 100% corretos
│   ├── quarantine/          # Registros rejeitados com as razões de erro mapeadas
│   └── gold/                # Visões agregadas de negócio prontas para BI
├── src/
│   ├── __init__.py
│   ├── config.py            # Definição centralizada dos caminhos do lakehouse
│   ├── utils.py             # Helpers de logging e leitura/escrita de CSV
│   ├── validation/
│   │   ├── __init__.py
│   │   └── schemas.py       # Validação de regras e esquemas com Pydantic v2
│   └── pipelines/
│       ├── __init__.py
│       ├── data_generator.py # Gerador sintético com falhas planejadas de qualidade
│       ├── bronze_pipeline.py# Ingestão de dados brutos para Bronze
│       ├── silver_pipeline.py# Validação e separação em Silver vs Quarentena
│       └── gold_pipeline.py  # Agregações e KPIs analíticos na camada Gold
└── tests/
    ├── __init__.py
    ├── conftest.py          # Fixtures e isolamento do ambiente de testes
    ├── test_validation.py   # Testes unitários das regras de qualidade do Pydantic
    └── test_pipelines.py    # Testes de integração end-to-end do fluxo Medallion
```

---

## 🧪 Automação de Testes

Os testes automatizados utilizam `pytest` para garantir prevenção de regressões:

```bash
# Execução padrão dos testes
pytest -v

# Execução com cobertura de código (coverage)
pytest --cov=src -v
```

### O que está coberto pela suíte:
* **Unitários (`tests/test_validation.py`)**: 
  - Testes individuais para cada regra de negócio (preço negativo, quantidade inválida, e-mail malformado, inconsistência matemática, data futura).
  - Teste de padronização automática de maiúsculas/minúsculas de categorias.
  - Teste de divisão em lote (`validate_records`) entre válidos e quarentena.
* **Integração (`tests/test_pipelines.py`)**: 
  - Execução ponta a ponta: Raw -> Bronze -> Silver -> Gold.
  - Isolamento de disco via fixture `tmp_path` do pytest (não afeta a pasta `data/` real).
  - Verificação quantitativa de registros gerados e cálculos de KPIs.

---

## 👤 Autor

Desenvolvido por **Lucas Morais** ([@lvcasTW](https://github.com/lvcasTW)).
