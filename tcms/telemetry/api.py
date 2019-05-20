from django.db.models import Count
from django.utils.translation import ugettext_lazy as _, override
from modernrpc.core import rpc_method

from tcms.testcases.models import TestCase, TestCaseStatus
from tcms.testplans.models import TestPlan
from tcms.testruns.models import TestRun, TestExecution, TestExecutionStatus


@rpc_method(name='Testing.breakdown')
def breakdown(query=None):
    """
    .. function:: XML-RPC Testing.breakdown(query)

        Perform a search and return the statistics for the selected test cases

        :param query: Field lookups for :class:`tcms.testcases.models.TestCase`
        :type query: dict
        :return: Object, containing the statistics for the selected test cases
        :rtype: dict
    """

    if query is None:
        query = {}

    test_cases = TestCase.objects.filter(**query).filter()

    manual_count = test_cases.filter(is_automated=False).count()
    automated_count = test_cases.filter(is_automated=True).count()
    count = {
        'manual': manual_count,
        'automated': automated_count,
        'all': manual_count + automated_count
    }

    priorities = _get_field_count_map(test_cases, 'priority', 'priority__value')
    categories = _get_field_count_map(test_cases, 'category', 'category__name')

    return {
        'count': count,
        'priorities': priorities,
        'categories': categories,
    }


def _get_field_count_map(test_cases, expression, field):
    confirmed = TestCaseStatus.get_confirmed()

    query_set_confirmed = test_cases.filter(
        case_status=confirmed
    ).values(field).annotate(
        count=Count(expression)
    )
    query_set_not_confirmed = test_cases.exclude(
        case_status=confirmed
    ).values(field).annotate(
        count=Count(expression)
    )
    return {
        confirmed.name: _map_query_set(query_set_confirmed, field),
        str(_('OTHER')): _map_query_set(query_set_not_confirmed, field)
    }


def _map_query_set(query_set, field):
    return {entry[field]: entry['count'] for entry in query_set}


@rpc_method(name='Testing.status_matrix')
def status_matrix(query=None):
    """
        .. function:: XML-RPC Testing.status_matrix(query)

            Perform a search and return data_set needed to visualize the status matrix
            of test plans, test cases and test executions

            :param query: Field lookups for :class:`tcms.testcases.models.TestPlan`
            :type query: dict
            :return: List, containing the information about the test executions
            :rtype: list
        """

    if query is None:
        query = {}

    test_plans = TestPlan.objects.filter(**query)

    test_runs = TestRun.objects.filter(plan__in=test_plans)
    test_executions = TestExecution.objects.filter(run__in=test_runs)

    data_set = []
    for test_case in TestCase.to_xmlrpc({'case_run__in': test_executions}, distinct=True):
        data_set_entry = {'case': test_case}

        for test_run in test_runs:
            test_executions = TestExecution.to_xmlrpc({
                'run_id': test_run.run_id,
                'case_id': test_case['case_id']
            })
            if test_executions:
                test_execution = test_executions[0]
                with override('en'):
                    if test_execution['status'] in TestExecutionStatus.failure_status_names:
                        test_execution['color'] = 'red'
                    elif test_execution['status'] == TestExecutionStatus.PASSED:
                        test_execution['color'] = 'green'
                key = 'run-{}'.format(test_run.run_id)
                data_set_entry[key] = test_execution

        data_set.append(data_set_entry)

    return data_set
