import json
import os

from .utils.parser import Problem


def getActionDetails(task, plan, output):
    actions = []
    act_map = {}

    for a in task.actions:
        act_map[a.name] = a

    for act_line in plan:
        while ' )' == act_line[-2:]:
            act_line = act_line[:-2] + ')'
        a_name = act_line[1:-1].split(' ')[0]
        if len(act_line.split(' ')) > 1:
            a_params = act_line[1:-1].split(' ')[1:]
        else:
            a_params = False

        a = act_map[a_name]
        actions.append({'name': act_line, 'action': a.export(grounding=a_params)})

    return json.dumps({'parse_status': 'ok',
                       'type': 'full',
                       'length': len(plan),
                       'plan': actions,
                       'output': output}, indent=4)


def getSimplePlan(plan, err_msg, output):
    return json.dumps({'parse_status': 'ok',
                       'type': 'simple',
                       'length': len(plan),
                       'plan': plan,
                       'error': err_msg,
                       'output': output}, indent=4)


def process_solution(domain, problem, solution, solver_output):
    try:
        task = Problem(domain, problem)
    except Exception as e:
        return json.dumps({'parse_status': 'err', 'output': solver_output,
                           'error': "Failed to parse the problem -- %s\n\n%s" % (str(e), solver_output)})

    try:

        if not os.path.isfile(solution):
            return json.dumps({'parse_status': 'err', 'output': solver_output,
                               'error': "Solver failed.\n\n%s" % solver_output})

        file = open(solution, 'r')
        plan = list(map(lambda x: x.strip().lower(), file.readlines()))
        file.close()

        if (len(plan) == 0) or (len(plan) == 1 and plan[0] == ''):
            err_str = "Suspected timeout.\n\n%s" % solver_output
            return json.dumps({'parse_status': 'err', 'output': solver_output, 'error': err_str})

        if '' == plan[-1]:
            plan = plan[:-1]

    except Exception as e:
        return json.dumps({'parse_status': 'err', 'output': solver_output,
                           'error': "Failed to parse plan -- %s\n\n%s" % (str(e), solver_output)})

    try:
        return getActionDetails(task, plan, solver_output)
    except Exception as e:
        return getSimplePlan(plan, str(e), solver_output)

