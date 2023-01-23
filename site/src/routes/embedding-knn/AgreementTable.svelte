<script lang="ts">
  import Table from "$lib/Table.svelte";
  export let data: any[] = [];
  $: options = {
    autoColumns: true,
    pagination: "local",
    paginationSize: 20,
    paginationCounter: "rows",
  };
</script>

{#if data.length > 0}
  <Table {data} {options} />
{/if}
