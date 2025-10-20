

from datetime import datetime, timedelta
from dataclasses import asdict, dataclass
from typing import List

import streamlit as st
import pandas as pd

from scheduler import Task, schedule_minimize_lateness


def init_state() -> None:
    """Inicializa variáveis em st.session_state usadas pelo app."""
    if 'tasks' not in st.session_state:
        st.session_state['tasks'] = []  # lista de dicionários


def fmt_tasks_df(tasks: List[dict]) -> pd.DataFrame:
    """Converte lista de tasks (dict) em DataFrame para exibição simples."""
    if not tasks:
        return pd.DataFrame(columns=['Tarefa', 'Duração (h)', 'Prazo', 'Prioridade', 'Cliente'])

    df = pd.DataFrame(tasks)
    # formata colunas esperadas
    if 'duration_hours' in df.columns:
        df['Duração (h)'] = df['duration_hours'].map(lambda v: f"{v:.2f}" if pd.notna(v) else '')
    if 'deadline' in df.columns:
        df['Prazo'] = pd.to_datetime(df['deadline']).dt.strftime('%d/%m/%Y %H:%M')
    df['Tarefa'] = df.get('name', '')
    df['Prioridade'] = df.get('priority', '')
    df['Cliente'] = df.get('client', '')
    return df[['Tarefa', 'Duração (h)', 'Prazo', 'Prioridade', 'Cliente']]


def main() -> None:
    """Ponto de entrada do app Streamlit"""
    st.title('Agenda de prazos')
    init_state()

    st.header('Tarefas atuais')
    df = fmt_tasks_df(st.session_state['tasks'])
    st.table(df)

    if st.button('Gerar agenda (EDF)'):
        tasks = []
        for t in st.session_state['tasks']:
            task = Task(
                id=int(t.get('id')),
                name=str(t.get('name')),
                duration_hours=float(t.get('duration_hours')),
                deadline=t.get('deadline') if isinstance(t.get('deadline'), datetime) else datetime.fromisoformat(t.get('deadline')),
                priority=t.get('priority', 'Média'),
                client=t.get('client', ''),
            )
            tasks.append(task)

        schedule = schedule_minimize_lateness(tasks, start_time=datetime.now())
        ordered = schedule.get('ordered', [])
        if not ordered:
            st.info('Nenhuma tarefa agendada')
        else:
            st.subheader('Agenda gerada (ordem de execução)')
            rows = []
            for item in ordered:
                rows.append({
                    'Tarefa': item.name,
                    'Início': item.start.strftime('%d/%m/%Y %H:%M'),
                    'Fim': item.finish.strftime('%d/%m/%Y %H:%M'),
                    'Lateness (h)': f"{item.lateness_hours:.2f}",
                    'Cliente': item.client,
                })
            st.table(pd.DataFrame(rows))


if __name__ == '__main__':
    main()
