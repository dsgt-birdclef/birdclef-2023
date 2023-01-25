<script lang="ts">
  import Table from "$lib/Table.svelte";

  export let data: any[] = [];

  $: options = {
    autoColumns: true,
    pagination: "local",
    paginationSize: 5,
    paginationCounter: "rows",
    autoColumnsDefinitions: [
      {
        field: "ego_primary_label",
        title: "species",
      },
      {
        field: "n_ego_birdnet_label_matches",
        title: "ego count",
      },
      {
        field: "n_knn_birdnet_label_matches",
        title: "knn count",
      },
      {
        field: "pct_ego_birdnet_label_matches",
        title: "ego percent",
      },
      {
        field: "pct_knn_birdnet_label_matches",
        title: "knn percent",
      },
    ],
  };
</script>

{#if data.length > 0}
  <Table {data} {options} />
{/if}
