"""Scheduler simples para ordenar tarefas por prazo e calcular lateness.

Este módulo contém:
    prioridade e cliente).

Observação: `duration_hours` deve ser um float representando horas.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any


@dataclass
class Task:
    """Dados de uma tarefa a ser agendada.

    Campos: id, name, duration_hours, deadline, priority, client.
    """
    id: int
    name: str
    duration_hours: float
    deadline: datetime
    priority: str = "média"
    client: str = ""


def schedule_minimize_lateness(tasks: List[Task], start_time: datetime) -> Dict[str, Any]:
    """
    Ordena tarefas por prazo (earliest deadline first) e calcula horários de fim e lateness.

    Retorna dicionário com: ordered (lista com campos start/finish/lateness), total_lateness_hours e max_lateness_hours.
    """
    # ordenar por deadline
    ordered = sorted(tasks, key=lambda t: t.deadline)

    current = start_time
    results = []
    total_lateness = 0.0
    max_lateness = timedelta(0)

    for t in ordered:
        finish = current + timedelta(hours=t.duration_hours)
        lateness_td = max(timedelta(0), finish - t.deadline)
        lateness_hours = lateness_td.total_seconds() / 3600.0
        results.append({
            'task': t,
            'start': current,
            'finish': finish,
            'lateness_hours': lateness_hours,
        })
        total_lateness += lateness_hours
        if lateness_td > max_lateness:
            max_lateness = lateness_td

        current = finish

    return {
        'ordered': results,
        'total_lateness_hours': total_lateness,
        'max_lateness_hours': max_lateness.total_seconds() / 3600.0,
    }


def _parse_example_tasks() -> List[Task]:
    """Gera um conjunto de tarefas de exemplo usado no autoteste do módulo."""
    return [
        Task(1, 'Petição Inicial', 4, datetime(2025, 10, 20, 17, 0), 'alta'),
        Task(2, 'Audiência', 2, datetime(2025, 10, 19, 10, 0), 'alta'),
        Task(3, 'Contestação', 3, datetime(2025, 10, 21, 12, 0), 'média'),
    ]


if __name__ == '__main__':
    # Execução rápida para depuração/local: imprime o cronograma calculado
    tasks = _parse_example_tasks()
    start = datetime(2025, 10, 19, 8, 0)
    out = schedule_minimize_lateness(tasks, start)
    print('Schedule starting at', start)
    for r in out['ordered']:
        t = r['task']
        print(f"{t.name}: {r['start']} -> {r['finish']} (lateness {r['lateness_hours']:.2f} h)")
    print('Total lateness (h):', out['total_lateness_hours'])
    print('Max lateness (h):', out['max_lateness_hours'])
