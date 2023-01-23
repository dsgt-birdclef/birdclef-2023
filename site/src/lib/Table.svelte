<script lang="ts">
  import { TabulatorFull as Tabulator } from "tabulator-tables";
  import "tabulator-tables/dist/css/tabulator.min.css";

  export let table = null;
  export let data: any[] = [];
  export let options = {};
  let element: HTMLElement | null = null;
  $: element &&
    data &&
    options &&
    (table = new Tabulator(element, {
      data: data,
      layout: "fitDataFill",
      ...options,
    }));
</script>

<div bind:this={element} />
