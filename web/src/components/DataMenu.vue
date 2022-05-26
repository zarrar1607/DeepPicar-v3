<template>
    <div class="text-h6">Begin and stop recording</div>
    <div>
        <q-btn-group outline>
            <q-btn outline size="lg" @click="record('begin')" label="Record" />
            <q-btn outline size="lg" @click="record('finish')" label="Finish" />
        </q-btn-group>
    </div>
    <div class="text-h6">Download : <q-btn size="lg" @click="download()" icon="download" /></div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'DataMenu',
    methods: {
        record: function (action) {
            axios.post('http://' + window.location.hostname + ':8000/record', { params: { action: action } })
                .then(response => this.responseData = response.data)
        },
        download: function () {
            window.open('http://' + window.location.hostname + ':8000/out-key.csv');
            window.open('http://' + window.location.hostname + ':8000/out-video.avi');
        }
    }
}
</script>
