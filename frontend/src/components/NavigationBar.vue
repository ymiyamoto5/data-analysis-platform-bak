<template>
  <div id="navigation-bar">
    <v-app-bar
      color="#6A76AB"
      dark
      flat
    >

      <template v-slot:img="{ props }">
        <v-img
          v-bind="props"
          gradient="to top right, rgba(100,115,201,.7), rgba(25,32,72,.7)"
        ></v-img>
      </template>

      <v-toolbar-title>非稼働分析ソリューション</v-toolbar-title>

      <template v-slot:extension>
        <v-tabs align-with-title>
          <v-tab :to="'/'">Home</v-tab>
          <v-tab :to="'Analysis'">分析</v-tab>
          <v-tab :to="'Report'">レポート</v-tab>
        </v-tabs>
      </template>
      
    </v-app-bar>
  </div>
</template>