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
      <q-btn round color="primary" size="lg" @mousedown="actuate('left')" @touchstart="actuate('left')" @mouseup="actuate('center')" @touchend="actuate('center')" icon="arrow_left" />
      <q-btn round color="primary" size="lg" @mousedown="actuate('right')" @touchstart="actuate('right')" @mouseup="actuate('center')" @touchend="actuate('center')" icon="arrow_right" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ControlPad',
  created: function () {
    window.addEventListener('keydown', this.keydown);
    window.addEventListener('keyup'. this.keyup)
  },
  methods: {
    actuate: function (direction) {
      axios.post('http://' + window.location.hostname + ':8000/actuate', { params: { direction: direction } })
        .then(response => this.responseData = response.data)
    },
    keydown: function(k) {
      if (k == 'ArrowUp'){
        this.actuate('forward')
      }
      if (k == 'ArrowLeft'){
        this.actuate('left')
      }
      if (k == 'ArrowRight'){
        this.actuate('right')
      }
      if (k == 'ArrowDown'){
        this.actuate('reverse')
      }
      if (k == 'Space'){
        this.actuate('stop')
      }
    },
    keyup: function(k) {
      if (k == 'ArrowLeft' || k == 'ArrowRight') {
        this.actuate('center')
      }
    }
  }
}
</script>
