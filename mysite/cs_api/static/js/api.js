(async function () {

'use strict';

const app = new Vue({
    el: '#app',
    data: {
        categoryList: [],
        formData: {
            apiKey: '',
            category: undefined,
            command: undefined,
            parameters: {},
            secretKey: '',
            url: '',
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
            console.log(this.formData);
            const response = await fetch('/receive_api_request', {
                body: JSON.stringify({
                    'form_data': {
                        'api_key': this.formData.apiKey,
                        'command_id': this.formData.command.id,
                        'parameter_list': Object.entries(this.formData.parameters).map(([id, value]) => {
                            return {
                                'id': id,
                                'value': value,
                            };
                        }),
                        'secret_key': this.formData.secretKey,
                        'url': this.formData.url,
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
                console.log(responseJson.error);
                this.lastResponse = responseJson.error;
            } else {
                console.log(responseJson);
                this.lastResponse = responseJson;
            }
        },
    },
});

const response = await fetch('/get_category_map');
const categoryData = await response.json();
console.log(categoryData);

app.categoryList = categoryData['categoryList'];

})();
