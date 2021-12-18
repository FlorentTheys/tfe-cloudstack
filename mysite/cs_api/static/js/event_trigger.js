(async function () {

'use strict';

const app = new Vue({
    el: '#event_trigger',
    data: {
        event_servers: undefined,
        cs_users: undefined,
        formData: {
            event_server_id: undefined,
            cloudstack_user_id: undefined,
            conditions: [],
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
        async submit() {
            const response = await fetch('/trigger_create', {
                body: JSON.stringify({
                    'form_data': {
                        'event_server_id': this.formData.event_server_id.id,
                        'cloudstack_user_id': this.formData.cloudstack_user_id.id,
                        'conditions': this.formData.conditions.map(condition => {
                            return {
                                'data_key': condition.data_key,
                                'operator': condition.operator,
                                'value': condition.value,
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

const response = await fetch('/get_data_for_trigger');
const data = await response.json();

app.event_servers = data['event_servers'];
app.cs_users = data['cs_users'];

app.formData.event_server_id = app.event_servers[0];
app.formData.cloudstack_user_id = app.cs_users[0];

})();
