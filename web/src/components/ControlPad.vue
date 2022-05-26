<template>
  <div class="text-h6">Use the buttons below to control the DeepPicar</div>
  <div class="row">
    <div class="column">
      <q-btn round color="primary" size="lg" @click="actuate('forward')" icon="north" />
      <q-btn round color="primary" size="lg" @click="actuate('stop')" icon="front_hand" />
      <q-btn round color="primary" size="lg" @click="actuate('reverse')" icon="south" />
    </div>
    <div class="flex-break"></div>
    <div class="q-pa-md q-gutter-sm row items-center justify-evenly">
      <q-btn round color="primary" size="lg" @click="actuate('left')" icon="arrow_left" />
      <q-btn round color="primary" size="lg" @click="actuate('center')" icon="adjust" />
      <q-btn round color="primary" size="lg" @click="actuate('right')" icon="arrow_right" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ControlPad',
  methods: {
    actuate: function (direction) {
      axios.post('http://' + window.location.hostname + ':8000/actuate', { params: { direction: direction } })
        .then(response => this.responseData = response.data)
    }
  }
}
</script>
