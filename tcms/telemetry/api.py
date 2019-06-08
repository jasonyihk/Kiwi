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
    print('+++++ inside status_matrix')
    if query is None:
        query = {}

    data_set = []
    row = {'tc_id': 0}
    for test_execution in TestExecution.objects.filter(**query).values(
            'pk', 'status__name',
            'run_id', 'run__summary',
            'case_id', 'case__summary').order_by('case_id', 'run_id'):
        if test_execution['case_id'] == row['tc_id']:
            row['runs'].append(test_execution)
        else:
            data_set.append(row)

            row = {
                'tc_id': test_execution['case_id'],
                'tc_summary': test_execution['case__summary'],
                'runs': [test_execution],
            }

    # first row is special so remove it
    del data_set[0]

    from pprint import pprint
    print("**** data_set =")
    pprint(data_set)
    return data_set
