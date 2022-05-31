<template>
    <div class="text-h6">Begin and stop recording</div>
    <div>
        <q-btn-group outline>
            <q-btn outline size="lg" @click="record('begin')" label="Record" />
            <q-btn outline size="lg" @click="record('finish')" label="Finish" />
        </q-btn-group>
    </div>
    <div class="text-h6">
        Download :
        <q-btn size="lg" @click="download()" icon="download" />
    </div>
    <div class="text-h6">
        Upload:
        <q-uploader
            :url="this.api + 'upload'"
            label="tflite upload"
            send-raw
        />
    </div>
    <div class="text-h6">Start and stop DNN</div>
    <div>
        <q-btn-group outline>
            <q-btn outline size="lg" @click="dnn('start')" label="Start DNN" />
            <q-btn outline size="lg" @click="dnn('stop')" label="Stop DNN" />
        </q-btn-group>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'DataMenu',
    data() {
        return {
            api: 'http://' + window.location.hostname + ':8000/'
        }
    },
    methods: {
        record: function (action) {
            axios.post(this.api + 'record', { params: { action: action } })
                .then(response => this.responseData = response.data)
        },
        download: function () {
            window.open('http://' + window.location.hostname + ':8000/out-key.csv');
            window.open('http://' + window.location.hostname + ':8000/out-video.avi');
        },
        dnn: function (action) {
            axios.post(this.api + 'dnn', { params: { action: action } })
                .then(response => this.responseData = response.data)
        }
    }
}
</script>
