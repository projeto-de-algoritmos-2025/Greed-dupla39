"""Interface Streamlit para cadastrar e gerar uma agenda de tarefas.

Este módulo contém:
- formulário lateral para cadastrar tarefas (nome, duração em HH:MM, prazo, cliente, prioridade),
- editor inline para editar/remover tarefas existentes,
- geração de um cronograma otimizado (Earliest Deadline First) exibido como um gráfico Gantt.
"""

import streamlit as st
from datetime import datetime, time
import pandas as pd
import plotly.express as px

from scheduler import Task, schedule_minimize_lateness


def safe_rerun():
    """Função auxiliar para reexecutar o Streamlit de forma segura."""
    try:
        if hasattr(st, 'rerun'):
            st.rerun()
    except Exception:
        return


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
    
    # Editor inline de tarefas
    with st.expander('Editar / Remover tarefas'):
        for idx, row in tasks_df.iterrows():
            cols = st.columns([2, 1, 1, 1, 1])
            name = cols[0].text_input(label=f"Tarefa {row['id']}", value=row['name'], key=f"nome_{row['id']}")
            
            # Converter duração de float para time para o time_input
            try:
                dh = float(row.get('duration_hours', 0.0))
                dh_hours = int(dh)
                dh_minutes = int(round((dh - dh_hours) * 60))
                default_dur_time = time(dh_hours % 24, dh_minutes)
            except Exception:
                default_dur_time = time(2, 0)
            
            dur_time = cols[1].time_input(label=f"Duração {row['id']}", value=default_dur_time, key=f"dur_{row['id']}")
            
            # Converter deadline para date e time separados
            try:
                existing_deadline = row['deadline']
                dl_date_val = existing_deadline.date()
                dl_time_val = existing_deadline.time()
            except Exception:
                dl_date_val = datetime.now().date()
                dl_time_val = datetime.now().time()
            
            dl_date = cols[2].date_input(label=f"Prazo (Data) {row['id']}", value=dl_date_val, key=f"dl_date_{row['id']}")
            dl_time = cols[2].time_input(label=f"Prazo (Hora) {row['id']}", value=dl_time_val, key=f"dl_time_{row['id']}")
            dl = datetime.combine(dl_date, dl_time)
            
            pr = cols[3].selectbox(label=f"Prioridade {row['id']}", options=['alta','média','baixa'], 
                                 index=['alta','média','baixa'].index(row['priority']), key=f"pr_{row['id']}")
            client_val = cols[0].text_input(label=f"Cliente {row['id']}", value=row.get('client',''), key=f"client_{row['id']}")
            
            # Botões de ação
            if cols[4].button('Salvar', key=f'save_{row["id"]}'):
                tasks = st.session_state['tasks']
                for t in tasks:
                    if t['id'] == row['id']:
                        t['name'] = name
                        try:
                            dt = dur_time
                            dur_hours = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
                        except Exception:
                            dur_hours = float(row.get('duration_hours', 0.0))
                        t['duration_hours'] = dur_hours
                        t['deadline'] = dl
                        t['priority'] = pr
                        t['client'] = client_val
                st.session_state['tasks'] = tasks
                st.success(f'Tarefa "{name}" salva!')
                safe_rerun()
            
            if cols[4].button('Remover', key=f'del_{row["id"]}'):
                st.session_state['tasks'] = [t for t in st.session_state['tasks'] if t['id'] != row['id']]
                st.success(f'Tarefa "{row["name"]}" removida!')
                safe_rerun()
else:
    st.info('Nenhuma tarefa cadastrada. Use o formulário lateral para adicionar.')

# Seção de cronograma EDF
st.header('Agenda otimizada (Earliest Deadline First)')

# Configuração de horário de início
col1, col2 = st.columns(2)
with col1:
    st_date = st.date_input('Início (data)', value=datetime.now().date())
with col2:
    st_time = st.time_input('Início (hora)', value=datetime.now().time())

start_time = datetime.combine(st_date, st_time)

# Construir objetos Task e gerar cronograma
if st.session_state['tasks']:
    tasks = []
    for t in st.session_state['tasks']:
        task = Task(
            id=t['id'], 
            name=t['name'], 
            duration_hours=float(t['duration_hours']), 
            deadline=t['deadline'], 
            priority=t.get('priority','média'), 
            client=t.get('client','')
        )
        tasks.append(task)
    
    # Gerar cronograma usando EDF
    schedule_result = schedule_minimize_lateness(tasks, start_time)
    
    # Exibir métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Atraso total (h)', f"{schedule_result['total_lateness_hours']:.2f}")
    with col2:
        st.metric('Atraso máximo (h)', f"{schedule_result['max_lateness_hours']:.2f}")
    
    # Exibir cronograma em tabela
    st.subheader('Cronograma de execução')
    schedule_rows = []
    for r in schedule_result['ordered']:
        t = r['task']
        schedule_rows.append({
            'Tarefa': t.name,
            'Cliente': t.client,
            'Início': r['start'].strftime('%d/%m/%Y %H:%M'),
            'Fim': r['finish'].strftime('%d/%m/%Y %H:%M'),
            'Duração': f"{t.duration_hours:.2f}h",
            'Prazo': t.deadline.strftime('%d/%m/%Y %H:%M'),
            'Atraso (h)': f"{r['lateness_hours']:.2f}",
            'Prioridade': t.priority
        })
    
    schedule_df = pd.DataFrame(schedule_rows)
    st.table(schedule_df)
    
    # Gráfico Gantt
    st.subheader('Gráfico Gantt')
    
    # Preparar dados para o gráfico Gantt
    gantt_rows = []
    for r in schedule_result['ordered']:
        t = r['task']
        gantt_rows.append({
            'Task': t.name,
            'Start': r['start'],
            'Finish': r['finish'],
            'Lateness (h)': round(r['lateness_hours'], 2),
            'Priority': t.priority,
            'Client': t.client,
            'Deadline': t.deadline,
        })
    
    gantt_df = pd.DataFrame(gantt_rows)
    
    # Definir cores baseadas no atraso (verde = no prazo, vermelho = atrasado)
    gantt_df['Color'] = gantt_df['Lateness (h)'].apply(lambda x: 'red' if x > 0 else 'green')
    
    # Função para formatar prazo no hover
    def format_deadline(val):
        try:
            return val.strftime('%d/%m/%Y %H:%M')
        except Exception:
            return str(val)
    
    # Criar labels customizados para hover
    def make_label(r):
        task = r.get('Task', '')
        client = r.get('Client', '')
        client_part = f" - {client}" if client else ""
        deadline_str = format_deadline(r.get('Deadline'))
        priority = r.get('Priority', '')
        lateness = r.get('Lateness (h)', 0)
        status = "ATRASADA" if lateness > 0 else "NO PRAZO"
        return f"{task}{client_part}<br>Prazo: {deadline_str}<br>Prioridade: {priority}<br>Status: {status}"
    
    gantt_df['Label'] = gantt_df.apply(make_label, axis=1)
    
    # Criar gráfico Gantt com Plotly
    fig = px.timeline(
        gantt_df, 
        x_start='Start', 
        x_end='Finish', 
        y='Task', 
        color='Color',
        color_discrete_map={'green': '#28a745', 'red': '#dc3545'},
        title='Cronograma de Execução das Tarefas'
    )
    
    # Customizar hover
    fig.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>',
        customdata=gantt_df[['Label']].values
    )
    
    # Ajustar layout
    fig.update_yaxes(autorange='reversed')  # Primeira tarefa no topo
    fig.update_layout(
        height=max(400, len(gantt_df) * 50),  # Altura dinâmica baseada no número de tarefas
        showlegend=False,
        xaxis_title="Tempo",
        yaxis_title="Tarefas"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info('Adicione tarefas para gerar um cronograma otimizado.')

