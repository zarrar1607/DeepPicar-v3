<template>
  <div class="column flex-center">
    <CameraView />
     <q-separator />
    <ControlPad />
     <q-separator />
    <DataMenu />
  </div>
</template>

<script>
// @ is an alias to /src
import CameraView from '@/components/CameraView.vue'
import ControlPad from '@/components/ControlPad.vue'
import DataMenu from '@/components/DataMenu.vue'


export default {
  name: 'HomeView',
  components: {
    CameraView,
    ControlPad,
    DataMenu
  },
  
}
</script>
