<template>
  <div>
    <q-layout view="hhh lpr fff" class="rounded-borders">
      <q-header elevated class="flex-center">
        <q-toolbar>
        <q-toolbar-title><div class="text-h4">LEAPES: DeepPicar</div></q-toolbar-title>
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page class="q-my-md home-page flex-center">
          <HomeView />
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
</template>

<script>
import HomeView from './views/HomeView.vue'

export default {
  name: 'app',

  components: {
    HomeView
  },

}
</script>
