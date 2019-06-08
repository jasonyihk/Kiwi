let table;
const table_columns = [
    {
        data: null,
        className: "table-view-pf-actions",
        render: function (data, type, full, meta) {
            const caseId = data.tc_id;

            return `<span style="padding: 5px;">` +
                   `<a href="/case/${caseId}">TC-${caseId}: ${data.tc_summary}</a>` +
                   `</span>`;
        },
        sortable: false
    },
];

function pre_process_data(data) {
    const _test_runs = []

    data.forEach(function(element) {
        element.runs.forEach(function(test_run) {
            _test_runs[test_run.run_id] = test_run.run__summary;
        });
    });

    _test_runs.forEach(function(element) {
// doesn't quite work, see:
// we need to first fetch the data, figure out column names
// and then pass all of the options to DataTables for rendering
// https://datatables.net/forums/discussion/33886/dynamic-columns-from-ajax-data-source#Comment_90684
        table_columns.push({
            data: null,
            title: element,
            sortable: false,
            render: function (data, type, full, meta) {
                return 'TE';
            }
        })
    });
}

$(document).ready(() => {
    loadInitialProduct();
    loadInitialTestPlans();

    document.getElementById('id_product').onchange = () => {
        update_version_select_from_product();
        update_build_select_from_product(true);
        updateTestPlanSelectFromProduct();

        drawTable();
    };

    document.getElementById('id_version').onchange = drawTable;
    document.getElementById('id_build').onchange = drawTable;
    document.getElementById('id_test_plan').onchange = drawTable;

    $('#id_after').on('dp.change', drawTable);
    $('#id_before').on('dp.change', drawTable);

    drawTable();
});


function drawTable() {
    if (table) {
        table.destroy();
    }

    table = $('#table').DataTable({
        ajax: (data, callback) => {
            const query = {};

            const productId = $('#id_product').val();
            if (productId) {
                query['product_version__product_id'] = productId;
            }

            const versionId = $('#id_version').val();
            if (versionId) {
                query['product_version_id'] = versionId;
            }

            const buildId = $('#id_build').val();
            if (buildId) {
                query['build_id'] = buildId;
            }

            const testPlanId = $('#id_test_plan').val();
            if (testPlanId) {
                query['plan_id'] = testPlanId;
            }

            const dateBefore = $('#id_before');
            if (dateBefore.val()) {
                query['stop_date__lte'] = dateBefore.data('DateTimePicker').date().format('YYYY-MM-DD 23:59:59');
            }

            const dateAfter = $('#id_after');
            if (dateAfter.val()) {
                query['start_date__gte'] = dateAfter.data('DateTimePicker').date().format('YYYY-MM-DD 00:00:00');
            }

            dataTableJsonRPC('Testing.status_matrix', query, callback, pre_process_data);
console.log('columns=', table_columns);
        },
        columns: table_columns,
        paging: false,
        dom: "t"
    });
}