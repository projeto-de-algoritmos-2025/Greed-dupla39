"""Interface Streamlit para cadastrar e gerar uma agenda de tarefas.

Este módulo contém:
- formulário lateral para cadastrar tarefas (nome, duração em HH:MM, prazo, cliente, prioridade),
- editor inline para editar/remover tarefas existentes,
- geração de um cronograma otimizado (Earliest Deadline First) exibido como um gráfico Gantt.
"""

import streamlit as st
from datetime import datetime, time
import pandas as pd

from scheduler import Task, schedule_minimize_lateness


st.set_page_config(page_title='Planejador de Prazos', layout='wide')

st.title('Planejador de Prazos')

# Inicializar session_state com tarefas de exemplo
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = [
        {'id': 1, 'name': 'Petição Inicial', 'duration_hours': 4.0, 'deadline': datetime(2025,10,20,17,0), 'priority':'alta', 'client':'João'},
        {'id': 2, 'name': 'Audiência', 'duration_hours': 2.0, 'deadline': datetime(2025,10,19,10,0), 'priority':'alta', 'client':'Maria'},
        {'id': 3, 'name': 'Contestação', 'duration_hours': 3.0, 'deadline': datetime(2025,10,21,12,0), 'priority':'média', 'client':'José'},
    ]


def new_task_form():
    """Renderiza o formulário lateral para cadastrar uma nova tarefa.
    
    O campo de duração usa `time_input` no formato HH:MM e, ao submeter, converte
    para horas (float) para armazenamento em `st.session_state['tasks']`.
    """
    st.sidebar.header('Cadastrar nova tarefa')
    name = st.sidebar.text_input('Nome da tarefa')
    duration_time = st.sidebar.time_input('Duração (HH:MM)', value=time(2, 0))
    dl_date = st.sidebar.date_input('Prazo (data)', value=datetime.now().date())
    dl_time = st.sidebar.time_input('Prazo (hora)', value=datetime.now().time())
    deadline = datetime.combine(dl_date, dl_time)
    client = st.sidebar.text_input('Cliente (opcional)')
    priority = st.sidebar.selectbox('Prioridade', ['alta', 'média', 'baixa'])
    
    if st.sidebar.button('Adicionar tarefa'):
        tasks = st.session_state.get('tasks', [])
        next_id = max([t['id'] for t in tasks], default=0) + 1
        try:
            dt = duration_time
            duration = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        except Exception:
            duration = 0.0
        tasks.append({
            'id': next_id, 
            'name': name, 
            'duration_hours': duration, 
            'deadline': deadline, 
            'priority': priority, 
            'client': client
        })
        st.session_state['tasks'] = tasks
        st.sidebar.success('Tarefa adicionada!')


new_task_form()

st.sidebar.markdown('---')
if st.sidebar.button('Limpar tarefas'):
    st.session_state['tasks'] = []

st.header('Tarefas cadastradas')
tasks_df = pd.DataFrame(st.session_state['tasks'])
if not tasks_df.empty:
    display_df = tasks_df.copy()
    if 'client' not in display_df.columns:
        display_df['client'] = ''
    
    # Formatar duração (float horas) para HH:MM
    def fmt_duration(h):
        try:
            total_minutes = int(round(float(h) * 60))
            hh = total_minutes // 60
            mm = total_minutes % 60
            return f"{hh:02d}:{mm:02d}"
        except Exception:
            return str(h)
    
    # Formatar prazo final para dd/mm/YYYY HH:MM
    def fmt_deadline(d):
        try:
            return d.strftime('%d/%m/%Y %H:%M')
        except Exception:
            return str(d)
    
    # Aplicar formatações
    if 'duration_hours' in display_df.columns:
        display_df['duration_hours'] = display_df['duration_hours'].apply(fmt_duration)
    if 'deadline' in display_df.columns:
        display_df['deadline'] = display_df['deadline'].apply(fmt_deadline)
    
    # Selecionar e renomear colunas para exibição
    display_df = display_df[['id', 'name', 'duration_hours', 'deadline', 'priority', 'client']]
    display_df = display_df.rename(columns={
        'name': 'Tarefa',
        'duration_hours': 'Duração',
        'deadline': 'Prazo final',
        'priority': 'Prioridade',
        'client': 'Cliente',
    })
    st.table(display_df)
else:
    st.info('Nenhuma tarefa cadastrada. Use o formulário lateral para adicionar.')
