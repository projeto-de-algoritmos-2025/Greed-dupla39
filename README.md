# Planejador de Prazos - Earliest Deadline First (EDF)

**Conteúdo da Disciplina**: Grafos 1<br>
**Dupla**: 39

## Alunos

| Matrícula    | Aluno |
| -- | -- |
| 19/0083590    | Amanda Alves Campos |
| 21/1062900    | Caio Lucas Lelis Borges |

## Sobre 

Este projeto implementa um **Planejador de Prazos** utilizando o algoritmo **Earliest Deadline First (EDF)** para otimizar o agendamento de tarefas e minimizar atrasos. A aplicação foi desenvolvida com interface web interativa usando Streamlit.

### Características principais:
- **Cadastro de tarefas**: Nome, duração (HH:MM), prazo, cliente e prioridade
- **Edição de tarefas**: Modificação e remoção de tarefas existentes
- **Algoritmo EDF**: Ordenação por prazo mais próximo para minimizar lateness
- **Visualização Gantt**: Cronograma visual das tarefas agendadas
- **Análise comparativa**: Comparação de desempenho com ordenação aleatória
- **Métricas detalhadas**: Atraso total, atraso máximo e número de tarefas atrasadas

## Screenshots

<p align="center"><b>Imagem 1: Visão inicial da Agenda de planejamento de prazos</b></p>

![pagina inicial](../assets/pagina-inicial.png)

<p align="center"><b>Imagem 2: Execução do algoritmo de agendamento com tarefas destacadas.</b></p>

![agenda](../assets/agenda.png)

<p align="center"><b>Imagem 3: Análise da eficiência do algoritmo.</b></p>

![analise](../assets/analise.png)

## Instalação 
**Linguagem**: Python<br>
**Framework**: Streamlit<br>

### Pré-requisitos:
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos para rodar:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/projeto-de-algoritmos-2025/Greed-dupla39.git
   cd Greed-dupla39
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   streamlit run app.py
   ```

5. **Acesse no navegador:**
   - Abra o link exibido no terminal (geralmente `http://localhost:8501`)


## Uso 

### Como usar a aplicação:

1. **Cadastrar tarefas:**
   - Use o formulário lateral para adicionar novas tarefas
   - Preencha nome, duração (formato HH:MM), prazo, cliente e prioridade
   - Clique em "Adicionar tarefa"

2. **Gerenciar tarefas:**
   - Visualize todas as tarefas na tabela principal
   - Use os botões "Editar" para modificar tarefas existentes
   - Use "Remover" para excluir tarefas
   - Use "Limpar tarefas" na barra lateral para remover todas

3. **Gerar cronograma:**
   - O algoritmo EDF ordena automaticamente as tarefas por prazo
   - Visualize o resultado no gráfico de Gantt interativo
   - Observe as métricas de atraso calculadas

4. **Analisar eficiência:**
   - Expanda a seção "Análise Comparativa"
   - Compare o desempenho do EDF com ordenação aleatória
   - Visualize as métricas de melhoria obtidas

### Funcionalidades técnicas:

- **Algoritmo EDF**: Implementação gulosa que ordena por deadline crescente
- **Cálculo de lateness**: Medida do atraso de cada tarefa (tempo de conclusão - deadline)
- **Otimização**: Minimiza o atraso total e máximo do conjunto de tarefas
- **Interface reativa**: Atualização automática do cronograma conforme mudanças

## Outros 

### Estrutura do projeto:
- **`app.py`**: Interface principal Streamlit com formulários e visualizações
- **`scheduler.py`**: Implementação do algoritmo EDF e classe Task

### Apresentação:
[Link para o vídeo de apresentação]()

