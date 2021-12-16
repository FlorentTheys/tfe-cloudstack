(async function () {

'use strict';

const app = new Vue({
    el: '#app',
    data: {
        categoryList: [],
        cloudstackUsers: [],
        formData: {
            category: undefined,
            command: undefined,
            csUser: undefined,
            parameters: {},
        },
        lastResponse: undefined,
    },
    methods: {
        onInputCategory() {
            this.formData.command = {};
            this.formData.parameters = {};
        },
        onInputCommand() {
            this.formData.parameters = {};
        },
        async submit() {
            const response = await fetch('/receive_api_request', {
                body: JSON.stringify({
                    'form_data': {
                        'command_id': this.formData.command.id,
                        'cs_user_id': this.formData.csUser.id,
                        'parameter_list': Object.entries(this.formData.parameters).map(([id, value]) => {
                            return {
                                'id': id,
                                'value': value,
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
            if (responseJson.error) {
                this.lastResponse = responseJson.error;
            } else {
                this.lastResponse = responseJson;
            }
            this.lastResponse = JSON.stringify(this.lastResponse, null, 4);
        },
    },
});

const response = await fetch('/get_category_map');
const data = await response.json();

app.categoryList = data['categoryList'];
app.cloudstackUsers = data['cloudstackUsers'];
app.formData.csUser = app.cloudstackUsers[0];

})();
