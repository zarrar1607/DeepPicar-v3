<template>
  <div>
    <img :src="picam" />
  </div>
</template>

<script>
export default {
  name: 'CameraView',
  data: function () {
    return {
      picam: "",
    };
  },
  created() {
    this.picam = 'http://' + window.location.hostname + ':8000/stream.mjpg';
  },
};
</script>
