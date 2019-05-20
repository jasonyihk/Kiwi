let table;

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
    const query = {};

    const productId = $('#id_product').val();
    if (productId) {
        query['plan__product_id'] = productId;
    }

    const versionId = $('#id_version').val();
    if (versionId) {
        query['product_version_id'] = versionId;
    }

    const buildId = $('#id_build').val();
    if (buildId) {
        query['build__build_id'] = buildId;
    }

    const testPlanId = $('#id_test_plan').val();
    if (testPlanId) {
        query['plan__plan_id'] = testPlanId;
    }

    const dateBefore = $('#id_before');
    if (dateBefore.val()) {
        query['plan__create_date__lte'] = dateBefore.data('DateTimePicker').date().format('YYYY-MM-DD 23:59:59');
    }

    const dateAfter = $('#id_after');
    if (dateAfter.val()) {
        query['plan__create_date__gte'] = dateAfter.data('DateTimePicker').date().format('YYYY-MM-DD 00:00:00');
    }

    jsonRPC('TestRun.filter', query, data => {

        if (table) {
            table.destroy();

            d3.selectAll('table > thead > tr > th:not(.header)').remove();
            d3.selectAll('table > tbody > tr').remove();
        }

        const columns = [
            {
                data: "case",
                className: "table-view-pf-actions",
                render: data => {
                    const caseId = data.case_id;

                    return `<span style="padding: 5px;">`
                        + `<a href="${window.location.origin}/case/${caseId}">TC-${caseId}</a>: ${data.summary}` +
                        `</span>`;
                },
                sortable: false
            },
        ];

        data.forEach(testRun => {
            d3.select('.table > thead > tr').append('th').text(testRun.summary);

            columns.push({
                data: `run-${testRun.run_id}`,
                sortable: false,
                render: data => {
                    if (!data) {
                        return '';
                    }
                    return `<span class="${data.color}">`
                        + `<a href='${window.location.origin}/runs/${data.run_id}/#caserun_${data.case_run_id}'> TE-${data.case_run_id} </a>`
                        + '</span>';
                }
            });
        });

        table = $('#table').DataTable({
            ajax: (data, callback) => {
                const query = {};

                const productId = $('#id_product').val();
                if (productId) {
                    query['product_id'] = productId;
                }

                const versionId = $('#id_version').val();
                if (versionId) {
                    query['product_version_id'] = versionId;
                }

                const buildId = $('#id_build').val();
                if (buildId) {
                    query['run__build'] = buildId;
                }

                const testPlanId = $('#id_test_plan').val();
                if (testPlanId) {
                    query['plan_id'] = testPlanId;
                }

                const dateBefore = $('#id_before');
                if (dateBefore.val()) {
                    query['create_date__lte'] = dateBefore.data('DateTimePicker').date().format('YYYY-MM-DD 23:59:59');
                }

                const dateAfter = $('#id_after');
                if (dateAfter.val()) {
                    query['create_date__gte'] = dateAfter.data('DateTimePicker').date().format('YYYY-MM-DD 00:00:00');
                }

                const initCallback = data => {
                    callback(data);

                    table.cells()
                        .nodes()
                        .each(node => {
                            if (node.firstChild &&
                                node.firstChild.classList &&
                                node.firstChild.classList.length > 0) {

                                node.classList.add(node.firstChild.classList);
                            }
                        });
                };

                dataTableJsonRPC('Testing.status_matrix', query, initCallback);
            },
            columns: columns,
            paging: false,
            dom: "t"
        });
    });
}
