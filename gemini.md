  Estruturação do Projeto Medallion e Qualidade de Dados: 
  Finalização e entrega do exemplo de estudo de arquitetura Medallion e Data
  Quality em Python.


✦ Com certeza! Criei no seu repositório uma implementação completa, profissional
  e extremamente educativa de um pipeline de dados utilizando a Arquitetura
  Medallion em Python, com foco total em Qualidade de Dados (Data Quality), Boas
  Práticas de Engenharia (Quarentena de dados) e Automação de Testes (unitários
  e de integração).

  Abaixo estão os detalhes do que foi estruturado e as boas práticas aplicadas:

  ---

  1. 🏗️ Estrutura do Projeto Gerada

    1 data-qa/
    2 ├── README.md               # Guia descritivo completo em português
    3 ├── requirements.txt         # Definições de dependências (pandas,
      pydantic, pytest)
    4 ├── main.py                  # Orquestrador central e executor do pipeline
    5 ├── data/                    # Banco de dados / "Data Lake" simulado
    6 │   ├── raw/                 # Landing Zone de arquivos CSV crus de
      entrada
    7 │   ├── bronze/              # Dados crus ingeridos com adição de
      metadados
    8 │   ├── silver/              # Dados 100% validados, limpos e tipados
    9 │   ├── quarantine/          # Registros rejeitados com logs detalhados do
      erro
   10 │   └── gold/                # Visões agregadas e prontas para BI /
      Analytics
   11 ├── src/
   12 │   ├── __init__.py
   13 │   ├── config.py            # Definição e gerenciamento de caminhos do
      Lakehouse
   14 │   ├── utils.py             # Helpers de I/O de arquivos e logging
      estruturado
   15 │   ├── validation/
   16 │   │   ├── __init__.py
   17 │   │   └── schemas.py       # Definição das regras de Data Quality com
      Pydantic
   18 │   └── pipelines/
   19 │       ├── __init__.py
   20 │       ├── data_generator.py # Gerador de dados com falhas planejadas de
      qualidade
   21 │       ├── bronze_pipeline.py# Ingestão de dados originais para a camada
      Bronze
   22 │       ├── silver_pipeline.py# Higienização de dados e roteamento para
      Quarentena
   23 │       └── gold_pipeline.py  # Agregador analítico de KPIs de Negócio
   24 └── tests/
   25     ├── __init__.py
   26     ├── conftest.py          # Fixtures e isolamento do ambiente de testes
   27     ├── test_validation.py   # Testes unitários das regras de qualidade
      (Pydantic)
   28     └── test_pipelines.py    # Testes de integração end-to-end (Bronze ->
      Silver -> Gold)

  ---

  2. 🌟 Principais Boas Práticas de Qualidade Aplicadas

   * Validação Declarativa Rigorosa: Usamos a biblioteca Pydantic (v2) no módulo
     schemas.py para criar regras detalhadas que validam campos (formatos de
     e-mail com EmailStr, valores estritamente positivos com Field(..., gt=0),
     categorias permitidas com padronização automática de letras
     maiúsculas/minúsculas).
   * Validação de Negócio (Consistência Matemática): Criamos um validador no
     modelo que calcula se quantidade * preço_unitário == total_amount de forma
     automática, identificando inconsistências comuns em sistemas transacionais.
   * Padrão de Quarentena (Observabilidade): Ao processar os dados da Bronze
     para a Silver, nenhum registro incorreto é apagado ou faz a pipeline
     falhar. Os registros corrompidos são automaticamente roteados para a pasta
     data/quarantine junto com metadados adicionais, incluindo o motivo exato da
     falha estrutural e o timestamp da rejeição, permitindo rápida análise e
     depuração por analistas de dados.
   * Metadados de Ingestão e Linhagem (Data Lineage): Em cada camada adicionamos
     colunas técnicas com prefixos especiais (como _bronze_source_file,
     _bronze_ingested_at, _silver_processed_at e _gold_updated_at) para fins de
     auditoria histórica e governança de dados.
   * Isolamento de Testes: As suites de testes no pytest utilizam fixtures com
     diretórios temporários gerados na hora da execução (tmp_path). Isso garante
     que os testes nunca interfiram no seu diretório data/ principal de
     desenvolvimento.

  Siga os passos abaixo em seu terminal para ver a pipeline e os testes rodando
  em sua máquina:

  A. Configurar o ambiente

   1 # 1. Criar ambiente virtual Python
   2 python3 -m venv .venv
   3
   4 # 2. Ativar o ambiente virtual
   5 source .venv/bin/activate  # (No Windows use: .venv\Scripts\Activate.ps1)
   6
   7 # 3. Instalar as dependências necessárias
   8 pip install -r requirements.txt

  B. Executar a Pipeline de dados completa
   1 python main.py
   * O que acontece ao rodar: O script detecta que a pasta de entrada está
     vazia, gera dados transacionais fictícios (com alguns erros propositais,
     como e-mail inválido, preço negativo, data no futuro, erro matemático e ID
     vazio), roda as etapas Bronze, Silver e Gold em sequência e imprime na tela
     um Relatório Detalhado de Qualidade de Dados (Quarentena) listando cada
     erro detectado detalhadamente.

  C. Executar os Testes Automatizados
   1 pytest -v
   * O que acontece ao rodar: Executa 9 testes unitários e de integração de
     forma isolada e em milissegundos, garantindo que todas as regras de
     qualidade estão totalmente blindadas contra alterações acidentais.
