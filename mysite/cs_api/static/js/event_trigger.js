(async function () {

'use strict';

const app = new Vue({
    el: '#event_trigger',
    data: {
        categoryList: [],
        event_servers: undefined,
        cs_users: undefined,
        formData: {
            category: undefined,
            cloudstack_user_id: undefined,
            command: undefined,
            conditions: [],
            event_server_id: undefined,
        },
    },
    methods: {
        onClickAddCondition() {
            this.formData.conditions.push({
                data_key: '',
                operator: '',
                value: '',
            });
        },
        onClickRemoveCondition(condition) {
            this.formData.conditions.splice(this.formData.conditions.indexOf(condition), 1);
        },
        onInputCategory() {
            this.formData.command = {};
        },
        onInputCommand() {
            if (!this.formData.command) {
                return;
            }
        },
        async submit() {
            const response = await fetch('/trigger_create', {
                body: JSON.stringify({
                    'form_data': {
                        'event_trigger_id': window.cs_api.event_trigger_id,
                        'event_server_id': this.formData.event_server_id.id,
                        'command_id': this.formData.command.id,
                        'cloudstack_user_id': this.formData.cloudstack_user_id.id,
                        'conditions': this.formData.conditions.map(condition => {
                            return {
                                'data_key': condition.data_key,
                                'operator': condition.operator,
                                'value': condition.value,
                            };
                        }),
                        'parameter_list': this.formData.command.parameterList.map(parameter => {
                            return {
                                'parameter_id': parameter.id,
                                'operator': parameter.operator,
                                'value': parameter.value,
                            };
                        }),
                    },
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
                },
                method: 'POST',
                mode: 'same-origin',
            });
            const responseJson = await response.json();
            window.location = '/cs_event_trigger_list';
        },
    },
});

const response = await fetch(`/get_data_for_trigger/${window.cs_api.event_trigger_id}`);
const data = await response.json();

app.event_servers = data['event_servers'];
app.cs_users = data['cs_users'];
app.categoryList = data['categoryList'];

if (data['formData']) {
    const category = app.categoryList.find(category => category.commandList.find(command => command.id == data['formData']['command_id']));
    app.formData = {
        category,
        cloudstack_user_id: app.cs_users.find(user => user.id == data['formData']['cloudstack_user_id']),
        command: category.commandList.find(command => command.id == data['formData']['command_id']),
        conditions: data['formData']['conditions'],
        event_server_id: app.event_servers.find(server => server.id == data['formData']['event_server_id']),
    };
    for (const parameter_data of data['formData']['parameterList']) {
        const parameter = app.formData.command.parameterList.find(parameter => parameter.id === parameter_data.id);
        parameter.operator = parameter_data.operator;
        parameter.value = parameter_data.value;
    }
} else {
    Object.assign(app.formData, {
        cloudstack_user_id: app.cs_users[0],
        event_server_id: app.event_servers[0],
    });
}

})();
